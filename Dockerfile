FROM python:3.6-alpine3.8

RUN apk --update add \
        gcc \
        zlib-dev \
        git \
        linux-headers \
        build-base \
        musl \
        musl-dev

COPY /. /var/app

WORKDIR /var/app

RUN pip install --no-cache-dir -r requirements.txt

ENTRYPOINT ["uwsgi"]

CMD ["--http", ":5000", "--wsgi-file" , "app.py", "--callable", "app"]
