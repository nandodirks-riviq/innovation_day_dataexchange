from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Table, MetaData
from sqlalchemy.sql import text
import os
import urllib.parse 
import pyodbc

app = Flask(__name__)

dbuser=os.environ['DBUSER']
dbpass=os.environ['DBPASS']
dbhost=os.environ['DBHOST']
dbname=os.environ['DBNAME']
params = urllib.parse.quote_plus(f'Driver={{ODBC Driver 17 for SQL Server}};Server=tcp:{dbhost},1433;Database={dbname};Uid={dbuser};Pwd={dbpass}')

app.config.update(
    SQLALCHEMY_DATABASE_URI = "mssql+pyodbc:///?odbc_connect=%s" % params,
    SQLALCHEMY_TRACK_MODIFICATIONS = False,
)

db = SQLAlchemy(app)

@app.route('/')
def testdb():
    try:
        db.session.query(text('1')).from_statement(text('SELECT 1')).all()
        return f'<h1>It works.</h1>'
    except Exception as e:
        # e holds description of the error
        error_text = "<p>The error:<br>" + str(e) + "</p>"
        hed = '<h1>Something is broken.</h1>'
        return hed + error_text
    
@app.route('/query')
def testdb2():
    try:
        md = MetaData()
        table = Table("dbo.BuildVersion", md, autoload=True, autoload_with=db)
        column_names  = [c.name for c in table.columns]
        return f'<h1>{column_names}</h1>'
    except Exception as e:
        return "<p>The error:<br>" + str(e) + "</p>"

if __name__ == '__main__':
    app.run(debug=True)

