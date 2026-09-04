import pandas as pd


def detect_outliers(df):
    """
    Detect outliers in numeric columns using the IQR method.
    """

    numeric_df = df.select_dtypes(include="number")

    outliers = {}

    for column in numeric_df.columns:
        Q1 = numeric_df[column].quantile(0.25)
        Q3 = numeric_df[column].quantile(0.75)

        IQR = Q3 - Q1

        lower_limit = Q1 - 1.5 * IQR
        upper_limit = Q3 + 1.5 * IQR

        column_outliers = numeric_df[
            (numeric_df[column] < lower_limit) |
            (numeric_df[column] > upper_limit)
        ][column]

        outliers[column] = {
            "count": len(column_outliers),
            "values": column_outliers.tolist(),
            "lower_limit": round(lower_limit, 2),
            "upper_limit": round(upper_limit, 2)
        }

    return outliers


def get_outlier_summary(df):
    """
    Return the number of outliers for each numeric column.
    """

    outliers = detect_outliers(df)

    summary = {}

    for column, data in outliers.items():
        summary[column] = data["count"]

    return summary