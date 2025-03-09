from flask import Flask
from config import Config
import os

app = Flask(__name__)
app.config.from_object(Config)

# Ensure upload directory exists with proper permissions
upload_dir = app.config['UPLOAD_FOLDER']
os.makedirs(upload_dir, exist_ok=True)
os.chmod(upload_dir, 0o755)  # Read/write for owner, read for others

from app import routes 