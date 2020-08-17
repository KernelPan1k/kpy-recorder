FROM python:3.7-buster

WORKDIR /usr/src/app

COPY entrypoint-linux.sh entrypoint.sh
COPY ./project.spec .
COPY ./requirements.txt .
COPY ./src src/
RUN chmod +x entrypoint.sh && mkdir dist/
RUN apt-get update \
    && apt-get install -y --no-install-recommends upx \
    && pip install --no-cache-dir pyinstaller

VOLUME /usr/src/app/dist

ENTRYPOINT ["./entrypoint.sh"]
