import marimo

__generated_with = "0.15.2"
app = marimo.App(width="medium")


@app.function
def foo():
    i = 0
    for j in range(20):
        if j == 10:
            raise ValueError
        i += j
    return i


@app.cell
def _():
    a = foo()
    return


@app.cell
def _():
    import marimo as mo

    return


if __name__ == "__main__":
    app.run()
