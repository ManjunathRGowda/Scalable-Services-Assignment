# Scalable-Services-Assignment
BITS-WILP Assignment: Microservices Development and Deployment.

# prog-webserv
The stateless web service is built in Python using FASTAPI Framework.

# Browser Support
Google Chrome

Mozilla Firefox

# OS Support
MacOS

Linux Distribution - Ubuntu, Centos, Debian, RHEL

Windows 10

# MacOS Prerequisites
Python >=3.8

# Windows Prerequisites
Python >=3.8

Ensure the python path is set as PATH variable.

# Linux Prerequisites
Python >=3.8

A package called "chrome-session-dump" needs to be installed.

To install chrome-session-dump package, Run the below command - 

`sudo curl -o /usr/bin/chrome-session-dump -L 'https://github.com/lemnos/chrome-session-dump/releases/download/v0.0.2/chrome-session-dump-linux' && sudo chmod 755 /usr/bin/chrome-session-dump`

# Installation Instructions
Pull the source code from GitHub repository.

`pip3 install --upgrade -r requirements.txt`

`uvicorn main:app --port=8000`

Port can be changed as per the user requirement.

The API docs will be accessible at - [http://localhost:8000/docs]()


# GET /start
Opens up a new web browser session. If the browser session already exists, it will add a new tab.

# GET /stop
Stops a web browser session.

# GET /cleanup
Clears the web browser cache, history, cookies, downloads etc. It will work only when the browser is closed.

# GET /geturl
Fetches the URL present in the active tab of the web browser. 

# Note
No WebDriver / Selenium components are used. The code relies on generic python libraries for the implementation.




