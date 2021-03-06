from flask import *
from datetime import timedelta
from utils import *
from flask_caching import Cache
from dotenv import dotenv_values

import time
import logging


#Blueprint
from auth.auth import auth
from dashboard.dashboard import dashboard
from admin.admin import admin


config = dotenv_values(".env")

app = Flask(__name__, template_folder='views', static_folder='assets', static_url_path='/assets')
app.secret_key = config['secret_key']
cache = Cache(app,config={'CACHE_TYPE': 'simple'})
#log = logging.getLogger('werkzeug')
#log.setLevel(logging.ERROR)

app.register_blueprint(auth)
app.register_blueprint(dashboard, url_prefix='/dashboard')
app.register_blueprint(admin, url_prefix='/admin')


@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(hours=5)

@app.route('/', methods=['GET', 'POST'])
#@cache.cached(timeout=200)
def index():
    return render_template('index.html')


@app.route('/sitemap.xml', methods=['GET', 'POST'])
def sitemap():
    return send_from_directory(app.static_folder, 'sitemap.xml')

@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('index.html'), 404



def start_site():
    try:
        app.debug = True
        app.run(host='0.0.0.0', port=53057, threaded=True)
    except Exception as e:
        print(e)
        time.sleep(2)
        start_site()

if __name__ == '__main__':
    start_site()