# Cobalt

# Requeriments: 

https://docs.google.com/document/d/1GwNZ4tYGZ7vQrjilLFj2I7rlG0fbWgahn7N9m7REcNU/edit?usp=sharing

## dependencies

- Redis > 3.0.0 `"$ brew install redis"`
- pipenv
  
## start in developing mode

- open console 
- in one tab run redis server `"$ redis-server"`
- open a virtualenv shell session by running `"$ pipenv shell"`
- in another tab `"$ python worker.py"` to run our worker runner
- in a third tab run the app `"$ FLASK_RUN_PORT=4567 FLASK_ENV=development FLASK_APP=app.py flask run"`
- open `"http://localhost:4567"` and login in
- If all works properly a new page will be rendered. `Check repo URL` link checks URL works properly. `get repositories` start job to retrieve up to 5000 repos and save them in DB. 


Check worker console! a message `"hello job!xxxxxxxx"` should shows up where xxxxx is the code to be used for authenticated request to Github Api

## Documentation

https://realpython.com/flask-by-example-implementing-a-redis-task-queue/
https://flask-rq2.readthedocs.io/en/latest/
https://help.github.com/en/github/searching-for-information-on-github/searching-on-github


# Search Example 1

"https://api.github.com/search/repositories?q=php+laravel+in:readme+pushed:>2020-02-10+created:<2020-02-11+language:php+topic:laravel"




