from flask import Flask
from flask_cors import CORS

from api.flow import flow_bp
from api.node import node_bp

app = Flask(__name__)
CORS(app)

# Register blueprints
app.register_blueprint(flow_bp, url_prefix='/')
app.register_blueprint(node_bp, url_prefix='/')

# Create database tables
# Base.metadata.create_all(bind=engine)

if __name__ == '__main__':
    app.run(debug=True)
