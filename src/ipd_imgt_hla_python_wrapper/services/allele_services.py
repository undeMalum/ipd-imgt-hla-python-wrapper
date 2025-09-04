import httpx

from ipd_imgt_hla_python_wrapper.services.allele_settings import (
    AllelesNames,
    AllelesSequences,
    SequenceTypes,
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


def donwload_over_1000_alele(
    allele_accession_list: list[str], seq_type: SequenceTypes = SequenceTypes.GENOMIC
) -> AllelesSequences:
    pass


if __name__ == "__main__":
    import asyncio

    query = 'startsWith(name, "B*27")'

    data = asyncio.run(fetch_all_alleles_from_query(query))

    accession_list = retrieve_allele_accession_numbers(data)
    print(accession_list)
