from fastapi import FastAPI
import httpx

app = FastAPI()


@app.get("/")
async def connect_to_db():
    URL = "https://www.ebi.ac.uk/cgi-bin/ipd/api/allele"
    initial_call = '?query=startsWith(name, "B*27")'

    response = httpx.get(URL + initial_call).json()

    next_page = response["meta"]["next"]

    while next_page is not None:
        temp_response = httpx.get(URL + next_page).json()

        response["data"].extend(temp_response["data"])

        next_page = temp_response["meta"]["next"]

    return response


@app.get("/downloads")
async def download_alleles():
    DOWNLOAD_URL = "https://www.ebi.ac.uk/cgi-bin/ipd/api/allele/download"

    params = {"query": 'startsWith(name, "B*27")', "type": "genomic"}

    response_download = httpx.get(DOWNLOAD_URL, params=params)

    alleles = response_download.text.split(">")[1:]

    sequences_json = {"sequences": []}

    for allele in alleles:
        allele_metadata, _, sequece = allele.split()
        allele_metadata = allele_metadata.split("|")
        allele_name = allele_metadata[1]

        sequences_json["sequences"].append(
            {"allele_name": allele_name, "sequence": sequece}
        )

    return sequences_json
