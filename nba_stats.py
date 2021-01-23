import streamlit as st
import pandas as pd
import base64
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from PIL import Image
from typing import List, Dict


st.title('Kantina Basketball Association')

image = Image.open('kba_logo.jpg')
st.image(image, use_column_width=True)

st.markdown("""### NBA player statistics and yahoo fanpoints for KBA league.
* **Data source:** [Basketball-reference.com](https://www.basketball-reference.com/)
""")


st.sidebar.header('User Input Features')
selected_year = st.sidebar.selectbox('Year', list(reversed([str(year)+"-"+str(year+1) for year in range(2010,2021)])))


def get_columns(dataframe: pd.DataFrame) -> List:
    return [column for column in dataframe.head().columns]


def get_aggregate_functions(columns: List) -> Dict:
    aggregation_functions = {}
    for column in columns:
        if column not in ("Player", "Pos", "Age", "Tm"):
            aggregation_functions[column] = "mean"
        else:
            aggregation_functions[column] = "last"
    return aggregation_functions


def get_numeric_columns(columns: List):
    numeric_columns = columns.copy()
    for column in ("Player", "Pos", "Age", "Tm"):
        numeric_columns.remove(column)
    return numeric_columns


def convert_columns_to_numeric(dataframe: pd.DataFrame, columns):
    for column in columns:
        dataframe[column] = pd.to_numeric(dataframe[column])


@st.cache
def load_data(year: str):
    url = "https://www.basketball-reference.com/leagues/NBA_" + str(year).split("-")[1] + "_per_game.html"
    html = pd.read_html(url, header = 0)
    data_frame = html[0]
    raw = data_frame.drop(data_frame[data_frame.Age == 'Age'].index) # Deletes repeating headers in content
    raw = raw.fillna(0)
    playerstats = raw.drop(['Rk'], axis=1)
    aggregation_functions = {}
    columns = get_columns(playerstats)
    convert_columns_to_numeric(playerstats, get_numeric_columns(columns))
    print(playerstats)
    aggregation_functions = get_aggregate_functions(columns)
    print(aggregation_functions)
    playerstats = playerstats.groupby(playerstats['Player']).aggregate(aggregation_functions)
    playerstats["FanPoints"] = playerstats.apply(
        lambda row:
            (float(row['FGA']) * -0.9) +
            (float(row['FG']) * 1) +
            (float(row['FTA']) * -0.8) +
            (float(row['FT']) * 1) +
            (float(row['3P']) * 2.2) +
            (float(row['PTS']) * 0.9) +
            (float(row['TRB']) * 1.5) +
            (float(row['AST']) * 2) +
            (float(row['STL']) * 3) +
            (float(row['BLK']) * 3) +
            (float(row['TOV']) * -2.2),
            axis=1
    )
    playerstats.sort_values(["FanPoints"], ascending=False, inplace=True)
    return playerstats

playerstats = load_data(selected_year)
print(playerstats)

# Sidebar - Team selection
sorted_unique_team = sorted(playerstats.Tm.unique())
selected_team = st.sidebar.multiselect('Team', sorted_unique_team, sorted_unique_team)

# Sidebar - Position selection
unique_pos = ['C','PF','SF','PG','SG']
selected_pos = st.sidebar.multiselect('Position', unique_pos, unique_pos)

# Filtering data
df_selected_team = playerstats[(playerstats.Tm.isin(selected_team)) & (playerstats.Pos.isin(selected_pos))]

st.header('Display Player Stats of Selected Team(s)')
st.write('Data Dimension: ' + str(df_selected_team.shape[0]) + ' rows and ' + str(df_selected_team.shape[1]) + ' columns.')
st.dataframe(df_selected_team)

# Download NBA player stats data
# https://discuss.streamlit.io/t/how-to-download-file-in-streamlit/1806
def filedownload(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # strings <-> bytes conversions
    href = f'<a href="data:file/csv;base64,{b64}" download="playerstats.csv">Download CSV File</a>'
    return href

st.markdown(filedownload(df_selected_team), unsafe_allow_html=True)
