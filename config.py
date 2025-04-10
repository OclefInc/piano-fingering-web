import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'a_default_secret_key'
    UPLOAD_FOLDER = 'uploads'
    ALLOWED_EXTENSIONS = {'txt', 'mid', 'midi', 'msc', 'mscz', 'mscx'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB limit for file uploads

    @staticmethod
    def is_allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS