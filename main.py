from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import os
from models import db, AccidentReport, User, SensorData, SystemStatus
from flask_bcrypt import Bcrypt
from flask_jwt_extended import create_access_token, jwt_required, JWTManager, get_jwt_identity

app = Flask(__name__)

app.config.from_object(os.getenv('APP_SETTINGS', 'config.DevelopmentConfig'))

app.config['JWT_SECRET_KEY'] = app.config['SECRET_KEY']

db.init_app(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

CORS(app)

prevention_alerts = [
    {
        "id": 1,
        "location": "Intersection A",
        "alert_type": "speed",
        "timestamp": "2024-03-20T10:05:00",
        "description": "Speed limit exceeded",
        "status": "active"
    },
    {
        "id": 2,
        "location": "School Zone",
        "alert_type": "pedestrian",
        "timestamp": "2024-03-20T12:00:00",
        "description": "High pedestrian activity",
        "status": "active"
    }
]

# --- Authentication Endpoints --- 

@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not username or not email or not password:
        return jsonify({"error": "Missing username, email, or password"}), 400

    # Check if user or email already exists
    existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
    if existing_user:
        return jsonify({"error": "Username or email already exists"}), 409 # 409 Conflict

    try:
        # Hash the password
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        
        # Create new user
        new_user = User(username=username, email=email, password_hash=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        
        # Optionally: return the created user's info (excluding password)
        return jsonify({"message": "User created successfully", "user": {"id": new_user.id, "username": new_user.username, "email": new_user.email}}), 201

    except Exception as e:
        db.session.rollback()
        # Log the error e
        return jsonify({"error": "Could not create user", "details": str(e)}), 500

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Missing username or password"}), 400

    try:
        user = User.query.filter_by(username=username).first()

        # Check if user exists and password is correct
        if user and bcrypt.check_password_hash(user.password_hash, password):
            # Create JWT access token - identity can be user ID or username
            access_token = create_access_token(identity=user.id)
            return jsonify(access_token=access_token, user_id=user.id, username=user.username)
        else:
            return jsonify({"error": "Invalid username or password"}), 401 # 401 Unauthorized

    except Exception as e:
        # Enhanced error logging
        error_message = str(e)
        app.logger.error(f"Login error: {error_message}")
        return jsonify({"error": "Login failed", "details": error_message}), 500

# --- Root Endpoint --- 

@app.route('/')
def root():
    return jsonify({
        "message": "Welcome to Accident Detection and Prevention API",
        "endpoints": {
            "accidents": {
                "create": "POST /accidents/ (Authentication Required)",
                "list": "GET /accidents/",
                "get": "GET /accidents/<id>"
            },
            "alerts": {
                "create": "POST /alerts/",
                "list": "GET /alerts/",
                "get": "GET /alerts/<id>"
            },
            "auth": {
                "signup": "POST /signup",
                "login": "POST /login"
            },
            "sensor-data": {
                "create": "POST /sensor-data/ (Authentication Required)",
                "latest": "GET /sensor-data/latest (Authentication Required)"
            },
            "system-status": {
                "update": "POST /system-status/ (Authentication Required)",
                "get": "GET /system-status/ (Authentication Required)"
            }
        }
    })

@app.route('/accidents/', methods=['GET'])
def get_accidents():
    try:
        all_reports = AccidentReport.query.all()
        return jsonify([report.to_dict() for report in all_reports])
    except Exception as e:
        return jsonify({"error": "Could not retrieve accident reports", "details": str(e)}), 500

@app.route('/accidents/<int:accident_id>', methods=['GET'])
def get_accident(accident_id):
    try:
        report = AccidentReport.query.get(accident_id)
        if report is None:
            return jsonify({"error": "Accident not found"}), 404
        return jsonify(report.to_dict())
    except Exception as e:
        return jsonify({"error": "Could not retrieve accident report", "details": str(e)}), 500

@app.route('/accidents/', methods=['POST'])
@jwt_required()
def create_accident():
    data = request.get_json()
    current_user_id = get_jwt_identity()
    
    required_fields = ['location', 'severity', 'description']
    if not data or not all(field in data for field in required_fields):
        missing = [field for field in required_fields if field not in data]
        return jsonify({"error": "Missing required fields", "missing": missing}), 400

    try:
        new_report = AccidentReport(
            user_id=current_user_id,
            location=data['location'],
            severity=data['severity'],
            description=data.get('description'), 
            status=data.get('status', 'pending'), 
            weather_conditions=data.get('weather_conditions'),
            road_conditions=data.get('road_conditions'),
            number_of_vehicles=data.get('number_of_vehicles'),
            injuries_reported=data.get('injuries_reported', False)
        )
        db.session.add(new_report)
        db.session.commit()
        return jsonify(new_report.to_dict()), 201
    except Exception as e:
        db.session.rollback() 
        return jsonify({"error": "Could not create accident report", "details": str(e)}), 500

@app.route('/alerts/', methods=['GET'])
def get_alerts():
    return jsonify(prevention_alerts)

@app.route('/alerts/<int:alert_id>', methods=['GET'])
def get_alert(alert_id):
    for alert in prevention_alerts:
        if alert['id'] == alert_id:
            return jsonify(alert)
    return jsonify({"error": "Alert not found"}), 404

@app.route('/alerts/', methods=['POST'])
def create_alert():
    data = request.get_json()
    new_alert = {
        "id": len(prevention_alerts) + 1,
        "location": data.get('location'),
        "alert_type": data.get('alert_type'),
        "timestamp": datetime.now().isoformat(),
        "description": data.get('description'),
        "status": "active"
    }
    prevention_alerts.append(new_alert)
    return jsonify(new_alert), 201

@app.route('/test/alert', methods=['POST'])
def test_create_alert():
    test_alert = {
        "id": len(prevention_alerts) + 1,
        "location": "Test Location",
        "alert_type": "test",
        "timestamp": datetime.now().isoformat(),
        "description": "Test alert",
        "status": "active"
    }
    prevention_alerts.append(test_alert)
    return jsonify(test_alert), 201

@app.route('/sensor-data/', methods=['POST'])
@jwt_required()
def create_sensor_data():
    data = request.get_json()
    current_user_id = get_jwt_identity()
    try:
        sensor_entry = SensorData(
            user_id=current_user_id,
            timestamp=datetime.utcnow(),
            latitude=data.get('latitude'),
            longitude=data.get('longitude'),
            max30102_heart_rate=data.get('max30102_heart_rate'),
            max30102_spo2=data.get('max30102_spo2'),
            alcohol_level=data.get('alcohol_level'),
            other_data=data.get('other_data')
        )
        db.session.add(sensor_entry)
        db.session.commit()
        return jsonify(sensor_entry.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Could not save sensor data', 'details': str(e)}), 500

@app.route('/sensor-data/latest', methods=['GET'])
@jwt_required()
def get_latest_sensor_data():
    current_user_id = get_jwt_identity()
    try:
        latest_data = SensorData.query.filter_by(user_id=current_user_id).order_by(SensorData.timestamp.desc()).first()
        if latest_data:
            return jsonify(latest_data.to_dict())
        else:
            return jsonify({'error': 'No sensor data found for user'}), 404
    except Exception as e:
        return jsonify({'error': 'Could not retrieve sensor data', 'details': str(e)}), 500

# --- System Status Endpoints ---

@app.route('/system-status/', methods=['POST'])
@jwt_required()
def update_system_status():
    data = request.get_json()
    current_user_id = get_jwt_identity()
    
    if 'is_active' not in data:
        return jsonify({"error": "Missing required field: is_active"}), 400
    
    try:
        # Check if a status entry already exists for this user
        status = SystemStatus.query.filter_by(user_id=current_user_id).first()
        
        if status:
            # Update existing status
            status.is_active = data['is_active']
            status.last_updated = datetime.utcnow()
            if 'device_id' in data:
                status.device_id = data['device_id']
            if 'device_info' in data:
                status.device_info = data['device_info']
        else:
            # Create new status entry
            status = SystemStatus(
                user_id=current_user_id,
                is_active=data['is_active'],
                device_id=data.get('device_id'),
                device_info=data.get('device_info')
            )
            db.session.add(status)
        
        db.session.commit()
        return jsonify(status.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Could not update system status", "details": str(e)}), 500

@app.route('/system-status/', methods=['GET'])
@jwt_required()
def get_system_status():
    current_user_id = get_jwt_identity()
    try:
        status = SystemStatus.query.filter_by(user_id=current_user_id).first()
        if status:
            return jsonify(status.to_dict())
        else:
            return jsonify({"error": "No system status found for user", "is_active": False}), 404
    except Exception as e:
        return jsonify({"error": "Could not retrieve system status", "details": str(e)}), 500

@app.route('/system-status/all', methods=['GET'])
@jwt_required()
def get_all_active_systems():
    try:
        # Only administrators should be able to access this endpoint
        # For now, we'll just implement it without admin checks
        active_systems = SystemStatus.query.filter_by(is_active=True).all()
        return jsonify({
            "active_count": len(active_systems),
            "systems": [system.to_dict() for system in active_systems]
        })
    except Exception as e:
        return jsonify({"error": "Could not retrieve active systems", "details": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port)