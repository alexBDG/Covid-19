# -*- coding: utf-8 -*-
"""
Created on Fri Mar 27 10:19:28 2020

@author: alspe
"""

from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask_login import UserMixin

from app import db, login


# Combien d'utilisateurs enregistrés :
# db.session.query(User).count()
# Affiche tous les utilisateurs enregistrés :
# db.session.query(User).all()

class User(UserMixin, db.Model):
    id            = db.Column(db.Integer, primary_key=True)
    username      = db.Column(db.String(64), index=True, unique=True)
    email         = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    posts         = db.relationship('Post', backref='author', lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    
    
class Post(db.Model):
    id        = db.Column(db.Integer, primary_key=True)
    body      = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id   = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post {}>'.format(self.body)
    
    
    
class Ip(db.Model):
    id           = db.Column(db.Integer, primary_key=True)
    ip_address   = db.Column(db.String(64))
    time_visite  = db.Column(db.DateTime, index=True, default=datetime.now())
    agent        = db.Column(db.String(128))

    def __repr__(self):
        return '<Ip {}>'.format(self.ip_address)
    
    def set_agent(self, agent):
        self.agent = agent
    
    
    
    
@login.user_loader
def load_user(id):
    return User.query.get(int(id))




