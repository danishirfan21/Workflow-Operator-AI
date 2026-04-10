from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import os


def send_email(to_email: str, subject: str, content: str):
    try:
        sg = SendGridAPIClient(os.getenv("SENDGRID_API_KEY"))

        message = Mail(
            from_email=os.getenv("FROM_EMAIL"),
            to_emails=to_email,
            subject=subject,
            html_content=content,
        )

        response = sg.send(message)

        print("SendGrid STATUS:", response.status_code)
        print("HEADERS:", response.headers)

        return {
            "success": True,
            "status_code": response.status_code
        }

    except Exception as e:
        print("SENDGRID ERROR:", str(e))

        return {
            "success": False,
            "error": str(e)
        }