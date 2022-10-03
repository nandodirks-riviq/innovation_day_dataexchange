from flask import Flask, render_template_string, request, make_response
from wtforms import Form, SelectMultipleField
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Table, MetaData
from sqlalchemy.sql import text
import os
import urllib.parse 
import pyodbc
import pandas as pd
from sqlalchemy import create_engine, inspect

app = Flask(__name__)

dbuser=os.environ['DBUSER']
dbpass=os.environ['DBPASS']
dbhost=os.environ['DBHOST']
dbname=os.environ['DBNAME']
params = urllib.parse.quote_plus(f'Driver={{ODBC Driver 17 for SQL Server}};Server=tcp:{dbhost},1433;Database={dbname};Uid={dbuser};Pwd={dbpass}')
conn_str = "mssql+pyodbc:///?odbc_connect=%s" % params

app.config.update(
    SQLALCHEMY_DATABASE_URI = conn_str,
    SQLALCHEMY_TRACK_MODIFICATIONS = False,
)

db = SQLAlchemy(app)

class LanguageForm(Form):
    col_names = db.session.execute("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.columns WHERE TABLE_NAME = 'Address'").all()
    col_names = [str(i)[2:-3] for i in col_names]
    language = SelectMultipleField(u'Desired columns', choices=col_names)
    
class TableForm(Form):
    tables = db.session.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES").all()
    tables = [str(i)[2:-3] for i in tables]
    table = SelectMultipleField(u'Desired table', choices=tables)

template_form = """
{% block content %}
<h1>Set Language</h1>

<form method="POST" action="/">
    <div>{{ form.table.label }} {{ form.table(rows=4, multiple=True) }}</div>
    <button type="submit" class="btn">Submit</button>    
</form>
{% endblock %}

"""

completed_template = """
{% block content %}
<h1>Language Selected</h1>

<div>{{ language }}</div>

{% endblock %}

"""

@app.route('/', methods=['GET', 'POST'])
def index():
    form = TableForm(request.form)

    if request.method == 'POST':
        print("POST request and form is valid")
        cols =  form.table.data

        df = pd.read_sql(f"SELECT * FROM {cols}", db.session.bind)
        resp = make_response(df.to_csv())
        resp.headers["Content-Disposition"] = "attachment; filename=export.csv"
        resp.headers["Content-Type"] = "text/csv"
        return resp
    else:
        return render_template_string(template_form, form=form)
    
    
# @app.route('/', methods=['GET', 'POST'])
# def index():
#     form = LanguageForm(request.form)

#     if request.method == 'POST':
#         print("POST request and form is valid")
#         cols =  form.language.data
#         print("languages in wsgi.py: %s" % request.form['language'])

#         df = pd.read_sql(f"SELECT {', '.join(cols)} FROM SalesLT.Address", db.session.bind)
#         resp = make_response(df.to_csv())
#         resp.headers["Content-Disposition"] = "attachment; filename=export.csv"
#         resp.headers["Content-Type"] = "text/csv"
#         return resp
#     else:
#         return render_template_string(template_form, form=form)

if __name__ == '__main__':
    app.run(debug=True)

