def generate_insights(df, statistics, correlations, outliers):
    """
    Generate simple human-readable insights from the analysis.
    """

    insights = []

    # Dataset size
    insights.append(
        f"The dataset contains {len(df)} rows and {len(df.columns)} columns."
    )

    # Statistical insights
    for column, values in statistics.items():

        mean = values.get("mean")
        median = values.get("median")

        if mean is not None and median is not None:
            if mean > median:
                insights.append(
                    f"For {column}, the mean ({mean}) is higher than "
                    f"the median ({median}), indicating some higher values."
                )

            elif mean < median:
                insights.append(
                    f"For {column}, the mean ({mean}) is lower than "
                    f"the median ({median}), indicating some lower values."
                )

            else:
                insights.append(
                    f"For {column}, the mean and median are approximately equal."
                )

    # Correlation insights
    for item in correlations:
        variable_1 = item["variable_1"]
        variable_2 = item["variable_2"]
        correlation = item["correlation"]

        if correlation > 0:
            insights.append(
                f"{variable_1} and {variable_2} have a strong positive "
                f"correlation ({correlation})."
            )
        else:
            insights.append(
                f"{variable_1} and {variable_2} have a strong negative "
                f"correlation ({correlation})."
            )

    # Outlier insights
    for column, count in outliers.items():

        if count > 0:
            insights.append(
                f"{column} contains {count} potential outlier(s)."
            )
        else:
            insights.append(
                f"No potential outliers were detected in {column}."
            )

    return insights