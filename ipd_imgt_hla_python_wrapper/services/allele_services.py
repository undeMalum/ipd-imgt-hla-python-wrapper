from pydantic import BaseModel
import httpx


class AllelesNames(BaseModel):
    data: list[dict]
    
    
class AllelesSequences(BaseModel):
    pass


async def download_alleles() -> AllelesNames:
    pass
