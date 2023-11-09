import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import pandas as pd
import seaborn as sns
import streamlit as st

from utils import get_leaderboard_df, get_gotchis_df

@st.cache_data(show_spinner="Loading leaderboard...", ttl=60*5)
def get_leaderboard_df_cached():
    return get_leaderboard_df()

@st.cache_data(show_spinner="Loading gotchi traits...", ttl=60*60)
def get_gotchis_df_cached(gotchi_ids):
    return get_gotchis_df(gotchi_ids)

st.title('Gotchi Crawler Leaderboard Analytics')
st.header('Current Leaderboard')

leaderboard_df = get_leaderboard_df_cached()
st.dataframe(leaderboard_df)

st.header('Metrics Overview')
st.dataframe(leaderboard_df.describe())

fig, ax = plt.subplots()
st.header('High Score Distribution')
sns.histplot(leaderboard_df['highScore'], kde=True)
st.pyplot(fig)

fig, ax = plt.subplots()
st.header('Play Time Distribution')
sns.histplot(leaderboard_df['playTime_s'] / 60, kde=True)
ax.set_xlabel('Play Time in Minutes')
st.pyplot(fig)

st.header('Score vs Depth')
fig, ax = plt.subplots()
sns.scatterplot(x=leaderboard_df['maxDepth'], y=leaderboard_df['maxDepthScore'], alpha=0.4)
st.pyplot(fig)
