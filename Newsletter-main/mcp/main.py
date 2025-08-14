from utils.logger import logger
from fastapi import FastAPI
from agents.scraper_agent import ScraperAgent
from agents.prioritization_agent import PrioritizationAgent
from agents.summarizer_agent import SummarizationAgent
from fastapi.responses import RedirectResponse
from agents.GmailMailer import GmailMailer

app = FastAPI()
scraper = ScraperAgent()
prioritizer = PrioritizationAgent()
summarizer = SummarizationAgent()
mailer = GmailMailer()

subscribers = ["trijesh.chodvadiya90@gmail.com"]
topic = '"agentic AI" OR "AI agents" OR "autonomous agents" OR "autonomous AI" OR "autonomous agents" OR "LLM agents"'


@app.get("/")
async def root():
    return {"message": "Welcome to the Agentic AI Newsletter API"}
    # return RedirectResponse(url="/scrape")


@app.get("/scrape")
async def scrape_and_send(query: str = None, num_items: int = 20, top_n: int = 3):

    selected_topic = query or topic
    data = scraper.run(
        query=selected_topic, num_articles=num_items, num_papers=num_items
    )
    prioritized_data = prioritizer.run(data, top_n=top_n)
    summarized_text = summarizer.run(prioritized_data)

    # return {"summary": data}

    send_result = mailer.send_newsletter(subscribers, prioritized_data)
    logger.info({"summary": summarized_text, "email_send_result": send_result})

    return {"summary": summarized_text, "email_send_result": send_result}
