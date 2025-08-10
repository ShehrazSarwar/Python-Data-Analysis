import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

st.title('NBA Player Stats Explorer')
st.markdown(''' 
This app performs simple webscraping of NBA player stats data!
* **Python Libraries:** pandas, numpy, matplotlib, seaborn, and streamlit
* **Data Source:** [Basketball-reference.com](https://www.basketball-reference.com)
''')

st.sidebar.title('User Input Features')
selected_year = st.sidebar.selectbox('Year',reversed(range(1990,2020)))

@st.cache_data
def load_data(selected_year):
    url = f'https://www.basketball-reference.com/leagues/NBA_{selected_year}_per_game.html'
    df = pd.read_html(url,header=0)
    df = pd.concat(df).drop_duplicates()
    if not df[df['Age'] == 'Age'].empty:
        raw = df.drop(df[df['Age'] == 'Age'].index)
        raw = raw.drop(raw[raw['Player'] == 'League Average'].index)
    else:
        raw = df.drop(df[df['Player'] == 'League Average'].index)
    playerstats = raw.fillna(0)
    return playerstats

playerstats = load_data(selected_year)

sorted_unique_team = sorted(playerstats.Team.unique())
selected_team = st.sidebar.multiselect('Team',sorted_unique_team,sorted_unique_team)

positions = sorted(playerstats.Pos.unique())
selected_position = st.sidebar.multiselect('Position',positions,positions)

df_selected_team = playerstats[(playerstats.Team.isin(selected_team)) & (playerstats.Pos.isin(selected_position))]

st.header('Display Player Stats of Selected Team(s)')
st.write(f'Data Dimension: {df_selected_team.shape[0]} rows and {df_selected_team.shape[1]} columns')
st.dataframe(df_selected_team)
st.download_button(data = df_selected_team.to_csv(index=False),label="Download CSV File",file_name=f'NBA{selected_year}.csv')

# Heatmap
if st.button('Intercorrelation Heatmap'):
    st.header('Intercorrelation Matrix Heatmap')

    corr = df_selected_team.corr(numeric_only=True)
    mask = np.zeros_like(corr)
    mask[np.triu_indices_from(mask)] = True
    with sns.axes_style("white"):
        f, ax = plt.subplots(figsize=(7, 5))
        ax = sns.heatmap(corr, mask=mask, vmax=1, square=True)
    st.pyplot(f)





