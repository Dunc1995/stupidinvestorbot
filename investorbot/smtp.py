import smtplib
from email.mime.text import MIMEText

from investorbot.app import app
from flask import render_template

from investorbot.constants import RECIPIENT_EMAIL, SENDER_EMAIL, SENDER_PASSWORD


def send_test_email():
    body = "<html><body>An Error has Occurred.</body></html>"
    sender_email = SENDER_EMAIL
    sender_password = SENDER_PASSWORD
    recipient_email = RECIPIENT_EMAIL

    subject = "Stupid Investor Bot Test Email"

    with app.app_context():
        body = render_template("emails/example.html")

    html_message = MIMEText(body, "html")
    html_message["Subject"] = subject
    html_message["From"] = sender_email
    html_message["To"] = recipient_email

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipient_email, html_message.as_string())
