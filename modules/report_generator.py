def generate_report(dataset_info, statistics, correlations, outliers, insights):
    """
    Generate a complete analysis report.
    """

    report = {
        "dataset_info": dataset_info,
        "statistics": statistics,
        "strong_correlations": correlations,
        "outliers": outliers,
        "insights": insights
    }

    return report


def format_report(report):
    """
    Convert the analysis report into readable text.
    """

    text = []

    text.append("STATISTICAL DATA ANALYSIS REPORT")
    text.append("=" * 40)

    # Dataset information
    dataset_info = report.get("dataset_info", {})

    text.append("\nDATASET INFORMATION")
    text.append("-" * 25)
    text.append(f"Rows: {dataset_info.get('rows', 0)}")
    text.append(f"Columns: {dataset_info.get('columns', 0)}")
    text.append(
        f"Missing Values: {dataset_info.get('missing_values', 0)}"
    )
    text.append(
        f"Duplicate Rows: {dataset_info.get('duplicate_rows', 0)}"
    )

    # Insights
    text.append("\nINSIGHTS")
    text.append("-" * 25)

    for insight in report.get("insights", []):
        text.append(f"- {insight}")

    return "\n".join(text)