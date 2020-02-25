import os 
from flask import request, session, Flask, render_template, jsonify
from flask_rq2 import RQ
from flask_github import GitHub
from datetime import date
import requests
import json
from datetime import date, timedelta


app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY") or os.urandom(24)
app.config['GITHUB_CLIENT_ID'] = os.environ.get("GITHUB_CLIENT_ID")
app.config['GITHUB_CLIENT_SECRET'] = os.environ.get("GITHUB_CLIENT_SECRET")

github = GitHub(app)
rq = RQ(app) 
repos_url = "https://api.github.com/search/repositories"
users_url = "https://api.github.com/search/users"

@rq.job
def my_hello_job(oauth_token):
    return 'job running....'

@rq.job
def simple_get_repos(oauth_token, search_query):
    total_repos = []
    number_of_request = 0
    headers = {'Authorization': f'token {oauth_token}', 'User-Agent': 'digitalents-cobalt'}
    query = f'{search_query}'
    url = f'{repos_url}?{query}'
    res = requests.get(url=f'{url}&page=1',headers=headers)
    repos_per_day = res.json()['items']
    while 'next' in res.links.keys():
        res = requests.get(res.links['next']['url'], headers=headers)
        number_of_request = number_of_request + 1
        # print('status', res.status_code, res.headers)
        repos = res.json()['items']
        repos_per_day += repos
    print(repos_per_day)
    ## set it DB or wait for results! 
    return repos_per_day

@rq.job
def simple_get_users(oauth_token, search_query):
    headers = {'Authorization': f'Bearer {oauth_token}', 'User-Agent': 'digitalents-cobalt'}
    final_url = f'{users_url}?q={search_query}&per_page=100'
    res=requests.get(url=f'{final_url}&page=1',headers=headers)
    # print('status', headers, final_url, res.json())
    if 'items' in res.json():
        total_repos = res.json()['items']
        while 'next' in res.links.keys():
            res=requests.get(res.links['next']['url'], headers=headers)
            print('status', res.status_code, res.headers)
            total_repos += res.json()['items']
        print('total', total_repos)

## @depreacted
@rq.job
def get_repositories_job(oauth_token, search_query):
    delta = 1
    total_repos = []
    number_of_request = 0
    headers = {'Authorization': f'token {oauth_token}', 'User-Agent': 'digitalents-cobalt'}
    while delta < 30:
        # define new query by timerange
        since = date.today() - timedelta(days=delta)
        until = date.today() - timedelta(days=delta-1)
        query = f'{search_query}+pushed:>{since}+created:<{until}'
        final_url = f'{repos_url}?{query}'

        res=requests.get(url=f'{final_url}&page=1',headers=headers)
        number_of_request = number_of_request + 1
        print('status', res.status_code, res.headers)
        json_response = res.json()
        total_repos_day = json_response['items']
        # when pagination...
        while 'next' in res.links.keys():
            res=requests.get(res.links['next']['url'], headers=headers)
            number_of_request = number_of_request + 1
            print('status', res.status_code, res.headers)
            json_response = res.json()
            repos = json_response['items']
            total_repos_day += repos
        total_repos += total_repos_day        
        delta = delta + 1
    print('total', len(total_repos), number_of_request)
    

@app.route('/api/start_users_job')
def get_users():
    try:
        access_token = request.args.get('access_token')
        search_query = request.args.get('search_query')
        job = simple_get_users.queue(access_token, search_query)
    except Exception as e:
         return f'Record not found {e}', 400
    return json.dumps({'success':True}), 200, {'ContentType':'application/json'}

@app.route('/api/start_repositories_job')
def get_repositories():
    try:
        access_token = request.args.get('access_token')
        search_query = request.args.get('search_query')
        delta = 1
        # get last 30 days repos
        while delta < 30:
            since = date.today()  - timedelta(days=delta)
            until = date.today()  - timedelta(days=delta-1)
            query = f'{search_query}+pushed:>{since}+created:<{until}'
            # schedule a job each minute
            job = simple_get_repos.schedule(timedelta(minutes=1), access_token, query)
    except Exception as e:
         return f'Record not found {e}', 400
    return json.dumps({'success':True}), 200, {'ContentType':'application/json'}
    
@app.route('/')
def index():
    return render_template('index.html')

@github.access_token_getter
def token_getter():
    return session['oauth_token']

@app.route('/api/check-repo-url')
def repo():
    today = date.today()
    delta = 2
    oauth_token = session['oauth_token']
    headers = {'Authorization': f'token {oauth_token}', 'User-Agent': 'digitalents-cobalt'}

    since = today - timedelta(days=delta)
    until = today - timedelta(days=delta-1)
    query = f'q=php+laravel+in:readme+pushed:>{since}+created:<{until}+language:php+topic:laravel'
    url = f'{repos_url}?{query}'
    print(url)
    res=requests.get(url=f'{url}&page=1',headers=headers)
    json_response = res.json()
    total_repos = json_response['items']
    while 'next' in res.links.keys():
        res=requests.get(res.links['next']['url'], headers=headers)
        json_response = res.json()
        repos = json_response['items']
    print(len(total_repos))
    return render_template('auth.html')



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