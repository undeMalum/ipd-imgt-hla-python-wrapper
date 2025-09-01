from fastapi import FastAPI
import httpx

app = FastAPI()


@app.get('/')
async def connect_to_db():
    response = httpx.get('https://www.ebi.ac.uk/cgi-bin/ipd/api/allele?query=startsWith(name, "B*27")')
    return response
