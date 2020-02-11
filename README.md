# Cobalt

## dependencies

- Redis > 3.0.0 `"$ brew install redis"`
- pipenv
  
## start in developing mode

- open console 
- in one tab run redis server `"$ redis-server"`
- in another tab `"$ python worker"` to run our worker runner
- in a third tab run the app `"$ FLASK_RUN_PORT=4567 FLASK_ENV=development FLASK_APP=app.py flask run"`

### Next...

1 - **authoriziation step**: open browser and paste `http;//localhost:4567/api/login` a github oauth page should popup asking to grant access you will be redirected to `/api/callback`

2 - **run job**: open another browser tab and run `http://localhost:4567/hello-job` a message `job should run now` appears. 

Check worker console! a message `"hello job!xxxxxxxx"` should shows up where xxxxx is the code to be used for authenticated request to Github Api

