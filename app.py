import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import pandas as pd
import seaborn as sns
import streamlit as st

from utils import \
    get_leaderboard_df, \
    get_gotchis_df, \
    get_gotchi_traits_df, \
    get_trait_scores_df, \
    get_trait_score_facet_grid

st.set_page_config(layout="wide", page_title='Gotchi Crawler Leaderboard Analytics', page_icon=':ghost:')

@st.cache_data(show_spinner="Loading leaderboard...", ttl=60*5)
def get_leaderboard_df_cached():
    return get_leaderboard_df()

@st.cache_data(show_spinner="Loading gotchi traits...", ttl=60*60)
def get_gotchis_df_cached(gotchi_ids):
    return get_gotchis_df(gotchi_ids)

def get_data():
    leaderboard_df = get_leaderboard_df_cached()
    trait_scores_df = get_trait_scores_df(leaderboard_df, \
        get_gotchi_traits_df(get_gotchis_df_cached(leaderboard_df.head(1000).index.tolist())))
    return leaderboard_df, trait_scores_df

def bin_xticks(g: sns.FacetGrid, nbins=5):
    # Set the maximum number of x ticks for each facet
    for ax in g.axes.flat:
        ax.xaxis.set_major_locator(ticker.MaxNLocator(nbins))

def main():

    leaderboard_df, trait_scores_df = get_data()
    
    st.title('Gotchi Crawler Leaderboard Analytics')
    st.header('Current Leaderboard')
    st.markdown('Data delayed by up to 5 minutes.')
    st.dataframe(leaderboard_df)
    
    st.header('Leaderboard Stats')
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric('Total Unique Gotchis', leaderboard_df.shape[0])
    with col2:
        st.metric('Total Unique Owners', leaderboard_df['ownerAddress'].nunique())
    with col3:
        st.metric('Total Matches', leaderboard_df['numMatches'].sum())
    with col4:
        st.metric('Total Hours Played', (leaderboard_df['playTime_s'].sum() / 60 / 60).round().astype(int))
    
    col1, col2, col3 = st.columns(3)

    with col1:
        fig, ax = plt.subplots()
        ax.set_title('High Score Distribution')
        sns.histplot(leaderboard_df['highScore'], kde=False)
        st.pyplot(fig)
        
    with col2:
        fig, ax = plt.subplots()
        sns.histplot(leaderboard_df.groupby('ownerAddress')['playTime_s'].sum() / 60, kde=False)
        ax.set_title('Play Time Distribution - Grouped by Owner Address')
        ax.set_xlabel('Play Time in Minutes')
        st.pyplot(fig)
        
    with col3:
        fig, ax = plt.subplots()
        ax.set_title('Score vs Depth')
        sns.scatterplot(x=leaderboard_df['maxDepth'], y=leaderboard_df['maxDepthScore'], alpha=0.4)
        st.pyplot(fig)
    
    @st.spinner('Loading charts...')
    def show_facet_grid(func, *args, **kwargs):
        g = get_trait_score_facet_grid(trait_scores_df)
        g.map(func, *args, **kwargs)
        bin_xticks(g)
        st.pyplot(g.fig)

    st.header('Player Trait Distribution')
    st.markdown('Distribution of traits for gotchis who have played.')
    show_facet_grid(sns.histplot, "value", kde=True)
    
    st.header('Player Trait vs Score')
    st.markdown('Scatter plots of high scores vs various gotchi traits.')
    show_facet_grid(plt.scatter, "value", "highScore", alpha=0.2)
    
    st.header('Player Trait vs Score (Density)')
    show_facet_grid(sns.kdeplot, "value", "highScore", cmap='hot', fill=True)
    
if __name__ == '__main__':
    main() 