from pydantic import BaseModel
import httpx

class SingleAllele(BaseModel):
    accession: str
    name: str


class MetaData(BaseModel):
    next: str | None
    prev: str | None
    sort: str | None
    total: int


class Sequence(BaseModel):
    allele_name: str
    sequence: str


class AllelesNames(BaseModel):
    data: list[SingleAllele]
    meta: MetaData
    
    
class AllelesSequences(BaseModel):
    sequences: list[Sequence]


async def fetch_all_alleles_from_query(query: str) -> AllelesNames:
    pass
