# Accident Detection and Prevention API

This is a REST API for managing accident detection and prevention systems. The API provides endpoints for reporting accidents and managing prevention alerts.

## Local Development

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the server:

```bash
python main.py
```

The API will be available at `http://localhost:8000`

## Deployment on Render

This API can be easily deployed on Render:

1. Create a new Web Service on Render
2. Connect your GitHub repository
3. Use the following settings:
   - Environment: Python
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

The service will be automatically deployed and you'll get a URL like `https://your-app-name.onrender.com`

## API Documentation

Once the server is running, you can access the interactive API documentation at:
- Swagger UI: `/docs`
- ReDoc: `/redoc`

## Endpoints

### Accidents
- `POST /accidents/` - Create a new accident report
- `GET /accidents/` - Get all accident reports
- `GET /accidents/{accident_id}` - Get a specific accident report

### Prevention Alerts
- `POST /alerts/` - Create a new prevention alert
- `GET /alerts/` - Get all prevention alerts
- `GET /alerts/{alert_id}` - Get a specific prevention alert

## Data Models

### AccidentReport
```json
{
    "id": 1,
    "location": "string",
    "severity": "string",
    "timestamp": "datetime",
    "description": "string",
    "status": "string"
}
```

### PreventionAlert
```json
{
    "id": 1,
    "location": "string",
    "alert_type": "string",
    "timestamp": "datetime",
    "description": "string",
    "status": "string"
}
``` 