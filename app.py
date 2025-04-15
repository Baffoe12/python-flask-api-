from main import app
from models import db

# Initialize database tables when the app starts
with app.app_context():
    db.create_all()
    print("Database tables created successfully!")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
