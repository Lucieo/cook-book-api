FROM python:3.7-alpine
MAINTAINER LucieO

#do not buffer the ouput print them directly
ENV PYTHONUNBUFFERED 1

#copy local file to docker image
COPY ./requirements.txt /requirements.txt

#install postegresql client apk(package manager of alpine) add(add a new package) --update(update registry before we add it) --no-cache (don't store registry index on our dockerfile = minimise docker container footprint)
RUN apk add --update --no-cache postgresql-client
#temporary requirements
RUN apk add --update --no-cache --virtual .tmp-build-deps \
    gcc libc-dev linux-headers postgresql-dev

#install all requirements
RUN pip install -r /requirements.txt
#delete temporary requirements
RUN apk del .tmp-build-deps

#creates app empty folder on docker image
RUN mkdir /app
#switches to it as default directory
WORKDIR /app
#copy app from local machine to app folder on image
COPY ./app /app

#create user that will run our app using docker (-D means for running applications only) = avoid image running using root account - limits scope that attacker could have on our docker container
RUN adduser -D user
#switch to that user
USER user