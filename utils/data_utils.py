# utils/data_utils.py

import pandas as pd
from typing import List, Dict


class DataUtils:
    @staticmethod
    def get_columns(dataframe: pd.DataFrame) -> List:
        return [column for column in dataframe.head().columns]

    @staticmethod
    def get_aggregate_functions(columns: List) -> Dict:
        aggregation_functions = {}
        for column in columns:
            if column not in ("Player", "Pos", "Age", "Tm"):
                aggregation_functions[column] = "mean"
            else:
                aggregation_functions[column] = "last"
        return aggregation_functions

    @staticmethod
    def get_numeric_columns(columns: List):
        numeric_columns = columns.copy()
        for column in ("Player", "Pos", "Age", "Tm"):
            numeric_columns.remove(column)
        return numeric_columns

    @staticmethod
    def convert_columns_to_numeric(dataframe: pd.DataFrame, columns):
        for column in columns:
            dataframe[column] = pd.to_numeric(dataframe[column])

    @staticmethod
    def calculate_fan_points(playerstats: pd.DataFrame) -> pd.Series:
        fan_points = playerstats.apply(
            lambda row: (float(row["FGA"]) * -0.9)
            + (float(row["FG"]) * 1)
            + (float(row["FTA"]) * -0.8)
            + (float(row["FT"]) * 1)
            + (float(row["3P"]) * 2.2)
            + (float(row["PTS"]) * 0.9)
            + (float(row["TRB"]) * 1.5)
            + (float(row["AST"]) * 2)
            + (float(row["STL"]) * 3)
            + (float(row["BLK"]) * 3)
            + (float(row["TOV"]) * -2.2),
            axis=1,
        )
        return fan_points

    @staticmethod
    def get_stat_type(selected_category: str) -> str:
        stat_type = "_per_game" if selected_category == "Avg" else "_totals"
        return stat_type
