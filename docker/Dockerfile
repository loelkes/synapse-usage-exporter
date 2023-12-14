FROM python:3.9

ARG APP_VERSION=latest
ENV APP_VERSION=${APP_VERSION}

ARG BUILD_ID
ENV BUILD_ID=${BUILD_ID}

WORKDIR /usr/src

COPY requirements.txt .
COPY docker/requirements.txt docker.requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -r docker.requirements.txt

COPY app app
COPY docker/entrypoint.sh .
COPY docker/wsgi.py .
COPY docker/uwsgi.ini .

EXPOSE 5000
ENTRYPOINT [ "/bin/sh", "entrypoint.sh" ]
