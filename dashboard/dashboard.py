import json
import html
import string
import random
import requests


from utils import *
from create_invoicePDF import create_invoice
from flask import *
from sqlalchemy.sql.elements import *
from database import Database
from datetime import date
from dateutil.relativedelta import relativedelta

dashboard = Blueprint('dashboard', __name__, template_folder='views', static_folder='assets', static_url_path='/assets')

typeOfBees = {
    0: "Comune",
    1: "Preziosa",
    2: "Minerale",
    3: "Nether"
}

def getInfo_dashboard(ids=-1):

    today = date.today()
    datetoPrint = today.strftime('%d-%m-%Y')
    
    invoices = json.loads(get_LastInvoicesToPay(session['username']))

    beehives = get_Beehives(session['username'])

    data = {
        "datetoPrint": datetoPrint,
        "tree": "",
        "tree_notCollapsed": "",
        "selector": "",
        "selector2": "",
    }

    for i in json.loads(beehives):
        apiarys_print = ""
        apiarys = get_Apiarys(i['id'])
        if apiarys != "[]":
            for j in json.loads(apiarys):
                apiarys_print += f""" <li>AL-{j['id']}</li> """ 
                data["selector2"] += f""" <option value="{j['id']}">AL-{j['id']}</option> """

        data["tree"] += f"""
                    <li>
                        <a href="/dashboard/view/{i['id']}" class="{'is-active' if ids != -1 and ids == i['id'] else ''}"><i class="fas fa-project-diagram"></i>&nbsp;&nbsp;{i['name']}</a>
                            <ul>
                                {apiarys_print}
                            </ul>
                    </li>
                """
        data["tree_notCollapsed"] += f"""
                    <li>
                        <a href="/dashboard/view/{i['id']}" class="{'is-active' if ids != -1 and ids == i['id'] else ''}"><i class="fas fa-project-diagram"></i>&nbsp;&nbsp;{i['name']}</a>
                    </li>
                """
        data["selector"] += f"""
                    <option value={i['id']}>{i['name']}</option>
                    """

    if invoices != "[]" and invoices != None:
        data["invoices"] = f"""
                            <p><i class="fas fa-exclamation-triangle" style="color:red"></i> Fattura da pagare! <i class="fas fa-exclamation-triangle" style="color:red"></i></p>
                            <p>Devi pagare: {invoices["ammount"]}IC</p>
                            <p>Fattura emessa: {invoices["date"]}</p>
                            <a href="/dashboard/payInvoices"><button class="button is-success is-small">Paga!</button></a>
        """
    else:
        data["invoices"] = """ <p>Nessuna fattura da mostrare!</p>\n <a href="/dashboard/payInvoices"><button class="button is-success is-small">Vedi le tue ultime fatture!</button></a>"""

   
    return data

def getInfo_beehive(ids):
    info = get_Beehive(ids)
    info = json.loads(info)

    allApiarys = get_Apiarys(ids)
    allApiarys = json.loads(allApiarys)

    data = {
        'id': info['id'],
        'name' : info['name'],
        'doc': info['doc'],
        'x_coords' : info['x_coords'],
        'z_coords' : info['z_coords'],
        'common_bees': 0,
        'precious_bees': 0,
        'mineral_bees': 0,
        'nether_bees': 0,
        'price_bees': 0,
    }
    if info != None:
        if info['owner'] != session['username']:
            return "error"

        for i in allApiarys:
            if int(i['typeBee']) == 0:
                data['common_bees'] += 1
            elif int(i['typeBee']) == 1:
                data['precious_bees'] += 1
            elif int(i['typeBee']) == 2:
                data['mineral_bees'] += 1
            elif int(i['typeBee']) == 3:
                data['nether_bees'] += 1

        data['price_bees'] = count_taxes(data['common_bees'], data['precious_bees'], data['mineral_bees'], data['nether_bees'])


        return data
    return "error"


@dashboard.route('/', methods=['GET', 'POST'])
@login_required
@is_member
def index():
    data = getInfo_dashboard()

    return render_template('dashboard.html', date=data["datetoPrint"], tree=data["tree_notCollapsed"], selector=data["selector"], selector2=data["selector2"], invoice=data["invoices"])

