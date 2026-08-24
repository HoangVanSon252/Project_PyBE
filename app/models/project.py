from sqlalchemy.orm import relationship
import enum
from sqlalchemy.sql import func
from app.db.database import Base
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Enum, Boolean

class ProjectRole(str, enum.Enum):
    OWNER = "OWNER"
    MEMBER = "MEMBER"

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_deleted = Column(Boolean, default=False)
    delete_at = Column(DateTime(timezone=True), nullable=True)

    owner = relationship("Users", back_populates="owner_project")
    members = relationship("ProjectMember", back_populates="project", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="project", cascade="all, delete-orphan")

    
class ProjectMember(Base):
    __tablename__ = "project_members"
    project_id = Column(Integer, ForeignKey("projects.id"), primary_key= True)
    user_id = Column(Integer, ForeignKey("users.id"), primary_key= True)
    role = Column(Enum(ProjectRole), nullable=False, default= ProjectRole.MEMBER)
    joined_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    project = relationship("Project", back_populates="members")
    user = relationship("Users", back_populates="project_members")