import requests as req
import smtplib as smt
from email.mime.text import MIMEText
import markdown
import re
import time


#note, in the url you must add "api." before "github", and "/repos/" before the username
repoLink = "https://api.github.com/repos/cvenclauskas/GH-Release-Bot"
fromAddress = "fromemail@gmail.com"
toAddress = "toemail@gmail.com"
password = ""
#THIS IS AN APP PASSWORD, NOT YOUR EMAIL PASSWORD

def createEmail(repoData, releaseData):
    
    #server stuff
    server = smt.SMTP("smtp.gmail.com", 587)
    server.starttls()

    server.login(fromAddress, password)

    body = releaseData["body"]

    #removes some weird whitespace
    body = re.sub(r'(?m)^  ', '', body)

    #prevents issue numbers from being displayed as urls
    body = re.sub(
        r'https://github\.com/[^/]+/[^/]+/(?:issues|pull)/(\d+)',
        r'[#\1](https://github.com/fmtlib/fmt/issues/\1)',
        body
    )

    changelog = markdown.markdown(body, extensions=["tables", "fenced_code"])

    #html stuff for email
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

    <a href="{releaseData["html_url"]}">
    Check it out here
    </a>

    </body>
    </html>
    """, "html", "utf-8")

    message["Subject"] = f"New GitHub Release - {repoData['name']}"
    message["From"] = fromAddress
    message["To"] = toAddress

    #sends email
    server.sendmail(fromAddress, toAddress, message.as_string())
    server.quit()
    print("email sent to", toAddress)


#once per minute check whether the latest release 
#id matches the previous checks latest release id
#if not then send an email
def main():

    interval = 30
    
    previousRelease = None
    
    while True:


        repoResponse = req.get(repoLink)
        releaseResponse = req.get(repoLink + "/releases")

        #if error, sleep and try again in interval seconds
        if releaseResponse.status_code == 404:
            time.sleep(interval)
            continue

        releaseData = releaseResponse.json()

        if not releaseData or not isinstance(releaseData, list):
            print("No releases or response isn't a list")
            time.sleep(interval))
            continue

        repoData = repoResponse.json()

        latestRelease = releaseData[0]
        latestReleaseId = latestRelease["id"]
        
        #if we are checking for the first time, assign latest release
        if previousRelease is None:
            previousRelease = latestReleaseId
            print("NEW RELEASE DETECTED:", latestRelease["name"])
            createEmail(repoData, latestRelease)
        #if new id, send email
        elif latestReleaseId != previousRelease:
            print("NEW RELEASE DETECTED:", latestRelease["name"])
            createEmail(repoData, latestRelease)
            previousRelease = latestReleaseId
        
        #sleeeeeeeeeeeeep
        time.sleep(interval)

if __name__ == "__main__":
    main()