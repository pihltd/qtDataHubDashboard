import os

import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
from datetime import datetime, timezone
from pytz import timezone as tz

def dhAPICreds(tier):
    """A simple way to retrieve the Data Hub submission URLs and API tokens

    :param tier: A string for the tier to return.  Must be one of prod, stage, qa, qa2, dev, dev2
    :type tier: String
    :return url: The URL for the requested tier
    :rtype: URL
    :return token: The API access token for the tier.
    :rtype: dictionary
    """
    
    #url = None
    #token = None
    
    urls = {
        'prod': 'https://hub.datacommons.cancer.gov/api/graphql',
        'stage': 'https://hub-stage.datacommons.cancer.gov/api/graphql',
        'qa': 'https://hub-qa.datacommons.cancer.gov/api/graphql',
        'qa2': 'https://hub-qa2.datacommons.cancer.gov/api/graphql',
        'dev': 'https://hub-dev.datacommons.cancer.gov/api/graphql',
        'dev2': 'https://hub-dev2.datacommons.cancer.gov/api/graphql',
        'localtest': 'https://this.is.a.test/url/graphql'
    }
    
    apikeys = {
        'prod': 'PRODAPI',
        'stage': 'STAGEAPI',
        'qa': 'QAAPI',
        'qa2': 'QA2API',
        'dev': 'DEVAPI',
        'dev2': 'DEV2API',
        'localtest': 'LOCALTESTAPI'
    }
    
    if tier in urls.keys():
        return {'url': urls[tier], 'token': os.getenv(apikeys[tier])}
    else:
        return {'url': None, 'token': None}



def dhApiQuery(url, apitoken, query, variables=None):
    """Runs queries against the Data Hub Submission Portal API

    :param url: URL of the Submission Portal API
    :type url: URL
    :param apitoken: API Access token obtained from the Submission Portal
    :type apitoken: String
    :param query: A valid GraphQL query
    :type query: String
    :param variables: a JSON object containing any variables for the provided query
    :type variables: dictionary, optional
    :return: If status_code == 200, a JSON object that is the full query response
    :rtype: dictionary
    :return: If status_code != 200, a string with error code and message
    :rtype: string
    :return: If HTTP error, the requests.HTTPError object
    :rtype: request.HTTPError
    """
    headers = {"Authorization": f"Bearer {apitoken}"}
    try:
        retry = Retry(total=5, backoff_factor=2, status_forcelist=[429, 500, 502, 503, 504])
        adapter = HTTPAdapter(max_retries=retry)
        session = requests.Session()
        session.mount('https://', adapter)
        if variables is None:
            result = session.post(url=url, headers=headers, json={"query": query}, timeout=160)
        else:
            result = session.post(url=url, headers=headers, json={"query": query, "variables": variables}, timeout=160)
        if result.status_code == 200:
            return result.json()
        else:
            return (f"Status Code: {result.status_code}\n{result.content}")
    except requests.exceptions.HTTPError as e:
        return (f"HTTPError: {e}")
    

def elapsedTime(submission_df):
    days = []
    for index, row in submission_df.iterrows():
        temp = row['updatedAt'].split('T')
        update = datetime.strptime(temp[0], '%Y-%m-%d')
        update = update.replace(tzinfo=tz('UTC'))
        now = datetime.now(timezone.utc)
        diff = (now - update).days
        days.append(diff)
    submission_df.insert(8,'inactiveDays',days,True)
    return submission_df