@dashboard.route('/view/<int:ids>')
@login_required
@is_member
def view(ids):
    data = getInfo_dashboard(ids)
    infoBeehive = getInfo_beehive(ids)

    if infoBeehive == "error":
        return render_template('error.html', error="Stai provando a fare qualcossa che non puoi fare")

    return render_template('dashboard.html', date=data["datetoPrint"], tree=data["tree"], selector=data["selector"], selector2=data["selector2"], invoice=data["invoices"], info=infoBeehive)

@dashboard.route('/notMember')
def notMember():
    return render_template('notMember.html')

@dashboard.route('/add/beehive', methods=['GET', 'POST'])
@login_required
@is_member
def add_beehive():
    if request.method == 'POST':
        name = request.form['name']
        x_coords = request.form['x_coords']
        z_coords = request.form['z_coords']

        name = html.escape(name)
        x_coords = html.escape(x_coords)
        z_coords = html.escape(z_coords)

        if name == '' or x_coords == '' or z_coords == '':
            return render_template('dashboard.html', error='Mancano dei dati!.')
        
        name = name[:20]
        x_coords = x_coords[:20]
        z_coords = z_coords[:20]

        today = date.today()
        datetoPrint = today.strftime('%d-%m-%Y')

        db = Database()
        db_session = db.session

        db_session.add(db.beehives(owner=session['username'], name=name, x_coords=x_coords, z_coords=z_coords, doc=datetoPrint))
        db_session.commit()

        db_session.close()

        return redirect(url_for('dashboard.index'))
    return render_template('dashboard.html')

@dashboard.route('/add/apiary', methods=['GET', 'POST'])
@login_required
@is_member
def add_apiery():
    if request.method == 'POST':
        typeBees = request.form['type']
        idBeehive = request.form['idBeehive']
        ammountBees = request.form['ammount']

        typeBees = html.escape(typeBees)
        idBeehive = html.escape(idBeehive)
        ammountBees = html.escape(ammountBees)

        if typeBees == '' or idBeehive == '':
            return render_template('dashboard.html', error='Mancano dei dati!.')
        if int(idBeehive) < 0 and int(idBeehive) > 3:
            return render_template('dashboard.html', error='ID beehive non valido!.')
        if int(ammountBees) < 1 or int(ammountBees) > 10:
            return render_template('dashboard.html', error='Quantità API non valida!.')

        db = Database()
        db_session = db.session

        if int(ammountBees) == 1:
            db_session.add(db.apiarys(owner=session['username'], idBeehive=idBeehive, typeBee=typeBees))
        else:
            for i in range(0, int(ammountBees)):
                db_session.add(db.apiarys(owner=session['username'], idBeehive=idBeehive, typeBee=typeBees))
        
        db_session.commit()

        db_session.close()

        return redirect(url_for('dashboard.index'))
    return render_template('dashboard.html')


@dashboard.route('/delete/beehive', methods=['GET', 'POST'])
@login_required
@is_member
def delete_beehive():
    if request.method == 'POST':
        id = request.form['idBeehive']
        id = html.escape(id)

        if int(id) < 0:
            return render_template('dashboard.html', error='ID beehive non valido!.')

        db = Database()
        db_session = db.session

        beehive = db_session.query(db.beehives).filter_by(id=id).first()
        if beehive.owner == session['username']:
            db_session.delete(beehive)
            db_session.commit()

            allApiarys = get_Apiarys(id)
            allApiarys = json.loads(allApiarys)

            if allApiarys != None and allApiarys != "[]":
                for i in allApiarys:
                    apiarys = db_session.query(db.apiarys).filter_by(id=i['id']).first()
                    db_session.delete(apiarys)
                    db_session.commit()

        db_session.close()

        return redirect(url_for('dashboard.index'))

@dashboard.route('/delete/apiary', methods=['GET', 'POST'])
@login_required
@is_member
def delete_apiary():
    if request.method == 'POST':
        id = request.form['idApiary']
        id = html.escape(id)


        if int(id) < 0:
            return render_template('dashboard.html', error='ID apiary non valido!.')

        db = Database()
        db_session = db.session

        apiary = db_session.query(db.apiarys).filter_by(id=id).first()
        if apiary.owner == session['username']:
            db_session.delete(apiary)
            db_session.commit()

        db_session.close()

        return redirect(url_for('dashboard.index'))


