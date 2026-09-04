import pandas as pd


def calculate_statistics(df):
    """
    Calculate basic statistical measures for numeric columns.
    """

    numeric_df = df.select_dtypes(include="number")

    if numeric_df.empty:
        return {}

    statistics = {}

    for column in numeric_df.columns:
        statistics[column] = {
            "mean": round(numeric_df[column].mean(), 2),
            "median": round(numeric_df[column].median(), 2),
            "mode": (
                numeric_df[column].mode().iloc[0]
                if not numeric_df[column].mode().empty
                else None
            ),
            "minimum": round(numeric_df[column].min(), 2),
            "maximum": round(numeric_df[column].max(), 2),
            "variance": round(numeric_df[column].var(), 2),
            "standard_deviation": round(numeric_df[column].std(), 2)
        }

    return statistics


def get_summary_statistics(df):
    """
    Return overall descriptive statistics.
    """

    numeric_df = df.select_dtypes(include="number")

    if numeric_df.empty:
        return {}

    return numeric_df.describe().round(2).to_dict()