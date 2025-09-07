import asyncio
from asyncio import Semaphore

import httpx

from ipd_imgt_hla_python_wrapper.services.allele_settings import (
    AllelesNames,
    AllelesSequences,
    SequenceTypes,
    Sequence,
)
from ipd_imgt_hla_python_wrapper.urls import ALLELE_URL, DOWNLOAD_URL


async def fetch_all_alleles_from_query(query: str) -> AllelesNames:
    results = []
    next_page = f"?query={query}"

    async with httpx.AsyncClient() as client:
        while next_page is not None:
            response = await client.get(ALLELE_URL + next_page)

            payload = response.json()

            results.extend(payload["data"])

            next_page = payload["meta"]["next"]

    return {"data": results, "meta": {"total": payload["meta"]["total"]}}


async def download_alleles(
    query: str, seq_type: SequenceTypes = SequenceTypes.GENOMIC
) -> AllelesSequences:
    params = {"query": query, "type": seq_type.value}

    async with httpx.AsyncClient() as client:
        response = await client.get(DOWNLOAD_URL, params=params)

    alleles = response.text.split(">")[1:]

    sequences = []

    for allele in alleles:
        allele_metadata, _, sequence = allele.split()
        allele_metadata = allele_metadata.split("|")
        allele_name = allele_metadata[1]

        sequences.append({"allele_name": allele_name, "sequence": sequence})

    return {"sequences": sequences}


def retrieve_allele_accession_numbers(allele_names: AllelesNames) -> list[str]:
    allele_accession_list = [allele["accession"] for allele in allele_names["data"]]

    return allele_accession_list


async def fetch_single_allele(
    allele_accession: str, client: httpx.AsyncClient, semaphore: Semaphore
) -> dict:
    async with semaphore:
        try:
            single_allele_url = f"{ALLELE_URL}/{allele_accession}"
            response = await client.get(single_allele_url)
            response.raise_for_status()
            return response.json()
        except httpx.TimeoutException as e:
            print(f"Allele {allele_accession} raised {e}. External API timeout (504).")
            return
        except httpx.HTTPError as e:
            print(f"Allele {allele_accession} raised {e} API error.")
            return
        except ValueError as e:
            print(f"Invalid API response {e} (502). URL used {single_allele_url}")
            return


async def download_over_1000_alleles(
    allele_accession_list: list[str],
    seq_type: SequenceTypes = SequenceTypes.GENOMIC,
    sem_sumb: int = 10,
) -> AllelesSequences:
    semaphore = Semaphore(sem_sumb)

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

    return AllelesSequences(sequences=sequences)


async def main():
    query = 'startsWith(name, "B")'

    data = await fetch_all_alleles_from_query(query)

    accession_list = retrieve_allele_accession_numbers(data)

    downloaded_sequences = await download_over_1000_alleles(accession_list)
    print(downloaded_sequences)


if __name__ == "__main__":
    asyncio.run(main())
