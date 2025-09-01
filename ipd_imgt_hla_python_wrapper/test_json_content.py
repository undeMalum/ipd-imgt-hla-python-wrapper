import marimo

__generated_with = "0.15.2"
app = marimo.App(width="medium")


@app.cell
def _():
    from pathlib import Path
    import json
    return Path, json


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
    import marimo as mo
    return


if __name__ == "__main__":
    app.run()
