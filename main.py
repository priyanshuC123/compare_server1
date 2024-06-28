from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl
import requests
from bs4 import BeautifulSoup
from fastapi.middleware.cors import CORSMiddleware
import time
import random
import logging

app = FastAPI()

# CORS (Cross-Origin Resource Sharing) middleware configuration
origins = [
    "http://localhost",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

class ProductURLs(BaseModel):
    url1: HttpUrl
    url2: HttpUrl

# user_agents = [
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36"
# ]

# logging.basicConfig(level=logging.INFO)

# def scrape_amazon_product_highlights(url):
#     max_retries = 5
#     for attempt in range(max_retries):
#         try:
#             headers = {
#                 "User-Agent": random.choice(user_agents)
#             }
#             page = requests.get(url, headers=headers)
#             page.raise_for_status()  # Raises an HTTPError for bad responses

#             soup = BeautifulSoup(page.text, "html.parser")
#             titles = soup.find_all("span", class_="a-size-large product-title-word-break")
#             specs = soup.find_all("ul", class_="a-unordered-list a-vertical a-spacing-mini")    

#             highlights = [title.text for title in titles] + [spec.text for spec in specs] 

#             if highlights:
#                 return highlights

#             logging.info(f"No highlights found on attempt {attempt + 1} for URL {url}")
#             if attempt < max_retries - 1:
#                 time.sleep(2 ** attempt)  # Exponential backoff

#         except requests.RequestException as e:
#             logging.error(f"RequestException occurred on attempt {attempt + 1} for URL {url}: {str(e)}")
#             if attempt < max_retries - 1:
#                 time.sleep(2 ** attempt)  # Exponential backoff
#                 continue
#             else:
#                 raise HTTPException(status_code=400, detail=str(e))
#         except Exception as e:
#             logging.error(f"Exception occurred on attempt {attempt + 1} for URL {url}: {str(e)}")
#             raise HTTPException(status_code=500, detail=str(e))

#     raise HTTPException(status_code=500, detail="Unable to retrieve product highlights after multiple attempts")

def scrape_flipkart_product_highlights(url):
    try:
        page = requests.get(url)
        page.raise_for_status()  # Raises an HTTPError for bad responses

        soup = BeautifulSoup(page.text, "html.parser")
        titles = soup.find_all("span", class_="VU-ZEz")
        specs = soup.find_all("li", class_="_7eSDEz")
        

        highlights = [title.text for title in titles] + [spec.text for spec in specs]  # Extract the text for each spec

        return highlights

    except requests.RequestException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Product Comparison API"}

@app.post("/")
async def compare_products(urls: ProductURLs):
    try:
        
        product1_highlights = scrape_flipkart_product_highlights(urls.url1)
        product2_highlights = scrape_flipkart_product_highlights(urls.url2)
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {
        "product1": {
            "url": urls.url1,
            "highlights": product1_highlights
        },
        "product2": {
            "url": urls.url2,
            "highlights": product2_highlights
        }
    }

# Run the FastAPI application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
