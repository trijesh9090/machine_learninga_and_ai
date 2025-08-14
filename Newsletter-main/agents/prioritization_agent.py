import os
import re
import json
from datetime import datetime, timezone, timedelta
from typing import List

from models.newsletter import Newsletter
from agents.base import Agent
from langchain_groq import ChatGroq
from langchain.schema import HumanMessage
from dotenv import load_dotenv

load_dotenv()


class PrioritizationAgent(Agent):
    def __init__(self):
        self.llm = ChatGroq(
            model="deepseek-r1-distill-llama-70b",
            api_key=os.getenv("GROQ_API_KEY"),
        )
        self.state: List[Newsletter] = []

    def prioritize(self, items: List[Newsletter], top_n: int = 5) -> List[Newsletter]:
        self.state.clear()
        now = datetime.now(timezone.utc)
        last_week = now - timedelta(days=7)

        recent_items = [
            item
            for item in items
            if item.published_at and item.published_at >= last_week
        ]

        if not recent_items:
            print("[INFO] No recent items to prioritize.")
            return items

        entries = []
        for i, item in enumerate(recent_items, start=1):
            entry = f"""{i}. ID: {item.id}
                        Title: {item.title}
                        Description: {item.description or 'N/A'}"""
            entries.append(entry)

        prompt = f"""
            You are helping curate a weekly newsletter on Agentic AI.

            Here are {len(recent_items)} items published in the past 7 days. Select the top {top_n} that are most important or relevant to Agentic AI. Make sure to prioritize only Agentic AI related content.

            Respond ONLY with a valid JSON list. Do NOT include any explanation or extra text. The format should be:

            [
            {{
                "id": "UUID1",
                "reason": "Why it's important"
            }},
            ...
            ]

            Here are the entries:
            {chr(10).join(entries)}
            """

        response = self.llm.invoke([HumanMessage(content=prompt)])
        raw_output = response.content.strip()

        match = re.search(r"\[\s*{.*?}\s*\]", raw_output, re.DOTALL)
        json_text = match.group(0) if match else raw_output

        try:
            prioritized = json.loads(json_text)
        except json.JSONDecodeError:
            print("[LLM ERROR] Could not parse JSON:\n", raw_output)
            return items

        prioritized_ids = {
            entry["id"]: entry.get("reason", "Prioritized by LLM")
            for entry in prioritized
        }

        for item in items:
            if item.id in prioritized_ids:
                item.is_prioritized = True
                item.priority_reason = prioritized_ids[item.id]
            else:
                item.is_prioritized = False

        self.state = items
        return self.state

    def run(self, items: List[Newsletter], *args, **kwargs) -> List[Newsletter]:
        top_n = kwargs.get("top_n", 5)
        return self.prioritize(items, top_n=top_n)
