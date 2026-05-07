import sys
import json
from fastapi.testclient import TestClient
from unittest.mock import patch

from main import app
from database import SessionLocal
from models import User, Tender, Criteria, VendorSubmission, EvaluationResult, FraudFlag
from routes.auth import create_access_token

client = TestClient(app)

print("==========================================")
print("   Phase 5: Evaluation & Fraud Detection  ")
print("==========================================")

db = SessionLocal()

# 1. Setup Admin
from utils.security import get_password_hash
admin_user = db.query(User).filter(User.email == "admin@nividaai.gov.in").first()
if not admin_user:
    admin_user = User(
        email="admin@nividaai.gov.in",
        password_hash=get_password_hash("admin123"),
        role="admin",
        name="Super Admin"
    )
    db.add(admin_user)
    db.commit()
    db.refresh(admin_user)

access_token = create_access_token(data={"sub": admin_user.email, "role": admin_user.role})
headers = {"Authorization": f"Bearer {access_token}"}

# 2. Setup Test Tender and Criteria
test_tender = Tender(title="Phase 5 Collusion Test", uploaded_by=admin_user.id)
db.add(test_tender)
db.commit()
db.refresh(test_tender)

crit1 = Criteria(
    tender_id=test_tender.id,
    code="C1",
    title="Minimum Annual Turnover",
    type="Financial",
    mandatory=True,
    requirement="Annual turnover must be at least Rs 10 Crore",
    threshold_value=10.0,
    comparison="gte"
)
db.add(crit1)
db.commit()

# 3. Setup Test Vendors and Submissions
# We'll create 3 vendors with identical turnover to trigger fraud detection
vendors = []
for i in range(3):
    email = f"collusion_vendor_{i}@test.com"
    v = db.query(User).filter(User.email == email).first()
    if not v:
        v = User(email=email, password_hash="hash", role="vendor", name=f"Collusion Co {i}")
        db.add(v)
    vendors.append(v)
db.commit()

submissions = []
for v in vendors:
    s = VendorSubmission(
        tender_id=test_tender.id,
        vendor_id=v.id,
        files_json=json.dumps([{"name": f"doc_{v.id}.pdf", "path": f"mock_path_{v.id}.pdf"}])
    )
    db.add(s)
    submissions.append(s)
db.commit()

print(f"[1] Created Tender ID {test_tender.id} with 3 vendors for collusion test.")

# 4. Mocking Services for /api/evaluate/run
print("\n[2] Running Evaluation with Mocked OCR and LLM...")

# Mocking OCR to return text for each file
with patch("routes.evaluate.OCRService.extract_text_from_file") as mock_ocr:
    mock_ocr.return_value = {"text": "Our turnover is exactly 12.5 Crore."}
    
    # Mocking LLM to return identical evidence for all 3 vendors
    with patch("routes.evaluate.LLMService.extract_vendor_evidence") as mock_evidence:
        mock_evidence.return_value = {
            "vendor_name": "Mocked Vendor",
            "extracted_values": [
                {
                    "criteria_id": crit1.id,
                    "found": True,
                    "extracted_value": "12.5 Crore",
                    "numeric_value": 12.5,
                    "unit": "Crore INR",
                    "source_snippet": "turnover is 12.5 Crore",
                    "confidence": 0.95
                }
            ]
        }
        
        with patch("routes.evaluate.LLMService.generate_explanation") as mock_exp:
            mock_exp.return_value = "The vendor meets the financial requirement with a turnover of 12.5 Crore."
            
            response = client.post(f"/api/evaluate/run?tender_id={test_tender.id}", headers=headers)
            print(f"Status Code: {response.status_code}")
            if response.status_code == 200:
                res_json = response.json()
                print("\nFraud Flags Detected:")
                print(json.dumps(res_json.get("fraud_flags", []), indent=2))
            else:
                print(response.text)

# 5. Verify Results in DB
print("\n[3] Verifying Database State...")
saved_results = db.query(EvaluationResult).join(VendorSubmission).filter(VendorSubmission.tender_id == test_tender.id).all()
print(f"Total evaluation results stored: {len(saved_results)}")

saved_flags = db.query(FraudFlag).filter(FraudFlag.tender_id == test_tender.id).all()
print(f"Total fraud flags stored: {len(saved_flags)}")
for f in saved_flags:
    print(f" - {f.flag_type}: {f.message}")

# 6. Test Override
if saved_results:
    res_id = saved_results[0].id
    print(f"\n[4] Testing Officer Override for result_id {res_id}...")
    override_data = {
        "result_id": res_id,
        "officer_override": "FAIL",
        "officer_notes": "Manual verification showed document was forged."
    }
    ov_res = client.post("/api/evaluate/override", json=override_data, headers=headers)
    print(f"Status Code: {ov_res.status_code}")
    
    # Check if override recorded
    db.refresh(saved_results[0])
    print(f"New Override Status: {saved_results[0].officer_override}")
    print(f"Officer Notes: {saved_results[0].officer_notes}")

# Cleanup
print("\n[5] Cleaning up test data...")
db.query(FraudFlag).filter(FraudFlag.tender_id == test_tender.id).delete()
for s in submissions:
    db.query(EvaluationResult).filter(EvaluationResult.submission_id == s.id).delete()
    db.delete(s)
db.delete(crit1)
db.delete(test_tender)
db.commit()

print("\n==========================================")
print("           Demonstration Complete           ")
print("==========================================")
