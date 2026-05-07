from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List
import json

from database import get_db
from models import User, Tender, VendorSubmission, Criteria
from routes.auth import get_current_user
from utils.file_handler import save_tender_file, save_vendor_submission_files, get_extension
from services.ocr_service import OCRService
from services.llm_service import LLMService

router = APIRouter()

@router.post("/upload")
def upload_tender(
    title: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only administrators can upload tenders")
        
    new_tender = Tender(title=title, uploaded_by=current_user.id)
    db.add(new_tender)
    db.commit()
    db.refresh(new_tender)
    
    try:
        file_path = save_tender_file(str(new_tender.id), file)
        new_tender.file_path = file_path
        db.commit()
    except Exception as e:
        db.delete(new_tender)
        db.commit()
        raise HTTPException(status_code=400, detail=str(e))
        
    file_type = get_extension(file.filename)
    ocr_result = OCRService.extract_text_from_file(file_path, file_type)
    
    return {
        "tender_id": new_tender.id,
        "message": "Tender uploaded successfully",
        "text_preview": ocr_result["text"][:200] + "..." if ocr_result["text"] else "",
        "confidence": ocr_result["confidence"],
        "warnings": ocr_result["warnings"]
    }

@router.post("/vendor/submit-documents")
def vendor_submit_documents(
    tender_id: int = Form(...),
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "vendor":
        raise HTTPException(status_code=403, detail="Only vendors can submit documents")
        
    tender = db.query(Tender).filter(Tender.id == tender_id).first()
    if not tender:
        raise HTTPException(status_code=404, detail="Tender not found")
        
    new_submission = VendorSubmission(
        tender_id=tender_id,
        vendor_id=current_user.id,
        status="processing"
    )
    db.add(new_submission)
    db.commit()
    db.refresh(new_submission)
    
    try:
        file_paths = save_vendor_submission_files(str(new_submission.id), files)
        
        extraction_results = []
        for file_obj, path in zip(files, file_paths):
            file_type = get_extension(file_obj.filename)
            ocr_result = OCRService.extract_text_from_file(path, file_type)
            
            extraction_results.append({
                "filename": file_obj.filename,
                "path": path,
                "confidence": ocr_result["confidence"],
                "method": ocr_result["method"],
                "warnings": ocr_result["warnings"]
            })
            
        new_submission.files_json = json.dumps(extraction_results)
        new_submission.status = "submitted"
        db.commit()
        
        return {
            "submission_id": new_submission.id,
            "message": "Documents submitted successfully",
            "extraction_results": extraction_results
        }
    except Exception as e:
        db.delete(new_submission)
        db.commit()
        raise HTTPException(status_code=500, detail=f"Submission failed: {str(e)}")

@router.post("/{tender_id}/extract-criteria")
def extract_tender_criteria(
    tender_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only administrators can extract criteria")
        
    tender = db.query(Tender).filter(Tender.id == tender_id).first()
    if not tender:
        raise HTTPException(status_code=404, detail="Tender not found")
        
    file_type = get_extension(tender.file_path)
    ocr_result = OCRService.extract_text_from_file(tender.file_path, file_type)
    tender_text = ocr_result.get("text", "")
    
    if not tender_text:
        raise HTTPException(status_code=400, detail="Could not extract text from tender document")

    extraction_result = LLMService.extract_tender_criteria(tender_text)
    
    # Delete existing criteria for this tender if any
    db.query(Criteria).filter(Criteria.tender_id == tender_id).delete()
    
    for crit in extraction_result.get("criteria", []):
        new_crit = Criteria(
            tender_id=tender.id,
            code=crit.get("id"),
            title=crit.get("title"),
            type=crit.get("type"),
            mandatory=crit.get("mandatory", True),
            requirement=crit.get("requirement"),
            threshold_value=crit.get("threshold_value"),
            threshold_unit=crit.get("threshold_unit"),
            comparison=crit.get("comparison")
        )
        db.add(new_crit)
    
    db.commit()
    
    criteria_list = extraction_result.get("criteria", [])
    summary_doc = LLMService.generate_summary_document(tender_text, criteria_list)
    
    tender.summary_json = json.dumps(summary_doc)
    db.commit()
    
    return {
        "criteria": extraction_result,
        "summary": summary_doc
    }

@router.get("/{tender_id}/summary")
def get_tender_summary(
    tender_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    tender = db.query(Tender).filter(Tender.id == tender_id).first()
    if not tender:
        raise HTTPException(status_code=404, detail="Tender not found")
        
    if not tender.summary_json:
        raise HTTPException(status_code=404, detail="Summary not available for this tender")
        
    return json.loads(tender.summary_json)
