#from recommendations_main import prepare_matrices, get_names_for_recommendations, recommendation
from recommendations_main import get_namespaces_availiable_for_update, get_namespaces_availiable_for_add, download_all_datasets, get_date, recommendation
from flask import Flask, jsonify, render_template
from flask.views import MethodView
from flask import jsonify
from flask import request
import json
from flask_simplelogin import SimpleLogin, get_username, login_required

my_users = {
    'sonya': {'password': 'qwerty', 'roles': ['admin']},
    'aivan': {'password': 'qwerty', 'roles': ['admin']},
    'alena': {'password': 'qwerty', 'roles': ['admin']},
    'nikita': {'password': 'qwerty', 'roles': ['admin']},
    'guest': {'password': 'qwerty', 'roles': []}
}


def check_my_users(user):
    user_data = my_users.get(user['username'])
    if not user_data:
        return False
    elif user_data.get('password') == user['password']:
        return True 

    return False


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret-here'

SimpleLogin(app, login_checker=check_my_users)


@app.route('/')
def index():
    companies = get_namespaces_availiable_for_update()
    search = ['item_based', 'matrix']
    return render_template('index.html', companies = companies, n = len(companies), search=search)

@app.route('/result', methods=['POST'])
def result():
    user_id = (request.form['user_id'])
    if (user_id == ''):
        return 'You need to write your id! <br/>'
    user_id = int(request.form['user_id'])
    company = request.form['company']
    search_type = request.form['search_type']
    number = int(request.form['number'])
    res, name, price, pictures = recommendation(company, search_type, user_id, number)
    if (res == []):
        return render_template('no_result.html', user_id=user_id)
    return render_template('result.html', res = res, name = name, price = price, n = len(res), pictures = pictures)

@app.route('/secret')
@login_required(username=['aivan', 'sonya', 'nikita', 'alena'])
def secret():
    companies = get_namespaces_availiable_for_update()
    dates = get_date(companies)
    return render_template('secret.html', companies=companies, dates=dates, n = len(companies))

@app.route('/update', methods=['POST'])
def update_mat():
    page_ids = request.form.getlist("update_it")
    download_all_datasets(page_ids)
    return render_template('update.html', page_ids = page_ids)

@app.route('/addcomp')
@login_required(username=['aivan', 'sonya', 'nikita', 'alena'])
def addcomp():
    companies = get_namespaces_availiable_for_add()
    return render_template('addcomp.html', companies=companies, n = len(companies))

@app.route('/addcomp2', methods=['POST'])
def addcomp2():
    page_ids = request.form.getlist("add_it")
    download_all_datasets(page_ids)
    return render_template('addcomp2.html', page_ids = page_ids)

@app.route('/api/recommend', methods=['POST'])
def parse_request():
    user_id = int(request.args.get("user_id"))
    company = request.args.get("company")    
    search_type = request.args.get("search_type")
    number = int(request.args.get("number"))
    res, name, price, pictures = recommendation(company, search_type, user_id, number)
    items = []
    for i in range(len(res)):
        item = {'id': res[i], 'name': name[i], 'price': price[i], 'pictures': pictures[i]}
        items.append(item)
    return json.dumps(items)

def be_admin(username):
    """Validator to check if user has admin role"""
    user_data = my_users.get(username)
    if not user_data or 'admin' not in user_data.get('roles', []):
        return "User does not have admin role"


def have_approval(username):
    """Validator: all users approved, return None"""
    return

class ProtectedView(MethodView):
    decorators = [login_required]

    def get(self):
        return "You are logged in as <b>{0}</b>".format(get_username())


app.add_url_rule('/protected', view_func=ProtectedView.as_view('protected'))


if __name__ == '__main__':
    app.run() #for local
    #app.run(host='0.0.0.0', port=5021) #for server
