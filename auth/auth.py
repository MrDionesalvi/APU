from flask import *
from utils import *
from database import Database

import requests

auth = Blueprint('auth', __name__, template_folder='views', static_folder='assets', static_url_path='/assets')


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        message = None
        invalid_inputs = {}

        errors = False
        if username == '':
            invalid_inputs['username'] = 'Devi inserire un username!'
            errors = True

        if password == '':
            invalid_inputs['password'] = 'Devi inserire una password!'
            errors = True

        if errors:
            return render_template('login.html', invalid_inputs=invalid_inputs, username_value=username, password_value=password)

        try:
            response = requests.get(f'https://sunfire.a-centauri.com/npayapi/?richiesta=estratto&utente={username}&auth={password}', timeout=3).json()
            if response['status'] != 403:
                session['logged'] = True
                session['id'] = response['status']
                session['username'] = username
                session['password'] = password
                session['admin'] = 0
                session['member'] = 0

                db = Database()
                data = db.session.query(db.user).filter(db.user.username == session['username']).first()
                
                
                if data:
                    if data.admin == 1:
                        session['admin'] = 1
                    if data.member == 1:
                        session['member'] = 1
                else:                    
                    db_session = db.session
                    db_session.add(db.user(username=username))
                    db_session.commit()
                db.session.close()
                    
                return redirect(url_for('dashboard.index'))
            elif response['detail'] == 'Credenziali errate':
                invalid_inputs['password'] = 'Password errata!'
            elif response['detail'] == 'Utente non trovato':
                invalid_inputs['username'] = 'Utente inesistente!'
        except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout):
            message = 'Impossibile contattare i server di autenticazione! Riprova pi?? tardi.'

        return render_template('login.html', invalid_inputs=invalid_inputs, message=message, username_value=username, password_value=password)


    if session.get('logged'):
        return redirect(url_for('dashboard.index'))
    else:
        return render_template('login.html', invalid_inputs={})


@auth.route('/logout')
def logout():
    if session.get('logged'):
        session.clear()
        session['logged'] = False

    return redirect(url_for('index'))
