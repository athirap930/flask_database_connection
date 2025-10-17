from flask import jsonify, request
from model.item_model import Item
from database import db
import time
import psutil
import os

APP_START_TIME = time.time()

def get_system_info():
    """Get system information"""
    try:
        return {
            "cpu_usage": psutil.cpu_percent(),
            "memory_usage": psutil.virtual_memory().percent,
            "disk_usage": psutil.disk_usage('/').percent,
            "python_version": os.sys.version.split()[0],
            "database": "PostgreSQL"
        }
    except:
        return {"error": "System stats unavailable"}

def register_routes(app):
    
    # Root route
    @app.route('/')
    def root():
        return jsonify({
            "message": "Flask API is running with PostgreSQL!",
            "endpoints": {
                "health": "/health",
                "docs": "/docs", 
                "api_hii": "/api/hii",
                "api_items": "/api/items"
            },
            "database": "PostgreSQL"
        })
    
    # Detailed health check at /health
    @app.route('/health')
    def health():
        current_time = time.time()
        uptime = round(current_time - APP_START_TIME, 2)
        
        # Check database health
        db_health = "healthy"
        db_type = "PostgreSQL"
        try:
            Item.query.limit(1).all()
        except Exception as e:
            db_health = f"unhealthy: {str(e)}"
            db_type = "Unknown"
        
        # Get system info
        system_info = get_system_info()
        
        return jsonify({
            "status": "healthy",
            "service": "Flask API",
            "timestamp": current_time,
            "uptime": uptime,
            "database": db_health,
            "database_type": db_type,
            "system": system_info,
            "endpoints": {
                "root": "/",
                "docs": "/docs",
                "health": "/health",
                "api_hii": "/api/hii",
                "api_items": "/api/items"
            }
        })
    
    # API Documentation at /docs
    @app.route('/docs')
    def docs():
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Flask API Documentation</title>
            <style>
                body { 
                    font-family: Arial, sans-serif; 
                    max-width: 800px; 
                    margin: 0 auto; 
                    padding: 20px; 
                    background: #f5f5f5;
                }
                .container {
                    background: white;
                    padding: 30px;
                    border-radius: 10px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }
                h1 { 
                    color: #333; 
                    text-align: center;
                    margin-bottom: 30px;
                }
                .endpoint { 
                    background: #f8f9fa; 
                    padding: 20px; 
                    margin: 15px 0; 
                    border-radius: 8px;
                    border-left: 4px solid #007bff;
                }
                .method { 
                    display: inline-block; 
                    padding: 5px 15px; 
                    border-radius: 4px; 
                    color: white; 
                    font-weight: bold;
                    margin-right: 10px;
                }
                .get { background: #28a745; }
                .post { background: #007bff; }
                .put { background: #ffc107; color: black; }
                .delete { background: #dc3545; }
                code {
                    background: #e9ecef;
                    padding: 10px;
                    border-radius: 4px;
                    display: block;
                    margin: 10px 0;
                    font-family: monospace;
                }
                a {
                    color: #007bff;
                    text-decoration: none;
                }
                a:hover {
                    text-decoration: underline;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Flask API Documentation</h1>
                
                <div class="endpoint">
                    <span class="method get">GET</span> <strong>/health</strong><br>
                    <p>Detailed health check with system information</p>
                    <code>Response: Detailed JSON with status, uptime, system metrics, etc.</code>
                </div>
                
                <div class="endpoint">
                    <span class="method get">GET</span> <strong>/api/hii</strong><br>
                    <p>Returns a simple greeting message</p>
                    <code>Response: "hii!"</code>
                </div>
                
                <div class="endpoint">
                    <span class="method get">GET</span> <strong>/api/items</strong><br>
                    <p>Get all items</p>
                    <code>Response: [{"id": 1, "name": "item1", "description": "desc1"}, ...]</code>
                </div>
                
                <div class="endpoint">
                    <span class="method post">POST</span> <strong>/api/items</strong><br>
                    <p>Create a new item</p>
                    <code>Body: {"name": "item name", "description": "item description"}</code>
                </div>
                
                <div class="endpoint">
                    <span class="method get">GET</span> <strong>/api/items/&lt;id&gt;</strong><br>
                    <p>Get a specific item by ID</p>
                </div>
                
                <div class="endpoint">
                    <span class="method put">PUT</span> <strong>/api/items/&lt;id&gt;</strong><br>
                    <p>Update an existing item</p>
                    <code>Body: {"name": "new name", "description": "new description"}</code>
                </div>
                
                <div class="endpoint">
                    <span class="method delete">DELETE</span> <strong>/api/items/&lt;id&gt;</strong><br>
                    <p>Delete an item by ID</p>
                </div>
                
                <h2>Technology Stack</h2>
                <ul>
                    <li><strong>Backend:</strong> Flask with PostgreSQL</li>
                    <li><strong>Frontend:</strong> HTML, CSS, JavaScript</li>
                    <li><strong>Containerization:</strong> Docker & Docker Compose</li>
                    <li><strong>Database:</strong> PostgreSQL</li>
                </ul>
                
                <h2>Access Points</h2>
                <ul>
                    <li><a href="/">Root</a> - API information</li>
                    <li><a href="/health">Health Check</a> - Detailed system health</li>
                    <li><a href="/docs">Documentation</a> - This page</li>
                    <li><a href="http://localhost:3000" target="_blank">Frontend App</a> - User interface</li>
                </ul>
            </div>
        </body>
        </html>
        """
    
    # API routes
    @app.route('/api/hii')
    def hii():
        return "hii!"
    
    # GET all items & CREATE item
    @app.route('/api/items', methods=['GET', 'POST'])
    def items():
        if request.method == 'GET':
            items = Item.query.all()
            return jsonify([item.to_dict() for item in items])
        else:  # POST
            data = request.get_json()
            if not data or not data.get('name'):
                return jsonify({"error": "Name is required"}), 400
            
            item = Item(
                name=data['name'], 
                description=data.get('description', '')
            )
            db.session.add(item)
            db.session.commit()
            return jsonify(item.to_dict())
    
    # GET single item, UPDATE item, DELETE item
    @app.route('/api/items/<int:id>', methods=['GET', 'PUT', 'DELETE'])
    def single_item(id):
        item = Item.query.get(id)
        
        if not item:
            return jsonify({"error": "Item not found"}), 404
        
        if request.method == 'GET':
            return jsonify(item.to_dict())
        
        elif request.method == 'PUT':
            data = request.get_json()
            if 'name' in data:
                item.name = data['name']
            if 'description' in data:
                item.description = data['description']
            db.session.commit()
            return jsonify(item.to_dict())
        
        elif request.method == 'DELETE':
            db.session.delete(item)
            db.session.commit()
            return jsonify({"message": "Item deleted successfully"})