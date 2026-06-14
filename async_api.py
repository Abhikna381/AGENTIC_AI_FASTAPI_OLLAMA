import asyncio
from fastapi import FastAPI


app = FastAPI()



@app.get("/wait")
async def wait(seconds: int):
    await asyncio.sleep(seconds) # Non-blocking sleep
    return {"message": f"Waited for {seconds} seconds"}