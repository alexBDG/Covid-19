# -*- coding: utf-8 -*-
"""
Created on Fri Mar 27 09:32:29 2020

@author: alspe
"""

from flask import render_template, flash, redirect, url_for
from flask import request, session, jsonify
from flask_login import current_user, login_user, logout_user
from flask_login import login_required
from werkzeug.urls import url_parse

from app import app, covid, db
from app.models import User, Ip
from app.forms import LoginForm, RegistrationForm

from datetime import datetime, timedelta



@app.route('/')
@app.route('/index/')
def index():
    # Comptage de visite si la dernière visite était il y a plus de 1h
    flag = True
    ip = Ip.query.filter_by(ip_address=request.remote_addr).first()
    date_actuelle = datetime.now()
    if ip is not None:
        if (ip.ip_address != "127.0.0.1") and (ip.ip_address != "localhost"):
            date_objet = ip.time_visite
            if date_objet.date() == date_actuelle.date():
                if (date_objet + timedelta(hours=1)).time() > date_actuelle.time():
                    flag = False
        else:
            flag = False
        
    if flag:
        ip = Ip(ip_address=request.remote_addr)
        ip.set_agent(str(request.user_agent))
        db.session.add(ip)
        db.session.commit()
    
    return render_template('index.html',
                           visiteurs=db.session.query(Ip).count())


@app.route('/about/')
def about():
    return render_template('about.html')


@app.route('/pays')
@app.route('/pays<idPays>')
@app.route('/region<int:idReg>')
@app.route('/departement<int:idDep>')
#@login_required
def prediction(idDep=-1, idReg=-1, idPays=""):
    nomDep  = ""
    nomReg  = ""
    nomPays = ""
    
    if idDep > 0:
        nomDep = covid.nomDepartement(idDep)
    
    elif idReg > 0:
        nomReg = covid.nomRegion(idReg)
    
    elif len(idPays) > 0:
        nomPays = covid.nomPays()
    
    return render_template('prediction.html',
                           idDep=idDep,
                           nomDep=nomDep,
                           idReg=idReg,
                           nomReg=nomReg,
                           idPays=idPays,
                           nomPays=nomPays)


@app.route('/france/',methods = ['POST', 'GET']) 
#@login_required
def france():
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
            covid.sosMedecins(idDep=idDep, sauvegarde=True)
            
            return redirect(url_for("prediction",
                                    idDep=idDep))
    
        elif idReg > 0:
            covid.afficheRegion(idReg, sauvegarde=True)
            covid.regionVsTous(idReg, sauvegarde=True)
            covid.sosMedecins(idReg=idReg, sauvegarde=True)
            
            return redirect(url_for("prediction",
                                    idReg=idReg))
        
        else:
            covid.affichePays(sauvegarde=True)
            covid.sosMedecins(sauvegarde=True)
            
            return redirect(url_for("prediction",
                                    idPays="FR"))
    
    else:
        return render_template('france.html',
                               choixDep=covid.decoupage_dep,
                               choixReg=covid.decoupage_reg)

    
@app.route('/francebis/',methods = ['POST', 'GET']) 
#@login_required
def francebis():
    if request.method == 'POST':
        
        if "idDep" in session:
            idDep = session.get("idDep")
            idReg = int(covid.departementVersRegion(idDep))
            session.pop("idDep", None)
            session["idReg"] = idReg
            
            covid.afficheRegion(idReg, sauvegarde=True)
            covid.regionVsTous(idReg, sauvegarde=True)
            covid.sosMedecins(idReg=idReg, sauvegarde=True)
            
            return redirect(url_for("prediction",
                                    idReg=idReg))
        
        elif "idReg" in session: 
            covid.affichePays(sauvegarde=True)
            covid.sosMedecins(sauvegarde=True)
            session.pop("idReg", None)
            
            return redirect(url_for("prediction",
                                    idPays="FR"))
    
    else:
        return render_template('france.html')


@app.route('/monde/',methods = ['POST', 'GET'])
#@login_required
def monde():
    if request.method == 'POST':
        
        n_premiers = int(request.form['nPremiers'])
        n_infectes = int(request.form['nInfectes'])
        n_deces    = int(request.form['nDeces'])
        
        covid.afficheMonde(n_premiers=n_premiers,
                           n_infectes=n_infectes,
                           n_deces=n_deces,
                           sauvegarde=True)
        
        return redirect(url_for("prediction"))
    
    else:
        return render_template('monde.html')
    
    



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



# Gérer les erreurs

@app.errorhandler(404)
def err404(e):
    return render_template('404.html', err=e), 404


@app.errorhandler(500)
def not_found(e):
    db.session.rollback()
    return render_template('500.html', err=e), 500