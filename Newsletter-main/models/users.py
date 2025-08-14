from typing import Optional


class User:
    def __init__(self, email: str, preferred_topic: str):
        self.email = email
        self.preferred_topic = preferred_topic


# Hardcoded test users
USER_DATABASE = {
    "trijesh.chodvadiya90@gmail.com": User(
        email="trijesh.chodvadiya90@gmail.com", preferred_topic="Agentic AI"
    ),
}


def get_user_by_email(email: str) -> Optional[User]:
    return USER_DATABASE.get(email)
