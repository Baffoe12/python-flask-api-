from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with accident reports
    accident_reports = db.relationship('AccidentReport', backref='user', lazy=True)
    
    # Relationship with sensor data
    sensor_data = db.relationship('SensorData', backref='user', lazy=True)

class AccidentReport(db.Model):
    __tablename__ = 'accident_reports'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    location = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    severity = db.Column(db.String(50))
    status = db.Column(db.String(50), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Additional fields for accident details
    weather_conditions = db.Column(db.String(100))
    road_conditions = db.Column(db.String(100))
    number_of_vehicles = db.Column(db.Integer)
    injuries_reported = db.Column(db.Boolean, default=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'location': self.location,
            'description': self.description,
            'severity': self.severity,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'weather_conditions': self.weather_conditions,
            'road_conditions': self.road_conditions,
            'number_of_vehicles': self.number_of_vehicles,
            'injuries_reported': self.injuries_reported
        }

class SensorData(db.Model):
    __tablename__ = 'sensor_data'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    max30102_heart_rate = db.Column(db.Float, nullable=True)
    max30102_spo2 = db.Column(db.Float, nullable=True)
    alcohol_level = db.Column(db.Float, nullable=True)
    other_data = db.Column(db.JSON, nullable=True)  # For extensibility

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'max30102_heart_rate': self.max30102_heart_rate,
            'max30102_spo2': self.max30102_spo2,
            'alcohol_level': self.alcohol_level,
            'other_data': self.other_data
        }

class SystemStatus(db.Model):
    __tablename__ = 'system_status'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=False)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    device_id = db.Column(db.String(100), nullable=True)
    device_info = db.Column(db.JSON, nullable=True)  # Additional device information
    
    # Relationship with user
    user = db.relationship('User', backref='system_statuses', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'is_active': self.is_active,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None,
            'device_id': self.device_id,
            'device_info': self.device_info
        }