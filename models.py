"""
Database models for ImpactBridge
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class CrisisCase(db.Model):
    """Crisis case model with priority scoring"""
    
    __tablename__ = 'crisis_case'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    severity = db.Column(db.Integer, nullable=False)
    people_affected = db.Column(db.Integer, nullable=False)
    urgency = db.Column(db.Integer, nullable=False)
    available_resources = db.Column(db.Integer, nullable=False)
    required_skill = db.Column(db.String(100), nullable=False)
    priority_score = db.Column(db.Integer, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Database constraints
    __table_args__ = (
        db.CheckConstraint('severity >= 1 AND severity <= 5', name='check_severity_range'),
        db.CheckConstraint('urgency >= 1 AND urgency <= 5', name='check_urgency_range'),
        db.CheckConstraint('people_affected >= 0', name='check_people_positive'),
        db.CheckConstraint('available_resources >= 0', name='check_resources_positive'),
        db.Index('idx_priority_created', 'priority_score', 'created_at'),
        db.Index('idx_severity_urgency', 'severity', 'urgency'),
    )
    
    def __repr__(self):
        return f'<CrisisCase {self.id}: {self.title} (Priority: {self.priority_score})>'
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'severity': self.severity,
            'people_affected': self.people_affected,
            'urgency': self.urgency,
            'available_resources': self.available_resources,
            'required_skill': self.required_skill,
            'priority_score': self.priority_score,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Volunteer(db.Model):
    """Volunteer/Personnel model"""
    
    __tablename__ = 'volunteer'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    skills = db.Column(db.String(200), nullable=False)
    availability = db.Column(db.String(50), nullable=False)
    registered_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Database constraints
    __table_args__ = (
        db.Index('idx_registered_at', 'registered_at'),
        db.Index('idx_availability', 'availability'),
    )
    
    def __repr__(self):
        return f'<Volunteer {self.id}: {self.name} ({self.availability})>'
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'name': self.name,
            'skills': self.skills,
            'availability': self.availability,
            'registered_at': self.registered_at.isoformat() if self.registered_at else None
        }
