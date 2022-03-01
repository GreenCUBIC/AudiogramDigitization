#!/usr/bin/env python3
"""
Copyright (c) 2020, Carleton University Biomedical Informatics Collaboratory

This source code is licensed under the MIT license found in the
LICENSE file in the root directory of this source tree.
"""

import os
import re

from flask import Flask, jsonify, request, send_from_directory
from dotenv import load_dotenv
from werkzeug.routing import BaseConverter
from flask_cors import CORS

from portal.database import db
from portal.routes.authentication import authentication
from portal.routes.reports import reports
from portal.routes.annotation import annotation
from portal.routes.digitizer import digitizer
from portal.routes.validation import validation
from portal.routes.data import data
from portal.routes.analyzer import analyzer

# Load the environment variables
load_dotenv()

ENVIRONMENT = os.getenv("ENVIRONMENT")
PORT = os.getenv("WEBSITES_PORT")
STATIC_ASSETS_PATH = os.getenv("STATIC_ASSETS_PATH")
CACHING_ENABLED = os.getenv("CACHING_ENABLED")
DATABASE_URI = re.sub(r"@.*:", "@localhost:" if ENVIRONMENT == "dev" else "@database:", os.getenv("DATABASE_URI"))
print(DATABASE_URI)

def create_app():
    # Instantiate the app
    app = Flask(
        __name__,
        instance_relative_config=False,
        static_url_path="/",
        static_folder='portal/client-tsx/build'
    )

    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URI").replace("database", "localhost") \
            if os.getenv("ENVIRONMENT") == "dev" \
            else os.getenv("DATABASE_URI").replace("localhost", "database")

    CORS(app)

    # Whether the app should serve a new file with every request
    if not CACHING_ENABLED:
        app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

    # Add the logic for all routes to the app
    app.register_blueprint(authentication, url_prefix='/api/auth')
    app.register_blueprint(reports, url_prefix='/api/reports')
    app.register_blueprint(annotation, url_prefix='/api/annotation')
    app.register_blueprint(digitizer, url_prefix='/api/digitizer')
    app.register_blueprint(validation, url_prefix='/api/validation')
    app.register_blueprint(data, url_prefix='/api/data')
    app.register_blueprint(analyzer, url_prefix='/api/analyzer')

    # Send the app for all 404 requests
    @app.errorhandler(404)
    def not_found(e):
        return app.send_static_file('index.html')

    return app

app = create_app()
app.app_context().push()
db.init_app(app)

if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        db.init_app(app)
        db.create_all()
    app.run(host='0.0.0.0', port=int(PORT), debug=True)
