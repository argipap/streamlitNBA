# nba_stats.property

import streamlit as st
import pandas as pd
from PIL import Image
from utils.export_utils import ExportUtils
from utils.config import DATA_SOURCE_URL
from utils.data_utils import DataUtils


st.title("Kantina Basketball Association")

image = Image.open("kba_logo.jpg")
st.image(image, use_column_width=True)

st.markdown(
    """### NBA player statistics and yahoo fanpoints for KBA league.
* **Data source:** [Basketball-reference.com](https://www.basketball-reference.com/)
"""
)

st.sidebar.header("Filtering")
selected_year = st.sidebar.selectbox(
    "Year",
    list(reversed([str(year) + "-" + str(year + 1) for year in range(1980, DataUtils.get_season_year())])),
)
selected_category = st.sidebar.selectbox("Stats", ("Avg", "Total"))


@st.cache
def load_data(year: str, stat_type: str):
    url = DATA_SOURCE_URL + str(year).split("-")[1] + stat_type + ".html"
    html = pd.read_html(url, header=0)
    data_frame = html[0]
    raw = data_frame.drop(
        data_frame[data_frame.Age == "Age"].index
    )  # Deletes repeating headers in content
    raw = raw.fillna(0)
    playerstats = raw.drop(["Rk"], axis=1)
    aggregation_functions = {}
    columns = DataUtils.get_columns(playerstats)
    DataUtils.convert_columns_to_numeric(
        playerstats, DataUtils.get_numeric_columns(columns)
    )
    aggregation_functions = DataUtils.get_aggregate_functions(columns)
    playerstats = playerstats.groupby(playerstats["Player"]).aggregate(
        aggregation_functions
    )
    playerstats["FanPoints"] = DataUtils.calculate_fan_points(playerstats)
    playerstats.sort_values(["FanPoints"], ascending=False, inplace=True)
    return playerstats


playerstats = load_data(selected_year, DataUtils.get_stat_type(selected_category))

# Sidebar - Player selection
sorted_unique_players = sorted(playerstats.Player.unique())
options = sorted_unique_players.append("All")
selected_player = st.sidebar.multiselect("Player", sorted_unique_players, ["All"])
if "All" in selected_player:
    selected_player = sorted_unique_players

# Sidebar - Team selection
sorted_unique_teams= sorted(playerstats.Tm.unique())
options = sorted_unique_teams.append("All")
selected_team = st.sidebar.multiselect("Team", sorted_unique_teams, ["All"])
if "All" in selected_team:
    selected_team = sorted_unique_teams

# Sidebar - Position selection
unique_pos = ["C", "PF", "SF", "PG", "SG"]
options = unique_pos.append("All")
selected_pos = st.sidebar.multiselect("Position", unique_pos, ["All"])
if "All" in selected_pos:
    selected_pos = unique_pos


# Filtering data
df_selection = playerstats[
    (playerstats.Tm.isin(selected_team)) &
    (playerstats.Pos.isin(selected_pos)) &
    (playerstats.Player.isin(selected_player))
]
st.header(f"Display season player(s) stats according to filtering criteria")
st.write(
    "Data Dimension: "
    + str(df_selection.shape[0])
    + " rows and "
    + str(df_selection.shape[1])
    + " columns."
)
st.dataframe(df_selection)

st.markdown(
    ExportUtils.export_to_csv(df_selection, selected_category, selected_year),
    unsafe_allow_html=True,
)
