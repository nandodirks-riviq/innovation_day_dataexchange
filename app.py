from flask import Flask, render_template_string, request, make_response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Table, MetaData
from sqlalchemy.sql import text
import os
import urllib.parse 
import pyodbc
import pandas as pd

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

def get_meta_data():
    meta_dict = {}
    tables = get_tables()
    for i in tables:
        cols = get_columns(i)
        meta_dict[i] = cols
    return meta_dict

def get_columns(table):
    col_names = db.session.execute(f"SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.columns WHERE TABLE_NAME = {table}").all()
    col_names = [str(i)[2:-3] for i in col_names]
    return col_names
    
def get_tables():
    tables = db.session.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES").all()
    tables = [str(i)[2:-3] for i in tables]
    return tables

# template_form = """
# {% block content %}
# <h1>Set Language</h1>

# <form method="POST" action="/">
#     <div>{{ form.table.label }} {{ form.table(rows=4, multiple=True) }}</div>
#     <button type="submit" class="btn">Submit</button>    
# </form>
# {% endblock %}

# """

# completed_template = """
# {% block content %}
# <h1>Language Selected</h1>

# <div>{{ language }}</div>

# {% endblock %}

# """

# @app.route('/', methods=['GET', 'POST'])
# def index():
#     form = TableForm(request.form)

#     if request.method == 'POST':
#         print("POST request and form is valid")
#         cols =  form.table.data

#         df = pd.read_sql(f"SELECT * FROM {cols}", db.session.bind)
#         resp = make_response(df.to_csv())
#         resp.headers["Content-Disposition"] = "attachment; filename=export.csv"
#         resp.headers["Content-Type"] = "text/csv"
#         return resp
#     else:
#         return render_template_string(template_form, form=form)
    
    
# # @app.route('/', methods=['GET', 'POST'])
# # def index():
# #     form = LanguageForm(request.form)

# #     if request.method == 'POST':
# #         print("POST request and form is valid")
# #         cols =  form.language.data
# #         print("languages in wsgi.py: %s" % request.form['language'])

# #         df = pd.read_sql(f"SELECT {', '.join(cols)} FROM SalesLT.Address", db.session.bind)
# #         resp = make_response(df.to_csv())
# #         resp.headers["Content-Disposition"] = "attachment; filename=export.csv"
# #         resp.headers["Content-Type"] = "text/csv"
# #         return resp
# #     else:
# #         return render_template_string(template_form, form=form)


@app.route('/')
def index():
    systems = get_meta_data()

    return render_template_string(template, systems=systems)

template = """
<!doctype html>
<form>
    <select id="system">
        <option></option>
    </select>
    <select id="game"></select>
    <button type="submit">Play</button>
</form>
<script src="//code.jquery.com/jquery-2.1.1.min.js"></script>
<script>
    "use strict";

    var systems = {{ systems|tojson }};

    var form = $('form');
    var system = $('select#system');
    var game = $('select#game');

    for (var key in systems) {
        system.append($('<option/>', {'value': key, 'text': key}));
    }

    system.change(function(ev) {
        game.empty();
        game.append($('<option/>'));

        var games = systems[system.val()];

        for (var i in games) {
            game.append($('<option/>', {'value': games[i], 'text': games[i]}));
        }
    });

    form.submit(function(ev) {
        ev.preventDefault();
        alert("playing " + game.val() + " on " + system.val());
    });
</script>
"""
if __name__ == '__main__':
    app.run(debug=True)
