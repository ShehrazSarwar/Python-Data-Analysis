import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import altair as alt

st.title('NFL Football Stats Explorer ⚽')

st.markdown("""
This app performs simple webscraping of NFL Football player stats data (focusing on Rushing)!
* **Python libraries:** pandas, streamlit, numpy, matplotlib, seaborn, altair
* **Data source:** [pro-football-reference.com](https://www.pro-football-reference.com/).
""")

st.sidebar.title('User Input Features 🤵')
selected_year = st.sidebar.selectbox('Year', reversed(range(2000,2025)))

@st.cache_data
def load_data(year):
    url = f"https://www.pro-football-reference.com/years/{selected_year}/rushing.htm"
    df = pd.read_html(url,header=1)
    df = pd.concat(df,ignore_index=True).drop_duplicates()
    df = df.drop(df[df['Player'] == 'League Average'].index)
    playerstats = df.fillna(0)
    return playerstats

playerstats = load_data(selected_year)

sorted_unique_team = sorted(playerstats.Team.unique())
selected_team = st.sidebar.multiselect('Team', sorted_unique_team, sorted_unique_team)

unique_pos = sorted(playerstats.Pos.unique())
selected_pos = st.sidebar.multiselect('Position', unique_pos, unique_pos)

df_selected_team = playerstats[(playerstats.Team.isin(selected_team)) & (playerstats.Pos.isin(selected_pos))]

st.header('Display Player Stats of Selected Team(s)')
st.write('Data Dimension: ' + str(df_selected_team.shape[0]) + ' rows and ' + str(df_selected_team.shape[1]) + ' columns.')
st.dataframe(df_selected_team)

if st.download_button(data = df_selected_team.to_csv(index=False),label='Download CSV File',file_name=f'NFL{selected_year}.csv'):
    st.success('Thank You for using NFL Football Stats Explorer 🤗')

cols = st.columns(3)
with cols[0]:
    total_players = df_selected_team['Player'].unique().shape[0]
    st.metric(label='Total Players',value=total_players,border=True)

with cols[1]:
    if df_selected_team.empty:
        st.metric(label='Max Goal Scorer',value=0,border=True)
    else:
        max_goal_scorer = df_selected_team[df_selected_team['G'] == df_selected_team['G'].max()]['Player'].values[0]
        st.metric(label='Max Goal Scorer',value=max_goal_scorer,border=True)
    
with cols[2]:
    if df_selected_team.empty:
        st.metric(label='Max Goal',value=0,border=True)
    else:
        max_goal = int(df_selected_team['G'].max())
        st.metric(label="Max Goal",value=max_goal,border=True)

# Visualizations
if not df_selected_team.empty:
    if len(df_selected_team) > 5:
        container = st.container(border=True)
        top_scorers = df_selected_team.nlargest(10,columns='G',keep='first')
        top_scorers['Rank'] = top_scorers['G'].rank(method='first')
        top_scorers = top_scorers.sort_values(by='Rank',ascending=False)
        container.write(f'**Top {top_scorers.shape[0]} Players**')
        container.bar_chart(top_scorers,x='Player',y='Rank',color='#ffaa00')

if not df_selected_team.empty:
    if len(df_selected_team) > 5:
        container.divider()

        top_success = df_selected_team.nlargest(5, columns='Succ%', keep='first')

        # Bubble chart
        chart = alt.Chart(top_success).mark_circle().encode(
            x=alt.X('Player:N', title='Player'),
            y=alt.Y('Succ%:Q', title='Success Rate (%)'),
            size=alt.Size('Succ%:Q', scale=alt.Scale(range=[500, 3000])),
            color=alt.Color('Player:N', scale=alt.Scale(scheme='category20b')),
            tooltip=['Player', alt.Tooltip('Succ%:Q', format='.2%')]
        ).properties(
            width=600,
            height=400,
            title='Top 5 Players by Success Rate'
        )

        container.altair_chart(chart, use_container_width=True)

# Heatmap
with st.expander('Check Intercorrelation Heatmap'):
    st.header('Intercorrelation Matrix Heatmap')
    corr = df_selected_team.corr(numeric_only=True)
    mask = np.zeros_like(corr)
    mask[np.triu_indices_from(mask)] = True
    with sns.axes_style("white"):
        f, ax = plt.subplots(figsize=(7, 5))
        ax = sns.heatmap(corr, mask=mask, vmax=1, square=True)
    st.pyplot(f)

with st.sidebar:
    st.subheader("🎵 Music Player")

    if "music_playing" not in st.session_state:
        st.session_state.music_playing = False

    col1, col2 = st.columns([0.4, 0.4])

    with col1:
        if st.button("▶ Play Music", key="play_btn"):
            st.session_state.music_playing = True

    with col2:
        if st.button("⏹ Stop Music", key="stop_btn"):
            st.session_state.music_playing = False

    # Inject HTML audio only when playing
    if st.session_state.music_playing:
        st.markdown("""
            <audio id="bg-music" autoplay loop>
                <source src="https://westsidemusicblog.net/wp-content/uploads/2022/11/Jungkook-Dreamers-.mp3" type="audio/mp3">
            </audio>
        """, unsafe_allow_html=True)