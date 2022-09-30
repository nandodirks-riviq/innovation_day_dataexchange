from flask import Flask
from flask_sqlalchemy import SQLAlchemy
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
    
# @app.route('/query')
# def testquery():
#     try:
#         result = db.session.execute("SELECT * FROM dbo.BuildVersion")
#         return result
#     except Exception as e:
#         return str(e)

if __name__ == '__main__':
    app.run(debug=True)

