from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base

class PlacementRound(Base):
    __tablename__ = "placement_rounds"
    id = Column(Integer, primary_key=True, index=True)
    company_history_id = Column(Integer, ForeignKey("company_history.id"), nullable=False)
    round_name = Column(String(255), nullable=False)
    round_description = Column(String(1000), nullable=True)
    difficulty_level = Column(String(50), nullable=True)

    company_history = relationship("CompanyHistory", backref="rounds")
