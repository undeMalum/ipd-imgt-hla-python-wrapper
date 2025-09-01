from fastapi import FastAPI
import httpx

app = FastAPI()


@app.get('/')
async def connect_to_db():
    URL = 'https://www.ebi.ac.uk/cgi-bin/ipd/api/allele?query=startsWith(name, "B*27")'
    
    response = httpx.get(URL).json()
    
    next_page = response["meta"]["next"]
    
    while next_page is None:
        temp_response = httpx.get(URL + next_page).json()
        
        print(temp_response)
        
        response["data"].extend(temp_response["data"])
        
        next_page = temp_response["meta"]["next"]
    

    return response
