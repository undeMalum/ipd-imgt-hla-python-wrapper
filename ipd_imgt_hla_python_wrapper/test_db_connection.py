from fastapi import FastAPI
import httpx

app = FastAPI()


@app.get('/')
async def connect_to_db():
    URL = 'https://www.ebi.ac.uk/cgi-bin/ipd/api/allele'
    initial_call = '?query=startsWith(name, "B*27")'
    
    response = httpx.get(URL + initial_call).json()
    
    next_page = response["meta"]["next"]
    
    while next_page is None:
        temp_response = httpx.get(URL + next_page).json()
        
        response["data"].extend(temp_response["data"])
        
        next_page = temp_response["meta"]["next"]
    

    return response
