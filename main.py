# main.py
from fastapi import FastAPI, HTTPException
from crud import get_random_properties
from models import Property
from typing import List

app = FastAPI()

@app.get("/recommendedProperties", response_model=List[Property])
async def recommended_properties():
    properties = await get_random_properties()
    if not properties:
        raise HTTPException(status_code=404, detail="No properties found")
    return properties

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
