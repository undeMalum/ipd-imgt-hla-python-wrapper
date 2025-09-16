import logging
import asyncio
from asyncio import Semaphore

import httpx
from fastapi import HTTPException
from ipd_imgt_hla_python_wrapper.services.allele_settings import (
    AllelesNames,
    AllelesSequences,
    SequenceTypes,
    Sequence,
    SingleAllele,
    MetaData,
)
from ipd_imgt_hla_python_wrapper.urls import ALLELE_URL, DOWNLOAD_URL

logger = logging.getLogger(__name__)


async def fetch_all_alleles_from_query(query: str) -> AllelesNames:
    results = []
    next_page = f"?query={query}"

    async with httpx.AsyncClient(timeout=30) as client:
        while next_page is not None:
            try:
                response = await client.get(ALLELE_URL + next_page)

                response.raise_for_status()

                payload = response.json()

                results.extend(payload["data"])

                next_page = payload["meta"]["next"]
            except httpx.TimeoutException as e:
                logger.error(f"Timeout fetching alleles for the query {query}: {e}")
                raise HTTPException(
                    status_code=504,
                    detail=f"Timeout fetching alleles for the query {query}: {e}",
                )
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error fetching alleles for the query {query}: {e}")
                raise HTTPException(
                    status_code=e.response.status_code,
                    detail=f"HTTP error fetching alleles for the query {query}: {e}",
                )
            except httpx.RequestError as e:
                logger.error(f"Network error for the query {query}: {e}")
                raise HTTPException(
                    status_code=502, detail=f"Network error for the query {query}: {e}"
                )

    logger.info(f"Successfully fetched {len(results)} for the query: {query}")

    return AllelesNames(
        data=[SingleAllele(**allele) for allele in results],
        meta=MetaData(total=payload["meta"]["total"]),
    )


async def download_alleles(
    query: str, seq_type: SequenceTypes = SequenceTypes.GENOMIC
) -> AllelesSequences:
    params = {"query": query, "type": seq_type.value}

    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.get(DOWNLOAD_URL, params=params)
            response.raise_for_status()

        except httpx.TimeoutException as e:
            logger.error(
                f"Timeout fetching alleles for the query {query} and sequence type {seq_type}: {e}"
            )
            raise HTTPException(
                status_code=504,
                detail=f"Timeout fetching alleles for the query {query} and sequence type {seq_type}: {e}",
            )
        except httpx.HTTPError as e:
            logger.error(
                f"HTTP error fetching alleles for the query {query} and sequence type {seq_type}: {e}"
            )
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"HTTP error fetching alleles for the query {query} and sequence type {seq_type}: {e}",
            )
        except httpx.RequestError as e:
            logger.error(
                f"Network error for the query {query} and sequence type {seq_type}: {e}"
            )
            raise HTTPException(
                status_code=502,
                detail=f"Network error for the query {query} and sequence type {seq_type}: {e}",
            )

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


async def fetch_single_allele(
    allele_accession: str, client: httpx.AsyncClient, semaphore: Semaphore
) -> dict | None:
    async with semaphore:
        try:
            single_allele_url = f"{ALLELE_URL}/{allele_accession}"
            response = await client.get(single_allele_url)
            response.raise_for_status()
            return response.json()
        except httpx.TimeoutException as e:
            logger.warning(f"Timeout fetching allele {allele_accession}: {e}")
            return None
        except httpx.HTTPError as e:
            logger.warning(f"HTTP error fetching allele {allele_accession}: {e}")
            return None
        except httpx.RequestError as e:
            logger.warning(
                f"Request failed for allele {allele_accession} with query {single_allele_url}: {e}"
            )
            return None


async def download_over_1000_alleles(
    allele_accession_list: list[str],
    seq_type: SequenceTypes = SequenceTypes.GENOMIC,
    max_concurrent_requests: int = 10,
) -> AllelesSequences:
    logger.info(f"Start the download of {len(allele_accession_list)} allele sequences.")

    semaphore = Semaphore(max_concurrent_requests)

    async with httpx.AsyncClient(timeout=60.0) as client:
        tasks = [
            fetch_single_allele(acc, client, semaphore) for acc in allele_accession_list
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
    query = 'startsWith(name, "B")'

    data = await fetch_all_alleles_from_query(query)

    accession_list = retrieve_allele_accession_numbers(data)

    downloaded_sequences = await download_over_1000_alleles(accession_list)
    print(downloaded_sequences)


if __name__ == "__main__":
    asyncio.run(main())
