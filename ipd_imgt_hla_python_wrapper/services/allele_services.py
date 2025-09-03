import httpx

from allele_settings import AllelesNames, AllelesSequences, SequenceTypes
from ..urls import ALLELE_URL, DOWNLOAD_URL


async def fetch_all_alleles_from_query(query: str) -> AllelesNames:
    results = []
    next_page = f"?query={query}"

    async with httpx.AsyncClient() as client:
        while next_page is not None:
            response = await client.get(ALLELE_URL + next_page)

            payload = response.json()

            results.extend(payload["data"])

            next_page = payload["meta"]["next"]

    return {"data": results, "meta": {"total": next_page["meta"]["total"]}}


async def download_alleles(
    query: str, seq_type: SequenceTypes = SequenceTypes.GENOMIC
) -> AllelesSequences:
    params = {"query": query, "type": seq_type.value}

    async with httpx.AsyncClient() as client:
        response = await client.get(DOWNLOAD_URL, params=params)

    alleles = response.text.split(">")[1:]

    sequences = []

    for allele in alleles:
        allele_metadata, _, sequece = allele.split()
        allele_metadata = allele_metadata.split("|")
        allele_name = allele_metadata[1]

        sequences.append({"allele_name": allele_name, "sequence": sequece})

    return {"sequences": sequences}
