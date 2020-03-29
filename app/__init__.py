# -*- coding: utf-8 -*-
"""
Created on Fri Mar 27 10:12:38 2020

@author: alspe
"""


from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

from app.config import Config

app = Flask(__name__)
app.config.from_object(Config)

db      = SQLAlchemy(app)
migrate = Migrate(app, db)

login            = LoginManager(app)
login.login_view = 'login'


from donnees_covid import donneesCovid

# Initialisation du modèle
covid = donneesCovid()


from app import routes, models


"""
import sys
from app.config import OwnConfig

from OpenSSL import SSL
import ssl

context = None
if OwnConfig.HTTPS_ENABLED:
    context = SSL.Context(SSL.TLSv1_METHOD)
    
    if OwnConfig.VERIFY_USER:
        context.verify_mode = ssl.CERT_REQUIRED
        context.load_verify_locations("ca.crt")
        
    try:
        context.use_certificate_file("server.crt")
        context.use_privatekey_file("server.key")
        
    except Exception as e:
        sys.exit("Error starting flask server. " +
                 "Missing cert of key. Details: {}".format(e))
"""




