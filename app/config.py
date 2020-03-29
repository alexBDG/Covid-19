# -*- coding: utf-8 -*-
"""
Created on Fri Mar 27 09:22:35 2020

@author: alspe
"""

import os
basedir = os.path.abspath(os.path.dirname(__file__))



class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or b'\xc2\xdc^*\xf1w\xce\xb7\xdd\xb7f\xf2V\xb1v\x03'
    
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    
    
class OwnConfig:
    HTTPS_ENABLED = True
    VERIFY_USER = True
    
    