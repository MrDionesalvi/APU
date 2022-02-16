import json
import html
import string
import random
import requests


from utils import *
from flask import *
from create_invoices import *
from sqlalchemy.sql.elements import *
from database import Database
from datetime import date
from dateutil.relativedelta import relativedelta

admin = Blueprint('admin', __name__, template_folder='views', static_folder='assets', static_url_path='/assets')


def datetoPrint():
    return date.today().strftime("%d/%m/%Y")

@admin.route('/')
@is_member
@is_admin
def index():
    return render_template('admin.html', date = datetoPrint())


@admin.route('/players')
@is_member
@is_admin
def players():
    data = {
        'players': ''
    }
    users = get_Users()
    for i in json.loads(users):
        invoices = json.loads(get_LastInvoicesToPay(i['username']))
        data['players'] += f"""
                <tr>
                    <td class="id">{i['id']}</td>
                    <td class="name">{i['username']}</td>
                    <td class="member">{"Sì" if int(i['member']) == 1 else "No"}</td>
                    <td class="occuped">{"Sì" if int(i['admin']) == 1 else "No"}</td>
                    <td class="invoices">{"Si" if invoices != "[]" and invoices != None else "No"}</td>
                    <td class="buttons">
                        <button value="{i['id']}" class="remove-item-btn button is-danger is-small" onclick="DeleteButton(this)">Elimina User</button>
                        <button value="{i['id']}" class="change-item-btn button is-warning is-small" onclick="ChangeButton(this)">Toggle Membro</button>
                    </td>
                </tr>
        """
    return render_template('players.html', data=data, date=datetoPrint())





@admin.route('/beehives')
@is_member
@is_admin
def beehives():
    data = {
        'beehives': ''
    }
    beehives = get_AllBeehives()

    for i in json.loads(beehives):
        type_bee = {
            'common_bees': 0,
            'precious_bees': 0,
            'mineral_bees': 0,
            'nether_bees': 0
        }
        apiarys = get_Apiarys(i['id'])
        for j in json.loads(apiarys):
            if j['typeBee'] == '0':
                type_bee['common_bees'] += 1
            elif j['typeBee'] == '1':
                type_bee['precious_bees'] += 1
            elif j['typeBee'] == '2':
                type_bee['mineral_bees'] += 1
            elif j['typeBee'] == '3':
                type_bee['nether_bees'] += 1

        data['beehives'] += f"""
                <tr>
                    <td class="id">{i['id']}</td>
                    <td class="owner">{i['owner']}</td>
                    <td class="name">{i['name']}</td>
                    <td class="x_coord">{i['x_coords']}</td>
                    <td class="z_coord">{i['z_coords']}</td>
                    <td class="doc">{i['doc']}</td>
                    <td class="bees">Comuni: {type_bee['common_bees']} Preziose: {type_bee['precious_bees']} Minerali: {type_bee['mineral_bees']} Nether: {type_bee['nether_bees']}</td>
                    <td class="buttons">
                        <button value="{i['id']}" class="remove-item-btn button is-danger is-small" onclick="DeleteButton(this)">Elimina Beehives</button>
                        <button value="{i['id']}" class="change-item-btn button is-warning is-small" onclick="ChangeButton(this)">Modifica Beehives</button>
                    </td>
                </tr>
        """
    return render_template('beehives.html', data=data, date=datetoPrint())    


@admin.route('/deleteMember')
@is_member
@is_admin
def deleteMember():
    user_id = request.args.get('user')
    if user_id:
        user_id = html.escape(user_id)
        db = Database()
        db_session = db.session
        data = db.session.query(db.user).filter(db.user.id == user_id).first()
        if data:
            db_session.delete(data)
            db_session.commit()
        db_session.close()
        return redirect(url_for('admin.players'))
    return redirect(url_for('admin.players'))


@admin.route('/changeMember')
@is_member
@is_admin
def changeMember():
    user_id = request.args.get('user')
    if user_id:
        user_id = html.escape(user_id)
        db = Database()
        db_session = db.session
        data = db.session.query(db.user).filter(db.user.id == user_id).first()
        if data.member == 1:
            data.member = 0
        else:
            data.member = 1
        db_session.commit()
        db_session.close()
        return redirect(url_for('admin.players'))
    return redirect(url_for('admin.players'))

@admin.route('/deleteBeehive')
@is_member
@is_admin
def deleteBeehive():
    beehive_id = request.args.get('beehive')
    if beehive_id:
        beehive_id = html.escape(beehive_id)
        db = Database()
        db_session = db.session
        data = db_session.query(db.beehives).filter(db.beehives.id == beehive_id).first()
        if data:
            db_session.delete(data)
            db_session.commit()
        db_session.close()
        return redirect(url_for('admin.beehives'))
    return redirect(url_for('admin.beehives'))


@admin.route('/invoices')
@is_member
@is_admin
def invoices():
    data = {
        'invoices': ''
    }
    invoices = get_AllInvoices()
    for i in json.loads(invoices):
        data['invoices'] += f"""
                <tr>
                    <td class="id">{i['id']}</td>
                    <td class="user">{i['user']}</td>
                    <td class="ammount">{i['ammount']}</td>
                    <td class="doc">{i['date']}</td>
                    <td class="paid">{"Si" if i['paid'] else "<b>No</b>"}</td>
                    <td class="buttons">
                        <button value="{i['id']}" class="remove-item-btn button is-danger is-small" onclick="DeleteButton(this)">Elimina Fattura</button>
                        <button value="{i['id']}" class="change-item-btn button is-warning is-small" onclick="ChangeButton(this)">Modifica Fattura</button>
                    </td>
                </tr>
        """
    return render_template('invoices.html', data=data, date=datetoPrint())

@admin.route('/deleteInvoice')
@is_member
@is_admin
def deleteInvoice():
    invoice_id = request.args.get('invoice')
    if invoice_id:
        invoice_id = html.escape(invoice_id)
        db = Database()
        db_session = db.session
        data = db_session.query(db.invoices).filter(db.invoices.id == invoice_id).first()
        if data:
            db_session.delete(data)
            db_session.commit()
        db_session.close()
        return redirect(url_for('admin.invoices'))
    return redirect(url_for('admin.invoices'))



@admin.route('/settings')
@is_member
@is_admin
def settings():
    return render_template('settings.html', date=datetoPrint())