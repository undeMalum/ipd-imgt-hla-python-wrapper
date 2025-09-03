from fastapi import FastAPI

from ipd_imgt_hla_python_wrapper.services.allele_services import (
    fetch_all_alleles_from_query,
    download_alleles,
)

app = FastAPI()


@app.get("/")
async def get_all_alleles():
    query = 'startsWith(name, "B*27")'
    data = await fetch_all_alleles_from_query(query)

    return data


@app.get()
async def get_allele_sequences():
    query = 'startsWith(name, "B*27")'
    data = await download_alleles(query)

    return data
