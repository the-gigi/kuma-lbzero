import os
import hug
import requests

social_graph_endpoint = os.environ.get('SOCIAL_GRAPH_MANAGER_PORT', 'http://localhost:9091')
social_graph_endpoint = social_graph_endpoint.replace('tcp://', 'http://')

@hug.get('/followers')
def followers(name):
    url = f'{social_graph_endpoint}/followers/{name}'
    try:
        return requests.get(url).json()
    except Exception as e:
        return dict(url=url,
                    err=str(e))


@hug.get('/following')
def followers(name):
    return requests.get(f'{social_graph_endpoint}/following/{name}').json()
