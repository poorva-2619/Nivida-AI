import sys
from fastapi.testclient import TestClient
from unittest.mock import patch
import json

from main import app
from database import get_db, SessionLocal
from models import User, Tender, Criteria
from routes.auth import create_access_token

client = TestClient(app)

print("==========================================")
print("   Phase 4: LLM Integration Demonstration ")
print("==========================================")

# 1. Setup Mock DB and Admin token
db = SessionLocal()
admin_user = db.query(User).filter(User.email == "admin@nividaai.gov.in").first()
if not admin_user:
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    admin_user = User(
        email="admin@nividaai.gov.in",
        password_hash=pwd_context.hash("admin123"),
        role="admin",
        name="System Admin"
    )
    db.add(admin_user)
    db.commit()
    db.refresh(admin_user)

access_token = create_access_token(data={"sub": admin_user.email})
headers = {"Authorization": f"Bearer {access_token}"}

# Create a mock tender in DB
test_tender = Tender(title="Phase 4 Test Tender", uploaded_by=admin_user.id, file_path="mock_path.docx")
db.add(test_tender)
db.commit()
db.refresh(test_tender)

print(f"[1] Created Test Tender with ID: {test_tender.id}")

# 2. Test Extract Criteria Endpoint
print("\n[2] Testing POST /api/tender/{tender_id}/extract-criteria")

with patch("routes.tender.OCRService.extract_text_from_file") as mock_ocr:
    mock_ocr.return_value = {"text": "Minimum Annual Turnover must be Rs 10 Crore."}
    
    with patch("routes.tender.LLMService.extract_tender_criteria") as mock_extract:
        mock_extract.return_value = {
            "tender_summary": "A mock tender for road construction.",
            "criteria": [
                {
                    "id": "C1",
                    "title": "Minimum Annual Turnover",
                    "type": "Financial",
                    "mandatory": True,
                    "requirement": "Annual turnover must be at least Rs 10 Crore",
                    "threshold_value": 10,
                    "threshold_unit": "Crore INR",
                    "comparison": "gte"
                }
            ],
            "total_mandatory": 1,
            "total_optional": 0
        }
        
        with patch("routes.tender.LLMService.generate_summary_document") as mock_summary:
            mock_summary.return_value = {
                "title": "Tender Requirements Summary",
                "sections": [
                    { "heading": "What This Tender Is For", "content": "Road construction." }
                ]
            }
            
            # Using patch to bypass get_extension since file doesn't actually exist
            with patch("routes.tender.get_extension") as mock_ext:
                mock_ext.return_value = "docx"
                response = client.post(f"/api/tender/{test_tender.id}/extract-criteria", headers=headers)
                print(f"Status Code: {response.status_code}")
                if response.status_code == 200:
                    print("Response JSON:")
                    print(json.dumps(response.json(), indent=2))
                else:
                    print(response.text)

# Verify criteria was saved in DB
saved_criteria = db.query(Criteria).filter(Criteria.tender_id == test_tender.id).all()
print(f"\n[DB Check] Saved {len(saved_criteria)} criteria in the database.")
for c in saved_criteria:
    print(f" - {c.code}: {c.title} ({c.type})")

# 3. Test Summary Endpoint
print("\n[3] Testing GET /api/tender/{tender_id}/summary")
summary_response = client.get(f"/api/tender/{test_tender.id}/summary", headers=headers)
print(f"Status Code: {summary_response.status_code}")
if summary_response.status_code == 200:
    print("Response JSON:")
    print(json.dumps(summary_response.json(), indent=2))
else:
    print(summary_response.text)

# Cleanup
db.query(Criteria).filter(Criteria.tender_id == test_tender.id).delete()
db.delete(test_tender)
db.commit()
print("\n==========================================")
print("           Demonstration Complete           ")
print("==========================================")
