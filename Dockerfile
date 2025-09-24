# pull official base image
# FROM python:3.8.1-slim-buster
# Won't build
# FROM python:3.9-slim-bullseye

# Add these lines to point to the archive
RUN sed -i \
    -e 's/deb.debian.org/archive.debian.org/g' \
    -e 's|security.debian.org|archive.debian.org|g' \
    -e '/buster-updates/d' \
    /etc/apt/sources.list


# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# STEP 1: Explicitly install the latest keyrings to fix GPG signature issues.
# This ensures the build environment trusts the Debian repositories.
RUN apt-get update && apt-get install -y --no-install-recommends \
    debian-keyring \
    debian-archive-keyring \
&& rm -rf /var/lib/apt/lists/*


# install system dependencies
# RUN apt-get update && apt-get install -y netcat
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc python3-dev

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt /usr/src/app/requirements.txt
RUN pip install -r requirements.txt

# copy project
COPY . /usr/src/app/

# run entrypoint.sh
# ENTRYPOINT ["/usr/src/app/entrypoint.sh"]