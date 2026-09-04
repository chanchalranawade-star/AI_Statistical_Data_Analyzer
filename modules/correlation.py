import pandas as pd


def calculate_correlation(df):
    """
    Calculate correlation between numeric columns.
    """

    numeric_df = df.select_dtypes(include="number")

    if numeric_df.shape[1] < 2:
        return {}

    correlation_matrix = numeric_df.corr().round(2)

    return correlation_matrix.to_dict()


def get_strong_correlations(df, threshold=0.7):
    """
    Find pairs of variables with strong positive or negative correlation.
    """

    numeric_df = df.select_dtypes(include="number")

    if numeric_df.shape[1] < 2:
        return []

    correlation_matrix = numeric_df.corr()

    strong_correlations = []

    columns = correlation_matrix.columns

    for i in range(len(columns)):
        for j in range(i + 1, len(columns)):

            value = correlation_matrix.iloc[i, j]

            if abs(value) >= threshold:
                strong_correlations.append({
                    "variable_1": columns[i],
                    "variable_2": columns[j],
                    "correlation": round(value, 2)
                })

    return strong_correlations