# -*- coding: utf-8 -*-
"""
Created on Fri Mar 27 09:32:29 2020

@author: alspe
"""

from flask import render_template, flash, redirect, url_for
from flask import request, session
from flask_login import current_user, login_user, logout_user
from flask_login import login_required
from werkzeug.urls import url_parse

from app import app, covid, db
from app.models import User
from app.forms import LoginForm, RegistrationForm



@app.route('/')
@app.route('/index/')
def index():
    return render_template('index.html')


@app.route('/about/')
def about():
    return render_template('about.html')


@app.route('/pays')
@app.route('/region<int:idReg>')
@app.route('/departement<int:idDep>')
@login_required
def prediction(idDep=-1, idReg=-1):
    nomDep  = ""
    nomReg  = ""
    nomPays = ""
    
    if idDep > 0:
        nomDep = covid.nomDepartement(idDep)
    
    elif idReg > 0:
        nomReg = covid.nomRegion(idReg)
    
    else:
        nomPays = covid.nomPays()
    
    return render_template('prediction.html',
                           idDep=idDep,
                           nomDep=nomDep,
                           idReg=idReg,
                           nomReg=nomReg,
                           nomPays=nomPays)


@app.route('/recherche/',methods = ['POST', 'GET']) 
@login_required
def recherche():
    if request.method == 'POST':
        
        try:
            idDep = int(request.form['idDep'])
            session["idDep"] = idDep
            if "idReg" in session:
                session.pop("idReg", None)
        except:
            idDep = -1
        try:
            idReg = int(request.form['idReg'])
            session["idReg"] = idReg
            if "idDep" in session:
                session.pop("idDep", None)
        except:
            idReg = -1
            
        if idDep > 0:
            covid.afficheDepartement(idDep, sauvegarde=True)
            covid.departementVsTous(idDep, sauvegarde=True)
            
            return redirect(url_for("prediction",
                                    idDep=idDep))
    
        elif idReg > 0:
            covid.afficheRegion(idReg, sauvegarde=True)
            covid.regionVsTous(idReg, sauvegarde=True)
            
            return redirect(url_for("prediction",
                                    idReg=idReg))
        
        else:
            covid.affichePays(sauvegarde=True)
            
            return redirect(url_for("prediction"))
    
    else:
        return render_template('recherche.html')

    
@app.route('/recherchebis/',methods = ['POST', 'GET']) 
@login_required
def recherchebis():
    if request.method == 'POST':
        
        if "idDep" in session:
            idDep = session.get("idDep")
            idReg = covid.departementVersRegion(idDep)
            session.pop("idDep", None)
            session["idReg"] = idReg
            
            covid.afficheRegion(idReg, sauvegarde=True)
            covid.regionVsTous(idReg, sauvegarde=True)
            
            return redirect(url_for("prediction",
                                    idReg=idReg))
        
        elif "idReg" in session: 
            covid.affichePays(sauvegarde=True)
            session.pop("idReg", None)
            
            return redirect(url_for("prediction"))
    
    else:
        return render_template('recherche.html')



# Partie pour l'identification

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Nom ou mot de passe incorrect.')
            return redirect(url_for('login'))
        
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    
    return render_template('login.html', form=form)



@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))



@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Félicitation, vous êtes maintenant un utilisateur enregistré !')
        return redirect(url_for('login'))
    
    return render_template('register.html', form=form)

