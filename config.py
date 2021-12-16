from flask import Flask, Blueprint
import os

basedir = os.getcwd()

config_data = {
    "app_admin_name": 'Bulan Restaurant Portal Admin',
    "app_admin_template_mode": "bootstrap4",
    "access_deny_message": "Access Denied!, you need to Login First!",
    "basedir":os.getcwd(),
    "image_file_path": os.path.join(basedir,'static\\images'),
    "database_location": 'sqlite:///' + os.path.join(os.getcwd(), 'bulan.db'),
    "upload_folder": os.path.join(basedir,'static\\uploads'),
    "max_upload_size": 20000000,
    "allowed_extensions" : {"txt","pdf","doc","docx","xls","xksx",'png','jpg','jpeg','gif'}
}


def setup_app():
    app = Flask(__name__)
    ##setting up SQLAlchemy
    ##config for SQLAlchemy
    app.config['SQLALCHEMY_DATABASE_URI'] = config_data["database_location"]
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    ##app upload files location
    print(f'uploadfolderloc: {config_data["upload_folder"]}')
    app.config['UPLOAD_FOLDER'] = config_data["upload_folder"]
    app.config['MAX_CONTENT_PATH'] = config_data["max_upload_size"]
    ##Secret Key for Authentication
    app.config['SECRET_KEY'] = 'mysecretkey'
    ##app admin look , pulse,
    app.config['FLASK_ADMIN_SWATCH'] = 'lux'
    return app

