# Dockerfile that installs imap-data-access and its dependencies
FROM public.ecr.aws/docker/library/python:3.10-slim
USER root

# Upgrade pip to the latest version
RUN pip install --upgrade pip

RUN pip install requests

# TODO: delete this section once imap-data-access is released
ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y git
RUN pip install git+https://github.com/IMAP-Science-Operations-Center/imap-data-access.git

# Create the /mnt/spice directory
WORKDIR /data
RUN mkdir /app/
COPY imap_api.py /app/

ENTRYPOINT ["python", "/app/imap_api.py"]
