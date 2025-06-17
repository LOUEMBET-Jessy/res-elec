import os
from werkzeug.utils import secure_filename
from datetime import datetime
import uuid

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_file(file, folder):
    if not file or not allowed_file(file.filename):
        raise ValueError('Invalid file type')

    # Create upload folder if it doesn't exist
    upload_folder = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'uploads', folder)
    os.makedirs(upload_folder, exist_ok=True)

    # Generate unique filename
    filename = secure_filename(file.filename)
    unique_filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{str(uuid.uuid4())[:8]}_{filename}"
    
    file_path = os.path.join(upload_folder, unique_filename)
    file.save(file_path)
    
    return os.path.join('uploads', folder, unique_filename)
