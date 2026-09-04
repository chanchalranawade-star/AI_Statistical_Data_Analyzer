import pandas as pd
import os


def load_dataset(file_path):
    """
    Load CSV or Excel dataset.
    """

    if not os.path.exists(file_path):
        raise FileNotFoundError("Dataset file not found.")

    extension = os.path.splitext(file_path)[1].lower()

    if extension == ".csv":
        df = pd.read_csv(file_path)

    elif extension in [".xlsx", ".xls"]:
        df = pd.read_excel(file_path)

    else:
        raise ValueError(
            "Unsupported file format. "
            "Only CSV, XLSX and XLS files are allowed."
        )

    return df


def get_dataset_info(df):
    """
    Return basic information about the dataset.
    """

    return {
        "rows": len(df),
        "columns": len(df.columns),
        "column_names": list(df.columns),
        "missing_values": int(df.isnull().sum().sum()),
        "duplicate_rows": int(df.duplicated().sum())
    }