def get_InfoInvoices():
    today = date.today()
    datetoPrint = today.strftime('%d-%m-%Y')

    data = ""

    invoices = get_Invoices(session['username'])
    for i in json.loads(invoices):
        link = "/dashboard/payInvoices/" + str(i['id'])
        data += f"""
                <tr>
                    <td class="id">{i['id']}</td>
                    <td class="user">{i['user']}</td>
                    <td class="ammount">{i['ammount']} IC</td>
                    <td class="doc">{i['date']}</td>
                    <td class="paid">{"Sì" if i['paid'] == True else "<b>No</b>"}</td>
                    <td class="buttons">
                        <a href="{link if i['paid'] == False else '#'}"><button value="{i['id']}" class="success-item-btn button {'is-success' if i['paid'] == False else 'disabled'} is-small " style="height: 10%; width:100%">{'Paga Fattura' if i['paid'] == False else 'Pagata'}</button></a>
                        {'<a href="/dashboard/downloadInvoices/' + str(i['id']) + '"><button value="' + str(i['id']) + '" class="success-item-btn button is-small is-success" style="height: 10%; width:100%">Scarica Fattura</button></a>' if i['paid'] == True else ''}
                    </td>
                </tr>
        """
    return datetoPrint, data

@dashboard.route('/payInvoices')
@login_required
@is_member
def payInvoices():
    data = {
        'invoices': ''
    }

    datetoPrint, data['invoices'] = get_InfoInvoices()

    return render_template('payInvoices.html', data=data, date=datetoPrint)


@dashboard.route('/payInvoices/<int:id>')  
@login_required
@is_member
def payInvoices_id(id):
    invoice = json.loads(get_Invoice(id))
    print(invoice)

    if invoice['user'] == session['username']:
        if invoice['paid'] == False:
            data = {
                'invoices': ''
            }
            datetoPrint, data['invoices'] = get_InfoInvoices()
            try:
                response = requests.get(f'https://sunfire.a-centauri.com/npayapi/?richiesta=trasferimento&utente={session["username"]}&auth={session["password"]}&valore={int(invoice["ammount"])}&beneficiario=mrdionesalvi', timeout=3).json()
                if response['status'] == 200:
                    create_invoice(invoice['id'], session['username'], invoice['ammount'], invoice['date'])
                    invoice_Id = str(invoice['id'])
                    file = "/home/dionesalvi/public_html/APU/assets/invoices/result_"+invoice_Id+".pdf"
                    db = Database()
                    db_session = db.session

                    invoice = db_session.query(db.invoices).filter_by(id=id).first()
                    invoice.paid = True
                    db_session.commit()

                    db_session.close()
                    message = 'Transazione completata!'
                    #return send_file(file, as_attachment=True)
                    return render_template('payInvoices.html', date=datetoPrint, data=data, message=message, message_type='is-success')
                else:
                    message_type = 'is-danger'
                    message = 'C\'è stato un problema con la transazione. Riprova più tardi.'
                    return render_template('payInvoices.html', date=datetoPrint, data=data, message=message, message_type=message_type)
            except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout):
                message_type = 'is-danger'
                message = 'Impossibile contattare i server per effettuare la transazione! Riprova più tardi.'

                return render_template('payInvoices.html', date=datetoPrint, data=data, message=message, message_type=message_type)
        else:
            return redirect(url_for('dashboard.payInvoices'))
    
    return redirect(url_for('dashboard.payInvoices'))


@dashboard.route('/downloadInvoices/<int:id>')
@login_required
@is_member
def downloadInvoices(id):
    id = html.escape(str(id))
    invoice = json.loads(get_Invoice(id))
    print(invoice)

    try:
        if invoice['user'] == session['username']:
            if invoice['paid'] == True:
                try:
                    file = "/home/dionesalvi/public_html/APU/assets/invoices/result_"+str(invoice['id'])+".pdf"
                    return send_file(file, as_attachment=True)
                except:
                    return redirect(url_for('dashboard.payInvoices'))
            else:
                return redirect(url_for('dashboard.payInvoices'))
    except:
        return redirect(url_for('dashboard.payInvoices'))
    
    return redirect(url_for('dashboard.payInvoices'))