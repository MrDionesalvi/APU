from utils import *
from database import Database
from datetime import date
import html
import json



def create_Allinvoice():
    users = get_Users()

    today = date.today()
    datetoPrint = today.strftime('%d-%m-%Y')

    for i in json.loads(users):
        data = {
            'common_bees': 0,
            'precious_bees': 0,
            'mineral_bees': 0,
            'nether_bees': 0,
            'price_bees': 0
        }
        user = i['username']
        user_apiarys = get_ApiarysFromUser(user)
        for j in json.loads(user_apiarys):
            if int(j['typeBee']) == 0:
                data['common_bees'] += 1
            elif int(j['typeBee']) == 1:
                data['precious_bees'] += 1
            elif int(j['typeBee']) == 2:
                data['mineral_bees'] += 1
            elif int(j['typeBee']) == 3:
                data['nether_bees'] += 1
        
        taxesToPay = count_taxes(data['common_bees'], data['precious_bees'], data['mineral_bees'], data['nether_bees'])

        if taxesToPay > 0:
            db = Database()
            db_session = db.session
            db_session.add(db.invoices(user = user, date = datetoPrint, ammount = taxesToPay))
            print(user, datetoPrint, taxesToPay)
            db_session.commit()
            db.session.close()


def create_invoice(user):
    today = date.today()
    datetoPrint = today.strftime('%d-%m-%Y')

    data = {
        'common_bees': 0,
        'precious_bees': 0,
        'mineral_bees': 0,
        'nether_bees': 0,
        'price_bees': 0
    }
    user_apiarys = get_ApiarysFromUser(user)
    for j in json.loads(user_apiarys):
        if int(j['typeBee']) == 0:
            data['common_bees'] += 1
        elif int(j['typeBee']) == 1:
            data['precious_bees'] += 1
        elif int(j['typeBee']) == 2:
            data['mineral_bees'] += 1
        elif int(j['typeBee']) == 3:
            data['nether_bees'] += 1

    taxesToPay = count_taxes(data['common_bees'], data['precious_bees'], data['mineral_bees'], data['nether_bees'])

    if taxesToPay > 0:
        db = Database()
        db_session = db.session
        db_session.add(db.invoices(user = user, date = datetoPrint, ammount = taxesToPay))
        print(user, datetoPrint, taxesToPay)
        db_session.commit()
        db.session.close()

if __name__ == '__main__':
    create_Allinvoice()