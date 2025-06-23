# -*- coding: utf-8 -*-
from app import routes
from flask import Flask
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", "dev-key")


# Import routes after creating the app to avoid circular imports
# This is a common pattern in Flask applications to ensure that the app is created before routes are imported.
# If routes are imported before the app is created, it can lead to circular import issues
# because routes often need to access the app instance.
