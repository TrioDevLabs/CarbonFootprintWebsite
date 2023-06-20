from flask import Flask, flash, render_template, request, redirect, url_for, session, jsonify
from flask_mail import Mail, Message
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_pyfile('config.py')

db = SQLAlchemy(app)
mail = Mail(app)

@app.route("/", methods=['GET', 'POST'])
def home_page():
  return render_template('index.html')

@app.errorhandler(404) 
def invalid_route(e): 
    return render_template('page-404.html')

@app.errorhandler(500) 
def invalid_route(e): 
    return render_template('page-500.html')

def exec_app():
    if __name__ == "app.app":
        app.run(debug=True)
