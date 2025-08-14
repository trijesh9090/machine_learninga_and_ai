import os
import arxiv
import requests
from datetime import datetime, timedelta, timezone
from typing import List

import urllib.parse

from dotenv import load_dotenv
from agents.base import Agent
from models.newsletter import Newsletter

load_dotenv()


class ScraperAgent(Agent):
    def __init__(self):
        self.news_api_key = os.getenv("NEWS_API_KEY")
        self.gnews_api_key = os.getenv("GNEWS_API_KEY")
        self.state: List[Newsletter] = []

    def fetch_news_api(
        self, query: str = "Agentic AI", num_articles: int = 10
    ) -> List[Newsletter]:
        from_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        to_date = datetime.now().strftime("%Y-%m-%d")

        url = (
            f"https://newsapi.org/v2/everything?"
            f"q={query}&"
            f"pageSize={num_articles}&"
            f"sortBy=publishedAt&"
            f"language=en&"
            f"from={from_date}&to={to_date}&"
            f"apiKey={self.news_api_key}"
        )

        response = requests.get(url)

        try:
            response.raise_for_status()
        except requests.HTTPError as e:
            print(f"[NewsAPI] HTTP error: {e}")
            print(f"[NewsAPI] Raw response: {response.text}")
            return []

        data = response.json()
        articles = data.get("articles", [])

        if not articles:
            print("[NewsAPI] No articles found. Full response:")
            print(data)

        news_items = []
        for article in articles:
            try:
                news_items.append(
                    Newsletter(
                        title=article["title"],
                        description=article.get("description"),
                        url=article["url"],
                        source=article["source"]["name"],
                        published_at=datetime.strptime(
                            article["publishedAt"], "%Y-%m-%dT%H:%M:%SZ"
                        ).replace(tzinfo=timezone.utc),
                        content=article.get("content"),
                        type="news",
                    )
                )
            except Exception as e:
                print(f"[NewsAPI] Error parsing article: {e}")

        self.state.extend(news_items)
        return news_items

    def fetch_gnews(
        self, query: str = "Agentic AI", num_articles: int = 10
    ) -> List[Newsletter]:
        # Limit to past 1–2 days for free-tier compatibility
        from_date = (
            (datetime.now(timezone.utc) - timedelta(days=2))
            .isoformat(timespec="seconds")
            .replace("+00:00", "Z")
        )
        to_date = (
            datetime.now(timezone.utc)
            .isoformat(timespec="seconds")
            .replace("+00:00", "Z")
        )

        raw_query = '"agentic AI" OR "AI agents" OR "autonomous agents"'
        encoded_query = urllib.parse.quote(query)

        url = (
            f"https://gnews.io/api/v4/search?"
            f"q={encoded_query}&"
            f"lang=en&"
            f"max={num_articles}&"
            f"sortby=publishedAt&"
            f"from={from_date}&to={to_date}&"
            f"token={self.gnews_api_key}"
        )

        response = requests.get(url)

        try:
            response.raise_for_status()
        except requests.HTTPError as e:
            print(f"[GNews] HTTP error: {e}")
            print(f"[GNews] Raw response: {response.text}")
            return []

        data = response.json()
        articles = data.get("articles", [])

        if not articles:
            print("[GNews] No articles found. Full response:")
            print(data)

        news_items = []
        for article in articles:
            try:
                news_items.append(
                    Newsletter(
                        title=article["title"],
                        description=article.get("description"),
                        url=article["url"],
                        source=article["source"]["name"],
                        published_at=datetime.strptime(
                            article["publishedAt"], "%Y-%m-%dT%H:%M:%S%z"
                        ),
                        content=None,
                        type="news",
                    )
                )
            except Exception as e:
                print(f"[GNews] Error parsing article: {e}")

        self.state.extend(news_items)
        return news_items

    def fetch_arxiv_papers(
        self, query: str = "Agentic AI", num_papers: int = 5
    ) -> List[Newsletter]:
        search = arxiv.Search(
            query=query,
            max_results=num_papers,
            sort_by=arxiv.SortCriterion.SubmittedDate,
        )

        one_week_ago = datetime.now(timezone.utc) - timedelta(days=7)

        papers = []
        for result in search.results():
            if result.published > one_week_ago:
                papers.append(
                    Newsletter(
                        title=result.title,
                        description=result.summary,
                        author=", ".join([a.name for a in result.authors]),
                        published_at=result.published,
                        url=result.pdf_url,
                        type="research",
                    )
                )

        self.state.extend(papers)
        return papers

    def run(self, *args, **kwargs) -> List[Newsletter]:
        self.state.clear()

        query = kwargs.get("query", "Agentic AI")
        num_articles = kwargs.get("num_articles", 10)
        num_papers = kwargs.get("num_papers", 5)

        newsapi_results = self.fetch_news_api(query=query, num_articles=num_articles)
        gnews_results = self.fetch_gnews(query=query, num_articles=num_articles)
        # arxiv_results = self.fetch_arxiv_papers(query=query, num_papers=num_papers)

        return gnews_results + newsapi_results
