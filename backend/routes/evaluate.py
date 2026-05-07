from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
import json

from database import get_db
from models import Tender, VendorSubmission, Criteria, EvaluationResult, FraudFlag, AuditLog, User
from routes.auth import get_current_user
from services.ocr_service import OCRService
from services.llm_service import LLMService
from services.evaluator import EvaluationEngine
from services.fraud_detector import FraudDetector

router = APIRouter()

class OverrideRequest(BaseModel):
    result_id: int
    officer_override: str # PASS or FAIL
    officer_notes: str

@router.post("/run")
def run_evaluation(tender_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can run evaluations")

    tender = db.query(Tender).filter(Tender.id == tender_id).first()
    if not tender:
        raise HTTPException(status_code=404, detail="Tender not found")

    criteria = db.query(Criteria).filter(Criteria.tender_id == tender_id).all()
    submissions = db.query(VendorSubmission).filter(VendorSubmission.tender_id == tender_id).all()

    if not submissions:
        return {"message": "No submissions found for this tender", "results": []}

    all_vendor_results = []
    
    # Clean up previous evaluations for this tender
    # (Optional: depends on if we want to keep history or re-run fresh)
    # db.query(EvaluationResult).filter(EvaluationResult.submission_id.in_([s.id for s in submissions])).delete(synchronize_session=False)
    # db.query(FraudFlag).filter(FraudFlag.tender_id == tender_id).delete()

    for sub in submissions:
        vendor = db.query(User).filter(User.id == sub.vendor_id).first()
        files = json.loads(sub.files_json)
        
        # Combine text from all submitted files
        full_vendor_text = ""
        for file_info in files:
            path = file_info.get("path")
            ext = path.split(".")[-1] if "." in path else ""
            if path:
                ocr_result = OCRService.extract_text_from_file(path, ext)
                full_vendor_text += ocr_result.get("text", "") + "\n"

        # Extract evidence using LLM
        evidence = LLMService.extract_vendor_evidence(full_vendor_text, [
            {
                "id": c.id,
                "title": c.title,
                "type": c.type,
                "mandatory": c.mandatory,
                "requirement": c.requirement,
                "comparison": c.comparison,
                "threshold_value": c.threshold_value
            } for c in criteria
        ])

        # Evaluate using EvaluationEngine
        evaluation = EvaluationEngine.evaluate_vendor(vendor.name, vendor.id, evidence, criteria)
        all_vendor_results.append(evaluation)

        # Store results in DB
        for cr in evaluation["criteria_results"]:
            db_res = db.query(EvaluationResult).filter(
                EvaluationResult.submission_id == sub.id,
                EvaluationResult.criteria_id == cr["criteria_id"]
            ).first()
            
            if not db_res:
                db_res = EvaluationResult(submission_id=sub.id, criteria_id=cr["criteria_id"])
                db.add(db_res)
            
            db_res.verdict = cr["verdict"]
            db_res.confidence = cr["confidence"]
            db_res.explanation = cr["explanation"]
            db_res.source_snippet = cr["source_snippet"]
            db_res.required_value = cr["required"]
            db_res.found_value = cr["found"]
            db_res.fail_warning = cr["fail_warning"]
        
        sub.status = evaluation["overall_verdict"]
        
        # Log to AuditLog
        audit = AuditLog(
            action_type="VENDOR_EVALUATION",
            user_id=current_user.id,
            tender_id=tender_id,
            input_summary=f"Evaluated vendor {vendor.name}",
            output_summary=f"Verdict: {evaluation['overall_verdict']}",
            model_version="claude-sonnet-4-20250514"
        )
        db.add(audit)

    # Fraud Detection
    fraud_flags = FraudDetector.detect_patterns(all_vendor_results, submissions)
    for flag in fraud_flags:
        db_flag = FraudFlag(
            tender_id=tender_id,
            flag_type=flag["flag_type"],
            vendor_ids_json=json.dumps(flag["vendor_ids"]),
            message=flag["message"],
            severity=flag["severity"]
        )
        db.add(db_flag)

    db.commit()
    return {
        "tender_id": tender_id,
        "results": all_vendor_results,
        "fraud_flags": fraud_flags
    }

@router.post("/override")
def override_result(req: OverrideRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can override results")

    result = db.query(EvaluationResult).filter(EvaluationResult.id == req.result_id).first()
    if not result:
        raise HTTPException(status_code=404, detail="Evaluation result not found")

    result.officer_override = req.officer_override
    result.officer_notes = req.officer_notes
    
    # Update submission status if needed
    submission = db.query(VendorSubmission).filter(VendorSubmission.id == result.submission_id).first()
    # Logic to re-calculate overall status based on override could go here
    
    audit = AuditLog(
        action_type="OFFICER_OVERRIDE",
        user_id=current_user.id,
        tender_id=submission.tender_id,
        input_summary=f"Override result_id {result.id} to {req.officer_override}",
        output_summary=f"Notes: {req.officer_notes}"
    )
    db.add(audit)
    db.commit()
    
    return {"message": "Override recorded successfully"}

@router.get("/session/{tender_id}")
def get_evaluation_session(tender_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    tender = db.query(Tender).filter(Tender.id == tender_id).first()
    if not tender:
        raise HTTPException(status_code=404, detail="Tender not found")

    submissions = db.query(VendorSubmission).filter(VendorSubmission.tender_id == tender_id).all()
    fraud_flags = db.query(FraudFlag).filter(FraudFlag.tender_id == tender_id).all()
    
    results = []
    for sub in submissions:
        vendor = db.query(User).filter(User.id == sub.vendor_id).first()
        sub_results = db.query(EvaluationResult).filter(EvaluationResult.submission_id == sub.id).all()
        
        results.append({
            "vendor_id": vendor.id,
            "vendor_name": vendor.name,
            "overall_verdict": sub.status,
            "criteria_results": [
                {
                    "id": r.id,
                    "criteria_id": r.criteria_id,
                    "verdict": r.verdict,
                    "required": r.required_value,
                    "found": r.found_value,
                    "confidence": r.confidence,
                    "explanation": r.explanation,
                    "fail_warning": r.fail_warning,
                    "officer_override": r.officer_override,
                    "officer_notes": r.officer_notes
                } for r in sub_results
            ]
        })

    return {
        "tender_id": tender_id,
        "tender_title": tender.title,
        "results": results,
        "fraud_flags": [
            {
                "flag_type": f.flag_type,
                "vendor_ids": json.loads(f.vendor_ids_json),
                "message": f.message,
                "severity": f.severity
            } for f in fraud_flags
        ]
    }
