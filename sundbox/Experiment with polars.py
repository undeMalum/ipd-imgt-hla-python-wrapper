import marimo

__generated_with = "0.15.2"
app = marimo.App(width="medium")


@app.cell
def _():
    URL = "https://www.ebi.ac.uk/cgi-bin/ipd/api/allele"
    return (URL,)


@app.cell
def _():
    params = {"query": 'startsWith(name, "B*27")', "type": "genomic"}
    params
    return (params,)


@app.cell
def _(URL, httpx, params):
    response_download = httpx.get(URL + "/download", params=params)
    response_download.url
    return (response_download,)


@app.cell
def _(response_download):
    response_download.text
    type(response_download.text)
    return


@app.cell
def _(response_download):
    from io import StringIO

    data = StringIO(response_download.text)
    data
    return (data,)


@app.cell
def _(data, pl):
    df = pl.scan_csv(data, has_header=False, eol_char=">", separator=" ")
    df
    return (df,)


@app.cell
def _(df):
    renamed_col_df = df.rename({"column_1": "allele_name", "column_2": "sequences"})
    renamed_col_df
    return (renamed_col_df,)


@app.cell
def _(pl, renamed_col_df):
    extract_allele_name = renamed_col_df.with_columns(
        pl.col("allele_name")
        .str.extract(r"\|(.*?)\|", 1)  # capture everything between first and second |
        .alias("allele_name")
    )

    extract_allele_name
    return (extract_allele_name,)


@app.cell
def _(extract_allele_name, pl):
    remove_bp = extract_allele_name.with_columns(
        pl.col("sequences").str.replace("bp", "").alias("sequences")
    )

    remove_bp
    return


@app.cell
def _(pl, renamed_col_df):
    both_simultaneously = renamed_col_df.with_columns(
        pl.col("allele_name").str.extract(r"\|(.*?)\|", 1).alias("allele_name"),
        pl.col("sequences").str.replace("bp", "").alias("sequences"),
    )
    both_simultaneously
    type(both_simultaneously)
    return (both_simultaneously,)


@app.cell
def _(both_simultaneously):
    json = both_simultaneously.collect().write_json()
    json
    return


@app.cell
def _():
    import marimo as mo
    import httpx
    import polars as pl

    return httpx, pl


if __name__ == "__main__":
    app.run()
