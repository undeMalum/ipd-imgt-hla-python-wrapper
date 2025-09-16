import logging

from fastapi import FastAPI
import httpx

from src.ipd_imgt_hla_python_wrapper.services.allele_services import (
    fetch_all_alleles_from_query,
    download_alleles,
    download_over_1000_alleles,
    retrieve_allele_accession_numbers,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("ipd_hla_wrapper.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

app = FastAPI()


@app.get("/")
async def get_all_alleles():
    logger.info("GET '/' endpoint called.")

    query = 'startsWith(name, "B*27")'

    async with httpx.AsyncClient() as client:
        data = await fetch_all_alleles_from_query(client, query)

    return data


@app.get("/downloads")
async def get_allele_sequences():
    logger.info("GET '/downloads' endpoint called.")

    query = 'startsWith(name, "B*27")'

    async with httpx.AsyncClient() as client:
        data = await download_alleles(client, query)

    return data


@app.get("/downloads/large")
async def get_large_number_sequences():
    logger.info("GET '/downloads/large' endpoint called.")

    query = 'startsWith(name, "B")'

    async with httpx.AsyncClient() as client:
        allele_names = await fetch_all_alleles_from_query(query)
        allele_list = retrieve_allele_accession_numbers(allele_names)
        data = await download_over_1000_alleles(allele_list)

    return data
