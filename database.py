from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Initialize SQLAlchemy instance
db = SQLAlchemy()

class CaseQueryLog(db.Model):
    """
    Database model for storing records of all case searches made by the scraper.
    """
    # Primary Key
    id = db.Column(db.Integer, primary_key=True)

    # Search Parameters
    case_type = db.Column(db.String(50), nullable=False)
    case_number = db.Column(db.String(20), nullable=False)
    filing_year = db.Column(db.String(4), nullable=False)
    
    # Response Data
    status = db.Column(db.String(20), nullable=False) # e.g., 'Success', 'Error', 'Failed (CAPTCHA)'
    raw_response = db.Column(db.Text, nullable=True) # Full JSON/HTML response snippet

    # Metadata
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"QueryLog('{self.case_type}', '{self.case_number}/{self.filing_year}', '{self.status}')"
