from flask import Flask, render_template_string, request, make_response
from flask_sqlalchemy import SQLAlchemy
import os
import urllib.parse 
import pyodbc
from azure.mgmt.datafactory import DataFactoryManagementClient
from azure.storage.blob import BlobServiceClient
from azure.identity import ClientSecretCredential
from azure.mgmt.datafactory import DataFactoryManagementClient
import time

app = Flask(__name__)


#sql db connection
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


#adf connection
subscription_id = '4d879729-ae6a-47cf-9e85-0d3a2685fa52'
rg_name = 'rg-data_delivery-dev-westeu'
df_name = 'data-delivery-fact'
p_name = 'pipeline1'
credentials = ClientSecretCredential(client_id='c71f3d68-311f-4220-8c1b-ac4f75e48b29', client_secret='Oep8Q~5BsBSta.lgqNID4~K8nuCjtBIeQqZnwcya', tenant_id='540d6e0e-8b44-4420-a0b5-a06c4d7f9666')
adf_client = DataFactoryManagementClient(credentials, subscription_id)

#blob connection
connect_str = 'DefaultEndpointsProtocol=https;AccountName=exportblobdelivery;AccountKey=8n9ULDJ9gZlIjfclF83EN3usDEHMbNpvAdbjwUFwfPqJ7sgF1uufD8SUiAEILeyNHDyw/Vnukqyz+AStaA66HQ==;EndpointSuffix=core.windows.net'
blob_service_client = BlobServiceClient.from_connection_string(connect_str)
container_name = 'exports'
container_client = blob_service_client.get_container_client(container_name)

blob_list = container_client.list_blobs()
for blob in blob_list:
    print("\t" + blob.name)
container_client = blob_service_client.get_container_client(container= container_name)

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
    table_data = db.session.execute("SELECT TABLE_SCHEMA, TABLE_NAME FROM INFORMATION_SCHEMA.TABLES").all()
    tables = [str(i[1]) for i in table_data]
    schema_tables = ['.'.join(i) for i in table_data]
    return tables, schema_tables


@app.route('/', methods =["GET", "POST"])
def index():
    if request.method == "POST":
        req_table = request.form.get('table')
        req_cols = request.form.getlist('cols')
        run_response = adf_client.pipelines.create_run(rg_name, df_name, p_name, parameters={})
        
        pipe_status = 'created'
        while pipe_status != 'Succeeded':
            time.sleep(30)
            pipeline_run = adf_client.pipeline_runs.get(
                rg_name, df_name, run_response.run_id)
            print("\n\tPipeline run status: {}".format(pipeline_run.status))
            pipe_status = pipeline_run.status
            
        resp = make_response(container_client.download_blob(blob.name).readall())
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
