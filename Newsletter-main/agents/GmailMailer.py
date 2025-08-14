import os
import smtplib
from typing import List
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class GmailMailer:
    def __init__(self):
        self.from_email = os.getenv("GMAIL_FROM_EMAIL")
        self.app_password = os.getenv("GMAIL_APP_PASSWORD")

        if not self.from_email or not self.app_password:
            raise ValueError(
                "GMAIL_FROM_EMAIL or GMAIL_APP_PASSWORD not set in environment variables"
            )

    def _build_html_content(self, newsletters) -> str:
        html_content = "<h1>Agentic AI Weekly Newsletter</h1>"
        html_content += "<p>Here are the top prioritized items for this week:</p><ul>"

        for item in newsletters:
            html_content += "<li>"
            html_content += f"<h2>{item.title}</h2>"
            if item.summary:
                html_content += f"<p>{item.summary}</p>"
            if item.url:
                html_content += f'<p><a href="{item.url}">Read more</a></p>'
            html_content += "</li>"

        html_content += "</ul>"
        html_content += "<p>Thank you for subscribing!</p>"
        return html_content

    def send_newsletter(self, to_emails: List[str], newsletters) -> dict:
        subject = "Your Agentic AI Weekly Newsletter"
        newsletters = [n for n in newsletters if n.is_prioritized]
        html_body = self._build_html_content(newsletters)

        message = MIMEMultipart()
        message["From"] = self.from_email
        message["To"] = ", ".join(to_emails)
        message["Subject"] = subject
        message.attach(MIMEText(html_body, "html"))

        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(self.from_email, self.app_password)
                server.sendmail(self.from_email, to_emails, message.as_string())
            return {"status": "sent", "recipients": to_emails}
        except Exception as e:
            return {"error": str(e)}
