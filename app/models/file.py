from sqlalchemy import Boolean, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class UploadedFile(Base):
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    template_type = Column(String, nullable=False)
    upload_date = Column(DateTime(timezone=True), server_default=func.now())
    processed = Column(Boolean, default=False)
    file_path = Column(String)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=True)
    
    # Relationships
    operations = relationship("AccountingOperation", back_populates="file", cascade="all, delete-orphan")
    user = relationship("User", back_populates="files")