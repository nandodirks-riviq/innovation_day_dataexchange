from flask import Flask, render_template_string, request
from wtforms import Form, SelectMultipleField
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

class LanguageForm(Form):
    col_names = db.session.execute("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.columns WHERE TABLE_NAME = 'BuildVersion'").all()
    for i in col_names:
        print(i)
    col_names = [i[2:-3] for i in col_names]
    language = SelectMultipleField(u'Desired columns', choices=col_names)

template_form = """
{% block content %}
<h1>Set Language</h1>

<form method="POST" action="/">
    <div>{{ form.language.label }} {{ form.language(rows=4, multiple=True) }}</div>
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
    form = LanguageForm(request.form)

    if request.method == 'POST':
        print("POST request and form is valid")
        cols =  form.language.data
        print("languages in wsgi.py: %s" % request.form['language'])
        db.session.execute("SELECT * FROM dbo.BuildVersion").all()
        return f"<p>{cols}</p>"
    else:
        return render_template_string(template_form, form=form)

if __name__ == '__main__':
    app.run(debug=True)

