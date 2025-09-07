from fastapi import FastAPI

from src.ipd_imgt_hla_python_wrapper.services.allele_services import (
    fetch_all_alleles_from_query,
    download_alleles,
    donwload_over_1000_alele,
    retrieve_allele_accession_numbers,
)

app = FastAPI()


@app.get("/")
async def get_all_alleles():
    query = 'startsWith(name, "B*27")'
    data = await fetch_all_alleles_from_query(query)

    return data


@app.get("/downloads")
async def get_allele_sequences():
    query = 'startsWith(name, "B*27")'
    data = await download_alleles(query)

    return data


@app.get("/downloads/large")
async def get_large_number_sequences():
    query = 'startsWith(name, "B")'

    allele_names = await fetch_all_alleles_from_query(query)
    allele_list = retrieve_allele_accession_numbers(allele_names)
    data = await donwload_over_1000_alele(allele_list)

    return data
