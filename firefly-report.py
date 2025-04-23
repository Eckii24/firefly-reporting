

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
    import_button = mo.ui.run_button(label="Import")

    file = mo.ui.file(
        label="Select Transaction CSV",
        filetypes=[".csv"],
        kind="button",
    )

    mo.vstack([file, import_button])
    return file, import_button


@app.cell
def _(file, import_button, io, mo, pd):
    mo.stop(not import_button.value)

    try:
        csv_data = file.value[0].contents.decode('utf-8')
        df = pd.read_csv(io.StringIO(csv_data))
    except Exception as e:
        print(f"Error reading CSV data: {e}")
        df = pd.DataFrame()
    return (df,)


@app.cell
def _(df, pd):
    df['account_name'] = df['source_name']
    df['account_type'] = df['source_type']
    df['leg_amount'] = -abs(df['amount'])
    df['leg_type'] = "Source"
    df['date'] = pd.to_datetime(df['date'], utc=True)
    return


@app.cell
def _(df, pd):
    # Create a copy of the original DataFrame
    _df_duplicated = df.copy()

    # Override account_name and account_type with destination_name and destination_type
    _df_duplicated['account_name'] = _df_duplicated['destination_name']
    _df_duplicated['account_type'] = _df_duplicated['destination_type']
    _df_duplicated['leg_amount'] = abs(_df_duplicated['amount'])
    _df_duplicated['leg_type'] = "Destination"

    # Concatenate the original and modified DataFrames
    df_enhanced = pd.concat([df, _df_duplicated], ignore_index=True)
    return (df_enhanced,)


@app.cell
def _(df_enhanced, mo):
    def get_column_values(column_name):
        _column_values = df_enhanced[column_name].unique()
        _column_values = [value for value in _column_values if isinstance(value, str)]
        _column_values.sort()

        return _column_values

    def get_column_selector(column_name):
        _column_values = get_column_values(column_name)

        return mo.ui.multiselect(options=_column_values)

    def get_column_selector_type():
        return mo.ui.radio(options=["Include", "Exclude"], inline=True)

    def get_column_array(column_name):
        return mo.ui.array([
            get_column_selector_type(),
            get_column_selector(column_name),
        ])

    def get_column_array2(column_name_base, column_name_base_item, column_name_derived):
        _column_values = df_enhanced[df_enhanced[column_name_base] == column_name_base_item][column_name_derived].unique()
        _column_values = [value for value in _column_values if isinstance(value, str)]
        _column_values.sort()

    category = get_column_array("category")
    tag = get_column_array("tags")
    type = get_column_array("type")

    #account_name_dict2 = mo.ui.dictionary({ account_type: get_column_array2("account_type", account_type, "account_name") for account_type in get_column_values("account_type") })
    account_name_dict2 = mo.ui.dictionary({})

    account_name_dict = mo.ui.dictionary({})
    for account_type in get_column_values("account_type"):
        account_names = df_enhanced[df_enhanced["account_type"] == account_type]["account_name"].unique()
        account_names = [name for name in account_names if isinstance(name, str)]
        account_names.sort()
        account_name_dict.elements[account_type] = mo.ui.array([
            get_column_selector_type(),
            mo.ui.multiselect(options=account_names)
        ])

    date_range_selector = mo.ui.date_range(
        value=(df_enhanced["date"].min().date(), df_enhanced["date"].max().date()),
        label="Date Range",
    )

    amount_range_selector = mo.ui.range_slider(
        label="Amount Range",
        start=df_enhanced["leg_amount"].min(),
        stop=df_enhanced["leg_amount"].max(),
        show_value=True
    )
    return (
        account_name_dict,
        account_name_dict2,
        amount_range_selector,
        category,
        date_range_selector,
        tag,
        type,
    )


@app.cell
def _(mo):
    mo.md(r"""## Data operations""")
    return


@app.cell
def _(
    account_name_dict,
    account_name_dict2,
    amount_range_selector,
    category,
    date_range_selector,
    mo,
    tag,
    type,
):
    mo.accordion(
        {
            "Filter": mo.vstack(
                [
                    date_range_selector,
                    amount_range_selector,
                    mo.hstack(
                        [mo.md("Catgory"), *category],
                        justify="start",
                        gap=5,
                        widths=[1, 1, 4],
                    ),
                    mo.hstack(
                        [mo.md("Tag"), *tag],
                        justify="start",
                        gap=5,
                        widths=[1, 1, 4],
                    ),
                    mo.hstack(
                        [mo.md("Type"), *type],
                        justify="start",
                        gap=5,
                        widths=[1, 1, 4],
                    ),
                    *[
                        mo.hstack(
                            [mo.md(selector), *items],
                            justify="start",
                            gap=5,
                            widths=[1, 1, 4],
                        )
                        for selector, items in account_name_dict.items()
                    ],
                    *[
                        mo.hstack(selector, justify="start", gap=5)
                        for selector in account_name_dict2.values()
                    ],
                ]
            ),
            "Display": mo.vstack([])
        }
    )
    return


@app.cell
def _(
    account_name_dict,
    amount_range_selector,
    category,
    date_range_selector,
    df_enhanced,
    tag,
    type,
):
    _df_filtered = df_enhanced.copy()

    # Date Range Filter
    _df_filtered = _df_filtered[
        (_df_filtered["date"].dt.date >= date_range_selector.value[0])
        & (_df_filtered["date"].dt.date <= date_range_selector.value[1])
    ]

    # Amount Range Filter
    _df_filtered = _df_filtered[
        (_df_filtered["leg_amount"] >= amount_range_selector.value[0])
        & (_df_filtered["leg_amount"] <= amount_range_selector.value[1])
    ]


    def apply_filter(_df, column_name, selector_array):
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
    _df_filtered = apply_filter(_df_filtered, "category", category)

    # Tag Filter
    _df_filtered = apply_filter(_df_filtered, "tags", tag)

    # Type Filter
    _df_filtered = apply_filter(_df_filtered, "type", type)

    # Account Name Filter
    for _account_type, items in account_name_dict.items():
        _df_filtered = apply_filter(_df_filtered, "account_name", items)

    _df_filtered
    return


if __name__ == "__main__":
    app.run()
