import requests

def dbx_authenticate():
    url = "http://192.168.7.221:9092/authorization/oauth/token"
    access_token = ""

    auth_header = "Basic SUQtQzIzMjMzQUEtQUI2Ri00REI0LUE2NEQtQjVFRDI0Nzk2NDJBOiRjZDY3OWYyMDczNGM0NzUxOGQ1NTQ1MTgwNjNlMTRkZg=="
    
    login_data = {
        "grant_type": "password",
        "username": "unisoma",
        "password": "unisoma"
    }

    response = requests.post(
        url,
        headers={"Authorization": auth_header},
        data=login_data
    )

    if response.status_code == 200:
        json_content = response.json()
        # print(json_content)
        # print(type(json_content))
        access_token = json_content["access_token"]

    return access_token


def dbx_call_service(access_token, entity_catalog):
    import requests
    import json
    url = f"http://192.168.7.221:9091/databox/api/metadata/findMetaDataByCatalogName/{entity_catalog}"
    auth_header = f"Bearer {access_token}"

    headers = {
        "Authorization": auth_header,
        "accept": "application/json",
        "content-type": "application/json"
    }

    response = requests.post(url, headers=headers)

    if response.status_code == 200:
        json_content = response.json()

        try:
            # We are considering that json_content is a dictionary
            sql = json_content.get("entityQuery")
            return sql
        
        except AttributeError:
            # For some reason, the json is actually a list
            for json_dict in json_content:
                if "entityQuery" not in json_dict:
                    continue 
                else:
                    sql = json_dict.get("entityQuery")
                    return sql
                
    else:
        return None


import os
import subprocess
import pandas as pd

def load_data(entity_catalog):
    print("Removing dump file...")
    dump_file = "~/dump.Rds"
    if os.path.exists(dump_file):
        os.remove(dump_file)

    print("Accessing DataBox...")
    # entity_catalog = "bi_projeto"
    # Authenticate with DataBOX and retrieve the appropriate SQL
    access_token = dbx_authenticate()
    meta_data_sql = dbx_call_service(access_token, entity_catalog)

    # Request data from DataBOX for the Catalog
    print("Collecting data...")
    os.chdir("~/.local/")
    subprocess.run(["/bin/python3", "/opt/trino/load_data.py", f"'{meta_data_sql}'"])

    print("Convert RDS to Dataset...")
    # Load data from the RDS file
    result = pd.read_rds(dump_file)

    return result

# Example usage:
entity_catalog = "bi_projeto"
loaded_data = load_data(entity_catalog)
print(loaded_data)
