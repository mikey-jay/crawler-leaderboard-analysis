import json
from typing import List

import pandas as pd
import requests
import seaborn as sns

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
    gotchis_response = requests.post('https://subgraph.satsuma-prod.com/tWYl5n5y04oz/aavegotchi/aavegotchi-core-matic/api', \
        data=gotchis_query_json).json()
    gotchis_df = pd.json_normalize(gotchis_response['data']['aavegotchis'])
    gotchis_df = gotchis_df.astype({'id': int, 'kinship': int, 'withSetsRarityScore': int})
    gotchis_df.set_index('id', inplace=True)
    return gotchis_df

def get_gotchi_traits_df(gotchis_df: pd.DataFrame):
    traits_df = gotchis_df['modifiedNumericTraits'].apply(pd.Series).rename(columns={0:'NRG', 1:'AGG', 2:'SPK', 3:'BRN', 4:'EYS', 5:'EYC'}).merge(gotchis_df[['kinship', 'withSetsRarityScore']], left_index=True, right_index=True)
    return traits_df

def get_trait_scores_df(leaderboard_df: pd.DataFrame, traits_df: pd.DataFrame):
    return pd.concat([traits_df, leaderboard_df['highScore']], axis='columns') \
        .melt(id_vars='highScore', var_name='trait', value_name='value')
        
def get_trait_score_facet_grid(trait_score_df: pd.DataFrame, sharex=False, col_wrap=4, height=4, **args):
    return sns.FacetGrid(trait_score_df, col="trait", sharex=sharex, col_wrap=col_wrap, height=height, **args)
