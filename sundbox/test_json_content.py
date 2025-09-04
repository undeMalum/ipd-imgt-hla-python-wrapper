import marimo

__generated_with = "0.15.2"
app = marimo.App(width="medium")


@app.cell
def _():
    from pathlib import Path
    import json
    import httpx
    import polars as pl

    return Path, httpx, json


@app.cell
def _(Path, json):
    json_path = Path(__file__).resolve() / "../../archives/response.json"

    with open(json_path, "r") as json_file:
        json_data = json.load(json_file)
    return (json_data,)


@app.cell
def _(json_data):
    json_data
    return


@app.cell
def _(json_data):
    json_data["meta"]["next"]
    return


@app.cell
def _():
    URL = "https://www.ebi.ac.uk/cgi-bin/ipd/api/allele"
    return (URL,)


@app.cell
def _():
    initial_call = '?query=startsWith(name, "B*27")'
    return (initial_call,)


@app.cell
def _(URL, httpx, initial_call):
    response = httpx.get(URL + initial_call).json()

    next_page = response["meta"]["next"]

    while next_page is not None:
        temp_response = httpx.get(URL + next_page).json()

        print(temp_response["data"])

        response["data"].extend(temp_response["data"])

        next_page = temp_response["meta"]["next"]
    return next_page, response


@app.cell
def _(next_page):
    next_page
    return


@app.cell
def _(response):
    response
    return


@app.cell
def _(response):
    len(response["data"])
    return


@app.cell
def _(URL):
    download_call = URL + "/download"  # + initial_call + "&type=genomic"
    download_call
    return (download_call,)


@app.cell
def _():
    params = {"query": 'startsWith(name, "B*27")', "type": "genomic"}
    params
    return (params,)


@app.cell
def _(download_call, httpx, params):
    response_download = httpx.get(download_call, params=params)
    response_download.url
    return (response_download,)


@app.cell
def _(response_download):
    response_download.text
    return


@app.cell
def _(response_download):
    alleles = response_download.text.split(">")[1:]
    alleles
    return (alleles,)


@app.cell
def _(alleles):
    sequences_json = {"sequences": []}

    for allele in alleles:
        allele_metadata, _, sequece = allele.split()
        allele_metadata = allele_metadata.split("|")
        allele_name = allele_metadata[1]

        sequences_json["sequences"].append(
            {"allele_name": allele_name, "sequence": sequece}
        )

    sequences_json
    return


@app.cell
def _():
    import marimo as mo

    return


if __name__ == "__main__":
    app.run()
