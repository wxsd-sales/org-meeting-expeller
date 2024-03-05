############################################################
# Dockerfile to build Org Meeting Expeller App
############################################################
#docker build -t org-meeting-expeller .
#docker run -i -p 10031:10031 -t org-meeting-expeller
#docker run -i --restart always -p 10031:10031 -v /Users/taylorhanson/Documents/GitHub/in-meeting-demos/.devcontainer/server/nodePuppeteer/media:/opt/server/nodePuppeteer/media -t org-meeting-expeller
###########################################################################

FROM python:3.8.3

# File Author / Maintainer
MAINTAINER "Taylor Hanson <tahanson@cisco.com>"

# Copy the application folder inside the container
ADD . .

# Set the default directory where CMD will execute
WORKDIR /

#Copy environment variables file. Overwrite it with prod.env if prod.env exists.
COPY server/.env server/prod.env* server/.env
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

#Run
WORKDIR /server
CMD ["python","server.py"]