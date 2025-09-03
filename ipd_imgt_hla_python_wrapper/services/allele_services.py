import httpx

from allele_settings import AllelesNames, AllelesSequences
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
