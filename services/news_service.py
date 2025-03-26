# newsapi_service.py
import os
import requests
from datetime import datetime, timedelta

NEWSAPI_API_KEY = os.getenv("NEWSAPI_API_KEY")

class NewsAPIService:
    BASE_URL = "https://newsapi.org/v2/everything"

    def __init__(self):
        self.api_key = os.getenv("NEWSAPI_API_KEY")
        if not self.api_key:
            raise ValueError("NEWSAPI_API_KEY environment variable not set.")

    def fetch_articles(self, query, from_date, to_date, sort_by="popularity", page_size=20):
        params = {
            "q": query,
            "from": from_date,
            "to": to_date,
            "sortBy": sort_by,
            "language": "en",
            "pageSize": page_size,
            "apiKey": self.api_key
        }
        response = requests.get(self.BASE_URL, params=params)
        response.raise_for_status()
        return response.json()["articles"]
