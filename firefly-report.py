

import marimo

__generated_with = "0.13.0"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import pandas as pd
    import io
    return io, mo, pd


@app.cell
def _(mo):
    mo.md(
        r"""
        # Firefly Reporting

        ## Import Transaction CSV
        """
    )
    return


@app.cell
def _(mo):
    file = mo.ui.file(
        label="Select Transaction CSV",
        filetypes=[".csv"],
        kind="button",
    )

    file
    return (file,)


@app.cell
def _(file, io, mo, pd):
    mo.stop(len(file.value) == 0)

    try:
        csv_data = file.value[0].contents.decode('utf-8')
        df = pd.read_csv(io.StringIO(csv_data), parse_dates=["date"])
    except Exception as e:
        print(f"Error reading CSV data: {e}")
        df = pd.DataFrame()
    return (df,)


@app.cell
def _(df, mo):
    def get_column_values(column_name):
        _column_values = df[column_name].unique()
        _column_values = [
            value for value in _column_values if isinstance(value, str)
        ]
        _column_values.sort()

        return _column_values


    def get_column_selector(column_name):
        _column_values = get_column_values(column_name)

        return mo.ui.multiselect(options=_column_values)


    def get_column_selector_type():
        return mo.ui.radio(options=["Include", "Exclude"], inline=True)


    def get_column_array(column_name):
        return mo.ui.array(
            [
                get_column_selector_type(),
                get_column_selector(column_name),
            ]
        )


    filters = mo.ui.dictionary(
        {
            "date": mo.ui.array([mo.ui.date_range(value=(df["date"].min().date(), df["date"].max().date()))]),
            "amount": mo.ui.array([mo.ui.range_slider(
                start=df["amount"].min(),
                stop=df["amount"].max(),
                show_value=True,
            )]),
            "category": get_column_array("category"),
            "tag": get_column_array("tags"),
            "type": get_column_array("type"),
            "source_name": get_column_array("source_name"),
            "source_type": get_column_array("source_type"),
            "destination_name": get_column_array("destination_name"),
            "destination_type": get_column_array("destination_type"),
        }
    )
    return (filters,)


@app.cell
def _(filters, mo):
    displays = mo.ui.dictionary(
        {
            "date_aggregation": mo.ui.radio(
                options=["Day", "Week", "Month", "Quarter", "Year"], inline=True
            ),
            "group_by": mo.ui.dropdown(
                options=list(filters.value.keys())
            ),
        }
    )
    return (displays,)


@app.cell
def _(file, mo):
    mo.stop(len(file.value) == 0)
    mo.md("## Data operations")
    return


@app.cell
def _(displays, filters, mo):
    mo.accordion(
        {
            "Filter": mo.vstack(
                [
                    *[
                        mo.hstack(
                            [mo.md(selector), *items],
                            justify="start",
                            gap=5,
                            widths=[1, 1, 4],
                        )
                        for selector, items in filters.items()
                    ]
                ]
            ),
            "Display": mo.vstack(
                [
                    *[
                        mo.hstack(
                            [mo.md(selector), items],
                            justify="start",
                            gap=5,
                            widths=[1, 4],
                        )
                        for selector, items in displays.items()
                    ]
                ]
            ),
        }
    )
    return


@app.cell
def _(file, mo):
    mo.stop(len(file.value) == 0)
    mo.md("## Data Analysis")
    return


@app.cell
def _(df, filters, pd):
    df_filtered = df.copy()

    # Date Range Filter
    df_filtered = df_filtered[
        (df_filtered["date"] >= pd.Timestamp(filters["date"][0].value[0], tz="UTC"))
        & (df_filtered["date"] <= pd.Timestamp(filters["date"][0].value[1], tz="UTC"))
    ]

    # Amount Range Filter
    df_filtered = df_filtered[
        (df_filtered["amount"] >= filters["amount"][0].value[0])
        & (df_filtered["amount"] <= filters["amount"][0].value[1])
    ]


    def apply_filter(_df, column_name):
        selector_array = filters[column_name]
        selector_type = selector_array[0].value
        selector_values = selector_array[1].value

        if selector_type is None or not selector_values:
            return _df

        if selector_type == "Include":
            _df = _df[_df[column_name].isin(selector_values)]
        elif selector_type == "Exclude":
            _df = _df[~_df[column_name].isin(selector_values)]
        return _df


    # Category Filter
    df_filtered = apply_filter(df_filtered, "category")
    df_filtered = apply_filter(df_filtered, "tag")
    df_filtered = apply_filter(df_filtered, "type")
    df_filtered = apply_filter(df_filtered, "source_name")
    df_filtered = apply_filter(df_filtered, "source_type")
    df_filtered = apply_filter(df_filtered, "destination_name")
    df_filtered = apply_filter(df_filtered, "destination_type")
    return (df_filtered,)


@app.cell
def _(df_filtered, displays, pd):
    df_displayed = df_filtered.copy()

    # Date Aggregation
    if displays["date_aggregation"].value == "Day":
        df_displayed["date_aggregation"] = pd.to_datetime(df_displayed["date"], utc=True).dt.strftime('%Y-%m-%d')
    elif displays["date_aggregation"].value == "Week":
        df_displayed["date_aggregation"] = pd.to_datetime(df_displayed["date"], utc=True).dt.strftime('%Y-W%U')
    elif displays["date_aggregation"].value == "Month":
        df_displayed["date_aggregation"] = pd.to_datetime(df_displayed["date"], utc=True).dt.strftime('%Y-%m')
    elif displays["date_aggregation"].value == "Quarter":
        df_displayed["date_aggregation"] = pd.to_datetime(df_displayed["date"], utc=True).dt.strftime('%Y-Q%q')
    elif displays["date_aggregation"].value == "Year":
        df_displayed["date_aggregation"] = pd.to_datetime(df_displayed["date"], utc=True).dt.strftime('%Y')
    else:
        df_displayed["date_aggregation"] = pd.to_datetime(df_displayed["date"], utc=True).dt.strftime('%Y-%m-%d')

    # Group By
    group_by = displays["group_by"].value if displays["group_by"].value else None

    if group_by:
        df_grouped = df_displayed.pivot_table(
            index=group_by,
            columns="date_aggregation",
            values="amount",
            aggfunc="sum",
            fill_value=0
        )
        df_grouped = df_grouped.reset_index()  # Make the index a column
    else:
        df_grouped = df_displayed.groupby("date_aggregation")["amount"].sum().reset_index()

    df_grouped
    return


if __name__ == "__main__":
    app.run()
