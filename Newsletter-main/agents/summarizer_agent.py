import os
import re
from typing import List
from agents.base import Agent
from langchain_groq import ChatGroq
from models.newsletter import Newsletter
from langchain.schema import HumanMessage

from dotenv import load_dotenv

load_dotenv()


class SummarizationAgent(Agent):
    def __init__(self):
        self.llm = ChatGroq(
            model="deepseek-r1-distill-llama-70b",
            api_key=os.getenv("GROQ_API_KEY"),
            temperature=0.4,
        )

    def summarize_single(self, item: Newsletter) -> str:
        prompt = f"""
        You are an expert newsletter editor for Agentic AI.

        Summarize this article clearly and concisely as a paragraph, highlighting why it matters.

        Title: {item.title}
        Description: {item.description or 'N/A'}
        Content: {item.content or 'N/A'}

        Return only the summary text, no extra explanation.
        """
        response = self.llm.invoke([HumanMessage(content=prompt)])
        raw_summary = response.content.strip()

        # Remove <think> blocks
        cleaned_summary = re.sub(
            r"<think>.*?</think>", "", raw_summary, flags=re.DOTALL
        ).strip()

        cleaned_summary = cleaned_summary.strip(" \"'\n")

        return cleaned_summary

    def run(self, items: List[Newsletter], *args, **kwargs) -> List[Newsletter]:
        # Summarize only prioritized items
        for item in items:
            if item.is_prioritized:
                item.summary = self.summarize_single(item)
            else:
                item.summary = None

        return items
