import requests as req
import smtplib as smt
from email.mime.text import MIMEText
import markdown
import re
import time


repoLink = ""
fromAddress = ""
toAddress = ""
password = ""

server = smt.SMTP("smtp.gmail.com", 587)
server.starttls()

server.login(fromAddress, password)


def createEmail(repoData, releaseData):
    
    body = releaseData["body"]

    body = re.sub(r'(?m)^  ', '', body)

    body = re.sub(
        r'https://github\.com/[^/]+/[^/]+/(?:issues|pull)/(\d+)',
        r'[#\1](https://github.com/fmtlib/fmt/issues/\1)',
        body
    )

    changelog = markdown.markdown(body, extensions=["tables", "fenced_code"])

    message = MIMEText(f"""
    <html>
    <head>
    <style>
        pre {{
            background-color: #f6f8fa;
            padding: 12px;
            border-radius: 6px;
            overflow-x: auto;
            font-family: monospace;
            border: 1px solid #d0d7de;
            margin-left: 55px;
        }}

        pre code {{
            background: none;
            padding: 0;
            border: none;
        }}

        table {{
            border-collapse: collapse;
            margin-left: 55px;
        }}

        th, td {{
            border: 1px solid #d0d7de;
            padding: 6px 10px;
        }}
                   
        h3 {{
            font-size: 20px;
        }}
    </style>
    </head>

    <body>

    <h2>A new Github release was detected for {repoData["name"]}</h2>

    <h3>Version: {releaseData["name"]}</h3>

    <p>
    <b>CHANGELOG:</b>
    </p>

    {changelog}

    <br>

    <a href="{releaseData["html_url"]}">
    Check it out here
    </a>

    </body>
    </html>
    """, "html", "utf-8")

    message["Subject"] = f"New GitHub Release - {repoData['name']}"
    message["From"] = fromAddress
    message["To"] = toAddress

    server.sendmail(fromAddress, toAddress, message.as_string())
    server.quit()



def main():
    previousRelease = None

    while True:
        repoResponse = req.get(repoLink)
        releaseResponse = req.get(repoLink + "/releases/latest")
        repoData = repoResponse.json()
        releaseData = releaseResponse.json()

        latestRelease = releaseData["id"]
        if previousRelease is None:
            previousRelease = latestRelease
        elif latestRelease != previousRelease:
            createEmail(repoData, releaseData)
            previousRelease = latestRelease

        time.sleep(60)


main()