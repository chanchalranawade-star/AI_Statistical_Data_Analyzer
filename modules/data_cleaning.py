import pandas as pd


def clean_dataset(df):
    """
    Clean the dataset safely.

    - Remove duplicate rows
    - Handle missing values
    - Convert numeric-looking columns to numeric values
    """

    cleaned_df = df.copy()

    # Remove duplicate rows
    cleaned_df = cleaned_df.drop_duplicates()

    # Try to convert object columns to numeric
    for column in cleaned_df.columns:

        if cleaned_df[column].dtype == "object":

            converted = pd.to_numeric(
                cleaned_df[column],
                errors="coerce"
            )

            # Convert only if most non-empty values are numeric
            original_non_null = cleaned_df[column].notna().sum()
            converted_non_null = converted.notna().sum()

            if (
                original_non_null > 0
                and converted_non_null / original_non_null >= 0.8
            ):
                cleaned_df[column] = converted

    # Handle missing values
    for column in cleaned_df.columns:

        if pd.api.types.is_numeric_dtype(cleaned_df[column]):

            median_value = cleaned_df[column].median()

            if pd.notna(median_value):
                cleaned_df[column] = cleaned_df[column].fillna(
                    median_value
                )

        else:

            cleaned_df[column] = cleaned_df[column].fillna(
                "Unknown"
            )

    return cleaned_df


def get_cleaning_summary(original_df, cleaned_df):
    """
    Return a summary of changes made during data cleaning.
    """

    return {
        "original_rows": len(original_df),
        "cleaned_rows": len(cleaned_df),
        "duplicates_removed": (
            len(original_df) - len(cleaned_df)
        ),
        "missing_values_before": int(
            original_df.isnull().sum().sum()
        ),
        "missing_values_after": int(
            cleaned_df.isnull().sum().sum()
        )
    }