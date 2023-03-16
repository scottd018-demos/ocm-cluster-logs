#!/bin/env python3

import requests
from requests_oauthlib import OAuth2Session
import json
from pathlib import Path
import pprint
import datetime
from dateparser import parse
import os
import boto3
import time
from requests.exceptions import ConnectionError

pp = pprint.PrettyPrinter(indent=4)

API_HOST = 'https://api.openshift.com'
API = API_HOST + '/api/clusters_mgmt/v1'
LOGS = API_HOST + '/api/service_logs/v1'
CLUSTER_LOGS = LOGS + '/cluster_logs'
CLUSTER_NAME = os.getenv('CLUSTER_NAME')
OCM_JSON = os.getenv('OCM_JSON', str(Path.home()) + "/.ocm.json")
DEBUG = False
API_KEY = os.getenv('OCM_API_KEY')

def get_token():

    f = open(OCM_JSON,)
    user = json.load(f)

    auth = (user['client_id'], user['access_token'])

    params = {
        "grant_type": "refresh_token",
        "refresh_token": user['refresh_token']
    }

    response = requests.post(user['token_url'], auth=auth, data=params)

    return response.json()['access_token']


def get_cluster(session):
    response = session.get(API + "/clusters/")
    if DEBUG:
        pp.pprint(response.json())
    for cluster in response.json()['items']:
        if cluster['name'] == CLUSTER_NAME:
            return cluster

    return None

# get list of clusters
iam = boto3.client('iam')
session = requests.Session()
token = get_token()
session.headers.update({'Authorization': 'Bearer {0}'.format(token)})

cluster = get_cluster(session)

if cluster is None:
    print("-> unable to locate cluster {0}".format(CLUSTER_NAME))
else:
    cluster_id = cluster['id']

    logs = session.get(CLUSTER_LOGS + '?size=1000&search=cluster_id%20%3D%20%27' + cluster_id + '%27')
    pp.pprint(logs.json())
