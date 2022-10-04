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
    tables, schema_tables = get_tables()
    for i, table in enumerate(tables):
        cols = get_columns(table)
        meta_dict[schema_tables[i]] = cols
    return meta_dict

def get_columns(table):
    col_names = db.session.execute(f"SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.columns WHERE TABLE_NAME = '{table}'").all()
    col_names = [str(i)[2:-3] for i in col_names]
    return col_names
    
def get_tables():
    tables = db.session.execute("SELECT TABLE_SCHEMA, TABLE_NAME FROM INFORMATION_SCHEMA.TABLES").all()
    print(tables)
    tables = [str(i[1])[2:-3] for i in tables]
    schema_tables = ['.'.join(i) for i in tables]
    return tables, schema_tables

@app.route('/', methods =["GET", "POST"])
def index():
    if request.method == "POST":
        req_table = request.form.get('table')
        req_cols = request.form.getlist('cols')
        
        df = pd.read_sql(f"SELECT {', '.join(req_cols)} FROM {req_table}", db.session.bind)
        resp = make_response(df.to_csv())
        resp.headers["Content-Disposition"] = "attachment; filename=export.csv"
        resp.headers["Content-Type"] = "text/csv"
        return resp
    else:  
        systems = get_meta_data()
        return render_template_string(template, systems=systems)

template = """
<!doctype html>
<form action="{{ url_for("index")}}" method="post">
    <select id="system" name='table'>
        <option></option>
    </select>
    <select id="game" name='cols' multiple></select>
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
</script>
"""

if __name__ == '__main__':
    app.run(debug=True)
