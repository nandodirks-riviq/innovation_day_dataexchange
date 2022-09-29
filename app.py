from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text
import os

app = Flask(__name__)

dbuser=os.environ['DBUSER'],
dbpass=os.environ['DBPASS'],
dbhost=os.environ['DBHOST'],
dbname=os.environ['DBNAME']
cstr = 'DRIVER={ODBC Driver 13 for SQL Server};SERVER='+dbhost+';DATABASE='+dbname+';UID='+dbuser+';PWD='+ dbpass

app.config.update(
    SQLALCHEMY_DATABASE_URI = cstr,
    SQLALCHEMY_TRACK_MODIFICATIONS = False,
)

db = SQLAlchemy(app)

@app.route('/')
def testdb():
    try:
        db.session.query(text('1')).from_statement(text('SELECT 1')).all()
        return '<h1>It works.</h1>'
    except Exception as e:
        # e holds description of the error
        error_text = "<p>The error:<br>" + str(e) + "</p>"
        hed = '<h1>Something is broken.</h1>'
        return hed + error_text

if __name__ == '__main__':
    app.run(debug=True)
