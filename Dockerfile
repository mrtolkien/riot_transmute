# Dev environment image
FROM python:latest

# Package dependencies
RUN pip install riotwatcher
RUN pip install lol-dto
RUN pip install lol-id-tools

# Dev dependencies
RUN pip install pytest
RUN pip install roleml
