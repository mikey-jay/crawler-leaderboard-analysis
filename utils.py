import json
from typing import List

import pandas as pd
import requests

def get_leaderboard_df():
    leaderboard_data = requests.get('https://server.gotchicrawler.com/api/leaderboard').json()
    leaderboard_df = pd.json_normalize(leaderboard_data['leaderboard']).set_index('tokenId').sort_values('highScore', ascending=False)
    return leaderboard_df

def get_gotchis_df(gotchi_ids: List[int]):
    
    gotchis_query = '''
    {{
    aavegotchis(first: 1000, where: {{ id_in: [{0}] }}) {{
        id
        kinship
        modifiedNumericTraits
        withSetsRarityScore
    }}
    }}
    '''.format(','.join(list(map(str, gotchi_ids))))

    gotchis_query_json = json.dumps({"query": gotchis_query})
    gotchis_response = requests.post('https://subgraph.satsuma-prod.com/tWYl5n5y04oz/aavegotchi/aavegotchi-core-matic/api', data=gotchis_query_json).json()
    gotchis_df = pd.json_normalize(gotchis_response['data']['aavegotchis'])
    gotchis_df = gotchis_df.astype({'id': int, 'kinship': int, 'withSetsRarityScore': int})
    gotchis_df.set_index('id', inplace=True)
    return gotchis_df