import os 
import requests
import json
from flask import request, session, Flask, render_template, jsonify
from datetime import date
from datetime import date, timedelta
# github support
from flask_github import GitHub
# database support
from flask_sqlalchemy import SQLAlchemy 
from flask_migrate import Migrate
from sqlalchemy.dialects.postgresql import JSON
# rq support
from flask_rq2 import RQ

## constants 
REPOS_URL = "https://api.github.com/search/repositories"
USERS_URL = "https://api.github.com/search/users"

## App set up 
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY") or os.urandom(24)
app.config['GITHUB_CLIENT_ID'] = os.environ.get("GITHUB_CLIENT_ID")
app.config['GITHUB_CLIENT_SECRET'] = os.environ.get("GITHUB_CLIENT_SECRET")
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

github = GitHub(app)
rq = RQ(app) 

## Models ####
class UserRepo(db.Model):
    __tablename__ = 'user_repos'
    id = db.Column(db.Integer, primary_key=True)
    repo = db.Column(JSON, nullable=False)
    searches = db.relationship('Search', backref='user_repo', lazy=True)

    def __init__(self, payload):
        self.payload = payload

    def __repr__(self):
        return '<User %r>' % self.payload


class Search(db.Model):
    __tablename__ = 'searches'
    id = db.Column(db.Integer, primary_key=True)
    search = db.Column(db.String, unique=False, nullable=False)
    user_repo_id = db.Column(db.Integer, db.ForeignKey('user_repo.id'),
        nullable=False)

    def __init__(self, search):
        self.search = search

    def __repr__(self):
        return '<Search %r>' % self.search

## Jobs definition ###

def save_repos_in_db(items, search):
    for item in items:
        user_repo = UserRepo(repo=item, search=search)

@rq.job
def simple_get_users(oauth_token, search_query):
    headers = {'Authorization': f'Bearer {oauth_token}', 'User-Agent': 'digitalents-cobalt'}
    final_url = f'{USERS_URL}?q={search_query}&per_page=100'
    res=requests.get(url=f'{final_url}&page=1',headers=headers)
    # print('status', headers, final_url, res.json())
    search = Search(search=search_query)
    db.session.add(search)
    # if 'items' in res.json():
    #    save_repos_in_db(res.json()['items'], search)
    #    while 'next' in res.links.keys():
    #        res=requests.get(res.links['next']['url'], headers=headers)
    #        print('status', res.status_code, res.headers)
            # total_repos += res.json()['items']
    #        save_repos_in_db(res.json()['items'], search)
    db.session.commit()


## Routes and auth management #### 

@github.access_token_getter
def token_getter():
    return session['oauth_token']

@app.route('/api/start_users_job')
def get_users():
    try:
        access_token = request.args.get('access_token')
        search_query = request.args.get('search_query')
        job = simple_get_users.queue(access_token, search_query)
    except Exception as e:
         return f'Record not found {e}', 400
    return json.dumps({'success':True}), 200, {'ContentType':'application/json'}
    
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/login')
def login():
    return github.authorize()

@app.route('/api/callback')
@github.authorized_handler
def authorized(oauth_token):
    if oauth_token is not None:
        session['oauth_token'] = oauth_token
    else:
        print('something went wrong')
    return session['oauth_token']

@app.route('/auth')
def template_auth():
    return render_template('auth.html', oauth_token=session['oauth_token'])