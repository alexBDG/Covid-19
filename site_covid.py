# -*- coding: utf-8 -*-
"""
Created on Fri Mar 27 10:33:39 2020

@author: alspe
"""

from app import app, db
from app.models import User, Post, Ip


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Post': Post, 'Ip': Ip}





if __name__ == '__main__':
    
    """
    set OPENSSL_CONF=C:/Users/alspe/Anaconda3/pkgs/openssl-1.1.1e-he774522_0/Library/openssl.cnf
    openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 1
    
    FR
    Île-de-France
    Paris
    Covid-19 : Stats et Prévisions
    
    127.0.0.1
    """
    
    """
    # Generate CA certificate (no password)
    openssl genrsa -out root_ca.key 2048
    openssl req -x509 -new -nodes -key root_ca.key -sha256 -days 1 -out root_ca.crt
    
    # Generate client request and sign it by the CA
    openssl genrsa -out client.key 2048
    openssl req -new -key client.key -out client.csr
    openssl x509 -req -in client.csr -CA root_ca.crt -CAkey root_ca.key -CAcreateserial -out client.crt -days 1 -sha256
    
    # Define the PEM files for CA and client
    type root_ca.crt root_ca.key > root_ca.pem
    type client.crt client.key > client.pem
    """
    
    """
    set FLASK_APP=site_covid.py
    flask db init
    flask db migrate -m "users table"
    flask db upgrade
    
    # Si mise à jour de la base :
    flask db migrate
    flaks db upgrade
    """
    
    """
    flask run -h '0.0.0.0' -p 8888 --cert=cert.pem --key=key.pem
    """
    
    app.run(debug=False),
#            host="0.0.0.0",
#            port=8888)#,
#            ssl_context=('cert.pem', 'key.pem'))
#            ssl_context=app.context)
    
    