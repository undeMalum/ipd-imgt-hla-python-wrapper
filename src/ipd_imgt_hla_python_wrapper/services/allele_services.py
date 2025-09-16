import logging
import asyncio
from asyncio import Semaphore
from typing import Callable, TypeVar, ParamSpec
from functools import wraps

import httpx
from fastapi import HTTPException
from ipd_imgt_hla_python_wrapper.services.allele_settings import (
    AllelesNames,
    AllelesSequences,
    SequenceTypes,
    Sequence,
    SingleAllele,
    MetaData,
    APIOperations,
)
from ipd_imgt_hla_python_wrapper.urls import ALLELE_URL, DOWNLOAD_URL

logger = logging.getLogger(__name__)

P = ParamSpec("P")
T = TypeVar("T")


def handle_http_errors(operation_name: APIOperations):
    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            try:
                return await func(*args, **kwargs)
            except httpx.TimeoutException as e:
                logger.error(f"Timeout while: {operation_name}: {e}")
                raise HTTPException(
                    status_code=504,
                    detail=f"Timeout while: {operation_name}: {e}",
                )
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error while {operation_name}: {e}")
                raise HTTPException(
                    status_code=e.response.status_code,
                    detail=f"HTTP error while {operation_name}: {e}",
                )
            except httpx.RequestError as e:
                logger.error(f"Network error while {operation_name}: {e}")
                raise HTTPException(
                    status_code=502, detail=f"Network error while {operation_name}: {e}"
                )

        return wrapper

    return decorator


def handle_single_allele_http_errors(operation_name: APIOperations):
    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            try:
                return await func(*args, **kwargs)
            except httpx.TimeoutException as e:
                logger.warning(f"Timeout while: {operation_name}: {e}")
                return None
            except httpx.HTTPStatusError as e:
                logger.warning(f"HTTP error while {operation_name}: {e}")
                return None
            except httpx.RequestError as e:
                logger.warning(f"Network error while {operation_name}: {e}")
                return None

        return wrapper

    return decorator


@handle_http_errors(APIOperations.FETCHING_ALLELES_FROM_QUERY.value)
async def fetch_all_alleles_from_query(
    client: httpx.AsyncClient, query: str
) -> AllelesNames:
    results = []
    next_page = f"?query={query}"

    while next_page is not None:
        response = await client.get(ALLELE_URL + next_page)

        response.raise_for_status()

        payload = response.json()

        results.extend(payload["data"])

        next_page = payload["meta"]["next"]

    logger.info(f"Successfully fetched {len(results)} for the query: {query}")

    return AllelesNames(
        data=[SingleAllele(**allele) for allele in results],
        meta=MetaData(total=payload["meta"]["total"]),
    )


@handle_http_errors(APIOperations.DOWNLOADING_ALLELE_SEQUENES.value)
async def download_alleles(
    client: httpx.AsyncClient,
    query: str,
    seq_type: SequenceTypes = SequenceTypes.GENOMIC,
) -> AllelesSequences:
    params = {"query": query, "type": seq_type.value}

    response = await client.get(DOWNLOAD_URL, params=params)
    response.raise_for_status()

    logger.info(
        f"Successfully downloaded sequences for the query {query} with the sequence type {seq_type}"
    )

    alleles = response.text.split(">")[1:]

    sequences = []

    for allele in alleles:
        allele_metadata, _, sequence = allele.split()
        allele_metadata = allele_metadata.split("|")
        allele_name = allele_metadata[1]

        sequences.append(Sequence(allele_name=allele_name, sequence=sequence))

    logger.info(
        f"Successfully transformed {len(sequences)} sequences for the query {query} and the sequence type {seq_type} from a text file into json."
    )

    return AllelesSequences(sequences=sequences)


def retrieve_allele_accession_numbers(allele_names: AllelesNames) -> list[str]:
    allele_accession_list = [allele.accession for allele in allele_names.data]

    logger.info(
        f"Successfully retrieved accession number for {len(allele_accession_list)} alleles."
    )

    return allele_accession_list


@handle_single_allele_http_errors(APIOperations.FETCHING_SINGLE_ALLELE.value)
async def fetch_single_allele(
    client: httpx.AsyncClient, semaphore: Semaphore, allele_accession: str
) -> dict | None:
    async with semaphore:
        single_allele_url = f"{ALLELE_URL}/{allele_accession}"
        response = await client.get(single_allele_url)
        response.raise_for_status()
        return response.json()


async def download_over_1000_alleles(
    client: httpx.AsyncClient,
    allele_accession_list: list[str],
    seq_type: SequenceTypes = SequenceTypes.GENOMIC,
    max_concurrent_requests: int = 10,
) -> AllelesSequences:
    logger.info(f"Start the download of {len(allele_accession_list)} allele sequences.")

    semaphore = Semaphore(max_concurrent_requests)

    tasks = [
        fetch_single_allele(client, semaphore, acc) for acc in allele_accession_list
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    sequences = []

    for result in results:
        if result and isinstance(result, dict) and result.get("status") != "Deleted":
            sequence = result["sequence"].get(seq_type.value)
            if sequence:
                sequences.append(
                    Sequence(allele_name=result["name"], sequence=sequence)
                )

    logger.info(f"Downloaded {len(sequences)}/{len(allele_accession_list)} sequences.")

    return AllelesSequences(sequences=sequences)


async def main() -> None:
    query = 'and(startsWith(name, "B*27"), eq(status, "Public"))'

    async with httpx.AsyncClient() as client:
        data = await fetch_all_alleles_from_query(client, query)

        accession_list = retrieve_allele_accession_numbers(data)

        downloaded_sequences = await download_over_1000_alleles(client, accession_list)

    print(downloaded_sequences)


if __name__ == "__main__":
    asyncio.run(main())
