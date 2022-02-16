from flask import redirect, url_for, session, request
from datetime import datetime
from functools import wraps
from flask.json import jsonify
from sqlalchemy.ext.declarative import DeclarativeMeta


from database import Database
import json
import math

def login_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        if not session.get('logged'):
            return redirect(url_for('auth.login', after=request.path))
        return f(*args, **kwargs)

    return decorator

def is_admin(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        if not session.get('admin'):
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorator

def is_member(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        if not session.get('member'):
            return redirect(url_for('dashboard.notMember'))
        return f(*args, **kwargs)
    return decorator

def count_taxes(common, precious, mineral, nether):
    """
    Conta quanti IC devono essere pagati per quelle api
    """
    total = 0

    common_category = math.ceil(common/15)
    precious_category = math.ceil(precious/15)
    mineral_category = math.ceil(mineral/15)
    nether_category = math.ceil(nether/15)

    #print(common, precious, mineral, nether)
    #print(common_category, precious_category, mineral_category, nether_category)

    if common_category > 1:
        total += common * 2500

    if precious_category == 1:
        total += precious * 2500
    elif precious_category == 2:
        total += precious * 5000
    elif precious_category == 3:
        total += precious * 10000
    elif precious_category == 4:
        total += precious * 20000
    elif precious_category == 5:
        total += precious * 35000
    elif precious_category == 6:
        total += precious * 42000
    elif precious_category == 7:
        total += precious * 62000
    elif precious_category > 8:
        total += precious * 85000

    if mineral_category == 1:
        total += mineral * 2500
    elif mineral_category == 2:
        total += mineral * 5000
    elif mineral_category == 3:
        total += mineral * 10000
    elif mineral_category == 4:
        total += mineral * 20000
    elif mineral_category == 5:
        total += mineral * 35000
    elif mineral_category == 6:
        total += mineral * 42000
    elif mineral_category == 7:
        total += mineral * 62000
    elif mineral_category > 8:
        total += mineral * 85000
    
    if nether_category == 2:
        total += nether * 500
    elif nether_category == 3:
        total += nether * 1000
    elif nether_category == 4:
        total += nether * 5000
    elif nether_category == 5:
        total += nether * 35000
    elif nether_category == 6:
        total += nether * 42000
    elif nether_category > 7:
        total += nether * 85000

    return total

class AlchemyEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj.__class__, DeclarativeMeta):
            # an SQLAlchemy class
            fields = {}
            for field in [x for x in dir(obj) if not x.startswith('_') and x != 'metadata']:
                data = obj.__getattribute__(field)
                try:
                    json.dumps(data) # this will fail on non-encodable values, like other classes
                    fields[field] = data
                except TypeError:
                    fields[field] = None
            # a json-encodable dict
            return fields

        return json.JSONEncoder.default(self, obj)


def get_Beehives(username: str):
    """
    Restituisce i Beehives sul DB
    """

    db = Database()
    db_session = db.session
    data = db_session.query(db.beehives).filter(db.beehives.owner == username).all()

    data_dumped = json.dumps(data, cls=AlchemyEncoder)

    db_session.close()

    return data_dumped

def get_AllBeehives():
    """
    Restituisce i Beehives sul DB
    """    
    
    db = Database()
    db_session = db.session
    data = db_session.query(db.beehives).all()

    data_dumped = json.dumps(data, cls=AlchemyEncoder)

    db_session.close()

    return data_dumped

def get_Apiarys(id: int):
    """
    Restituisce gli Apiarys con l'id dell'Alveare madre
    """

    db = Database()
    db_session = db.session
    data = db_session.query(db.apiarys).filter(db.apiarys.idBeehive == id).all()

    data_dumped = json.dumps(data, cls=AlchemyEncoder)

    db_session.close()

    return data_dumped


def get_Beehive(id: int):
    """
    Restituisce il Beehive con l'id passato
    """

    db = Database()
    db_session = db.session
    data = db_session.query(db.beehives).filter(db.beehives.id == id).first()

    data_dumped = json.dumps(data, cls=AlchemyEncoder)

    db_session.close()

    return data_dumped


def get_Users():
    """
    Restituisce gli utenti sul DB
    """
    
    db = Database()
    db_session = db.session
    data = db_session.query(db.user).all()

    data_dumped = json.dumps(data, cls=AlchemyEncoder)

    db_session.close()

    return data_dumped

def get_ApiarysFromUser(username: str):
    """
    Restituisce gli Apiarys del proprietario
    """

    db = Database()
    db_session = db.session
    data = db_session.query(db.apiarys).filter(db.apiarys.owner == username).all()

    data_dumped = json.dumps(data, cls=AlchemyEncoder)

    db_session.close()

    return data_dumped


def get_LastInvoicesToPay(username: str):
    """
    Ritorna le fatture da pagare
    """

    db = Database()
    db_session = db.session
    data = db_session.query(db.invoices).filter(db.invoices.user == username, db.invoices.paid == False).order_by(db.invoices.id.desc()).first()

    data_dumped = json.dumps(data, cls=AlchemyEncoder)

    db_session.close()

    return data_dumped


def get_InvoicesToPay(username: str):
    """
    Ritorna le fatture da pagare
    """

    db = Database()
    db_session = db.session
    data = db_session.query(db.invoices).filter(db.invoices.user == username, db.invoices.paid == False).order_by(db.invoices.id.desc()).all()

    data_dumped = json.dumps(data, cls=AlchemyEncoder)

    db_session.close()

    return data_dumped

def get_Invoice(id: int):
    """
    Ritorna la fattura con l'id passato
    """

    db = Database()
    db_session = db.session
    data = db_session.query(db.invoices).filter(db.invoices.id == id).first()

    data_dumped = json.dumps(data, cls=AlchemyEncoder)

    db_session.close()

    return data_dumped

def get_Invoices(username: str):
    """
    Ritorna le fatture del proprietario
    """

    db = Database()
    db_session = db.session
    data = db_session.query(db.invoices).filter(db.invoices.user == username).all()

    data_dumped = json.dumps(data, cls=AlchemyEncoder)

    db_session.close()

    return data_dumped

def get_AllInvoices():
    """
    Ritorna tutte le fatture
    """

    db = Database()
    db_session = db.session
    data = db_session.query(db.invoices).all()

    data_dumped = json.dumps(data, cls=AlchemyEncoder)

    db_session.close()

    return data_dumped