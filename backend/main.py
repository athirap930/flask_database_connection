from flask import Flask
from flask_cors import CORS
from routes.api_routes import register_routes
from database import init_db, db
import os
import time

app = Flask(__name__)

# Initialize database with PostgreSQL
init_db(app)

# Enable CORS for all origins in Docker
CORS(app)

# Register routes
register_routes(app)

def create_tables():
    """Create database tables with retry logic for Docker startup"""
    max_retries = 5
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            with app.app_context():
                db.create_all()
            print("✅ Database tables created successfully!")
            return True
        except Exception as e:
            print(f"❌ Database connection failed (attempt {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                print(f"🔄 Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
    return False

if __name__ == "__main__":
    # Wait for database to be ready and create tables
    if create_tables():
        host = os.getenv('FLASK_HOST', '0.0.0.0')
        port = int(os.getenv('FLASK_PORT', 5000))
        
        print(f"🚀 Flask API running on http://{host}:{port}")
        print("🐳 Running in Docker container")
        print("🗄️  Using PostgreSQL database")
        print("📋 Available endpoints:")
        print("   /       - API information")
        print("   /health - Detailed health check") 
        print("   /docs   - API documentation")
        print("   /api/*  - All API endpoints")
        
        app.run(debug=False, host=host, port=port)
    else:
        print("💥 Failed to connect to database after multiple attempts")
        exit(1)