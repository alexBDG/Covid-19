# -*- coding: utf-8 -*-
"""
Created on Fri Mar 27 09:29:34 2020

@author: alspe
"""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo

from app.models import User


class LoginForm(FlaskForm):
    username    = StringField("Nom d'utilisateur",
                              validators=[DataRequired()])
    password    = PasswordField('Mot de passe',
                                validators=[DataRequired()])
    remember_me = BooleanField('Se souvenir de moi')
    submit      = SubmitField('Connexion')
    


class RegistrationForm(FlaskForm):
    username  = StringField("Nom d'utilisateur",
                            validators=[DataRequired()])
    email     = StringField('Email', 
                            validators=[DataRequired(), 
                                        Email()])
    password  = PasswordField('Mot de passe', 
                              validators=[DataRequired()])
    password2 = PasswordField('Répéter le mot de passe',
                              validators=[DataRequired(),
                                          EqualTo('password')])
    submit = SubmitField('Enregistrer')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError("Utiliser un nom d'utilisateur différent.")

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Utiliser une adresse mail différente.')