FROM python:3.7-alpine

LABEL "com.github.actions.name"="Wait for Appveyor"
LABEL "com.github.actions.description"="Wait for Appveyor to return a status"
LABEL "com.github.actions.icon"="clock"
LABEL "com.github.actions.color"="yellow"

LABEL "repository"="http://github.com/prayasJ/appveyor-wait"
LABEL "homepage"="http://github.com/actions"
LABEL "maintainer"="http://github.com/prayasJ"

RUN apk --no-cache add git && \
    pip3 install requests
ADD wait_for_Appveyor.py /wait_for_Appveyor.py
CMD ["/wait_for_Appveyor.py"]
