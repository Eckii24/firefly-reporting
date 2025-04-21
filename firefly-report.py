

import marimo

__generated_with = "0.13.0"
app = marimo.App(width="medium")


@app.cell
def _():
    import pandas as pd

    df = pd.read_csv("../2025_04_21_transaction_export.csv")
    return df, pd


@app.cell
def _(df, pd):
    df['account_name'] = df['source_name']
    df['account_type'] = df['source_type']
    df['corrected_amount'] = -abs(df['amount'])
    df['date'] = pd.to_datetime(df['date'], utc=True)
    return


@app.cell
def _(df, pd):
    # Create a copy of the original DataFrame
    _df_duplicated = df.copy()

    # Override account_name and account_type with destination_name and destination_type
    _df_duplicated['account_name'] = _df_duplicated['destination_name']
    _df_duplicated['account_type'] = _df_duplicated['destination_type']
    _df_duplicated['corrected_amount'] = abs(_df_duplicated['amount'])

    # Concatenate the original and modified DataFrames
    df_enhanced = pd.concat([df, _df_duplicated], ignore_index=True)
    return (df_enhanced,)


@app.cell
def _(df_enhanced):
    import marimo as mo

    categories = df_enhanced["category"].unique()
    categories = [c for c in categories if isinstance(c, str)]
    categories.sort()

    tags = df_enhanced["tags"].unique()
    tags = [c for c in tags if isinstance(c, str)]
    tags.sort()

    types = df_enhanced["type"].unique()
    types = [c for c in types if isinstance(c, str)]
    types.sort()

    account_types = df_enhanced["account_type"].unique()
    account_types = [at for at in account_types if isinstance(at, str)]
    account_types.sort()


    category_selector = mo.ui.dropdown(
        options=categories,
        label="Category",
    )

    tag_selector = mo.ui.dropdown(
        options=tags,
        label="Tag",
    )

    type_selector = mo.ui.dropdown(
        options=types,
        label="Type",
    )

    account_name_selectors = {}
    for account_type in account_types:
        account_names = df_enhanced[df_enhanced["account_type"] == account_type]["account_name"].unique()
        account_names = [name for name in account_names if isinstance(name, str)]
        account_names.sort()
        account_name_selectors[account_type] = mo.ui.dropdown(
            options=account_names,
            label=f"Account Name ({account_type})",
        )

    account_type_selector = mo.ui.dropdown(
        options=account_types,
        label="Account Type",
    )
    return (
        account_name_selectors,
        account_type_selector,
        category_selector,
        mo,
        tag_selector,
        type_selector,
    )


@app.cell
def _(
    account_name_selectors,
    account_type_selector,
    category_selector,
    mo,
    tag_selector,
    type_selector,
):
    mo.vstack(
        [
            category_selector,
            *[selector for selector in account_name_selectors.values()],
            tag_selector,
            type_selector,
            account_type_selector,
        ]
    )
    return


@app.cell
def _(df_enhanced, mo):
    date_range_selector = mo.ui.date_range(
        value=(df_enhanced["date"].min().date(), df_enhanced["date"].max().date()),
        label="Date Range",
    )

    date_range_selector
    return


@app.cell
def _(
    account_type_selector,
    category_selector,
    mo,
    tag_selector,
    type_selector,
):
    filter_types = {
        "category": category_selector,
        "tag": tag_selector,
        "type": type_selector,
        "account_type": account_type_selector,
    }

    filter_selections = mo.ui.multiselect(
        options=list(filter_types.keys()), label="Select Filters"
    )


    def filter_uis(selected_filters):
        uis = []
        filter_configs = {}
        for filter_name in selected_filters:
            selector = filter_types[filter_name]
            include_exclude = mo.ui.radio(
                options=["Include", "Exclude"], value="Include", label="Include/Exclude"
            )
            uis.append(mo.hstack([selector, include_exclude]))
            filter_configs[filter_name] = (selector, include_exclude)

        return mo.vstack(*uis), filter_configs
    return filter_selections, filter_uis


@app.cell
def _(filter_selections, filter_uis, mo):
    def _filter_ui(filter_selections_value):
        filter_ui, _filter_configs = filter_uis(filter_selections_value)
        return filter_ui

    mo.vstack([_filter_ui(filter_selections.value)])
    return


if __name__ == "__main__":
    app.run()
