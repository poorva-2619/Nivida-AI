from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Text, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False) # admin or vendor
    name = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Tender(Base):
    __tablename__ = "tenders"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    uploaded_by = Column(Integer, ForeignKey("users.id"))
    file_path = Column(String)
    status = Column(String, default="active")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    summary_json = Column(Text, nullable=True)

    criteria = relationship("Criteria", back_populates="tender")
    submissions = relationship("VendorSubmission", back_populates="tender")

class Criteria(Base):
    __tablename__ = "criteria"
    id = Column(Integer, primary_key=True, index=True)
    tender_id = Column(Integer, ForeignKey("tenders.id"))
    code = Column(String)
    title = Column(String)
    type = Column(String)
    mandatory = Column(Boolean, default=True)
    requirement = Column(Text)
    threshold_value = Column(Float, nullable=True)
    threshold_unit = Column(String, nullable=True)
    comparison = Column(String, nullable=True)

    tender = relationship("Tender", back_populates="criteria")

class VendorSubmission(Base):
    __tablename__ = "vendor_submissions"
    id = Column(Integer, primary_key=True, index=True)
    tender_id = Column(Integer, ForeignKey("tenders.id"))
    vendor_id = Column(Integer, ForeignKey("users.id"))
    files_json = Column(Text) # JSON string of files
    status = Column(String, default="pending")
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())

    tender = relationship("Tender", back_populates="submissions")

class EvaluationResult(Base):
    __tablename__ = "evaluation_results"
    id = Column(Integer, primary_key=True, index=True)
    submission_id = Column(Integer, ForeignKey("vendor_submissions.id"))
    criteria_id = Column(Integer, ForeignKey("criteria.id"))
    verdict = Column(String)
    confidence = Column(Float)
    explanation = Column(Text)
    source_snippet = Column(Text)
    officer_override = Column(Boolean, default=False)
    officer_notes = Column(Text, nullable=True)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)

class FraudFlag(Base):
    __tablename__ = "fraud_flags"
    id = Column(Integer, primary_key=True, index=True)
    tender_id = Column(Integer, ForeignKey("tenders.id"))
    flag_type = Column(String)
    vendor_ids_json = Column(Text)
    message = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class AuditLog(Base):
    __tablename__ = "audit_log"
    id = Column(Integer, primary_key=True, index=True)
    action_type = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    tender_id = Column(Integer, ForeignKey("tenders.id"), nullable=True)
    input_summary = Column(Text)
    output_summary = Column(Text)
    model_version = Column(String)
    confidence = Column(Float, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
