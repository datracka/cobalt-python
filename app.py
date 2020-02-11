import os 
from flask import request, session, redirect, Flask, url_for
from flask_rq2 import RQ
from flask_github import GitHub

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY") or os.urandom(24)
app.config['GITHUB_CLIENT_ID'] = os.environ.get("GITHUB_CLIENT_ID")
app.config['GITHUB_CLIENT_SECRET'] = os.environ.get("GITHUB_CLIENT_SECRET")

github = GitHub(app)
rq = RQ(app)

@rq.job
def my_hello_job(oauth_token):
    print('hello job!', oauth_token)
    return 'hello job!'

@app.route('/hello-job')
def hello_world():
    job = my_hello_job.queue(session['oauth_token'])
    print(job.get_id())
    return f'job should run now'

@app.route('/api/login')
def login():
    return github.authorize()

@app.route('/')
def hello():
    return 'hello world!'

@app.route('/api/callback')
@github.authorized_handler
def authorized(oauth_token):
    if oauth_token is not None:
        session['oauth_token'] = oauth_token
    else:
        print('something went wrong')
    return 'github auth succesful'