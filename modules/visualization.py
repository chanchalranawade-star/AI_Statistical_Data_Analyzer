import matplotlib.pyplot as plt


def create_histogram(df, column, output_path):
    """
    Create a histogram for a numeric column.
    """

    plt.figure(figsize=(8, 5))
    plt.hist(df[column].dropna(), bins=10)
    plt.xlabel(column)
    plt.ylabel("Frequency")
    plt.title(f"Distribution of {column}")
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()


def create_bar_chart(df, column, output_path):
    """
    Create a bar chart for a column.
    """

    values = df[column].value_counts().head(10)

    plt.figure(figsize=(8, 5))
    values.plot(kind="bar")
    plt.xlabel(column)
    plt.ylabel("Count")
    plt.title(f"Top Values of {column}")
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()


def create_boxplot(df, column, output_path):
    """
    Create a boxplot for a numeric column.
    """

    plt.figure(figsize=(8, 5))
    plt.boxplot(df[column].dropna())
    plt.ylabel(column)
    plt.title(f"Boxplot of {column}")
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()


def create_correlation_heatmap(df, output_path):
    """
    Create a correlation heatmap for numeric columns.
    """

    numeric_df = df.select_dtypes(include="number")

    if numeric_df.shape[1] < 2:
        return

    plt.figure(figsize=(10, 7))
    plt.imshow(numeric_df.corr(), cmap="coolwarm", aspect="auto")
    plt.colorbar()

    plt.xticks(
        range(len(numeric_df.columns)),
        numeric_df.columns,
        rotation=45,
        ha="right"
    )

    plt.yticks(
        range(len(numeric_df.columns)),
        numeric_df.columns
    )

    plt.title("Correlation Heatmap")
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()

def create_pie_chart(df, column, output_path):
    """
    Create a pie chart for a categorical column.
    """

    values = df[column].value_counts().head(10)

    if values.empty:
        return

    plt.figure(figsize=(8, 6))

    plt.pie(
        values.values,
        labels=values.index,
        autopct="%1.1f%%",
        startangle=90
    )

    plt.title(f"Distribution of {column}")
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()