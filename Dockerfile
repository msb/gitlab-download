FROM python:3.8-alpine

WORKDIR /app

ADD ./ ./

RUN apk --no-cache add git && \
    pip install --upgrade pip && \
    pip install -r requirements.txt && \
    git clone https://github.com/msb/fs.googledrivefs.git --branch support_for_service_accounts /tmp/fs.googledrivefs && \
    pip install /tmp/fs.googledrivefs/

VOLUME /app
VOLUME /data

ENTRYPOINT ["python3", "gitlabdownload.py"]