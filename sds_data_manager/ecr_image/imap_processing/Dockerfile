FROM python:3.11-slim

RUN apt-get update && \
    apt-get install -y git

RUN python -m pip install --upgrade pip

WORKDIR /imap_processing/

# Install imap-processing using below command
RUN pip install git+https://github.com/IMAP-Science-Operations-Center/imap_processing.git@dev

COPY script.py ./script.py

ENTRYPOINT [ "/usr/local/bin/python", "script.py" ]
