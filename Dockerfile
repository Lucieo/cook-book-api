FROM python:3.7-alpine
MAINTAINER LucieO

#do not buffer the ouput print them directly
ENV PYTHONUNBUFFERED 1

#copy local file to docker image
COPY ./requirements.txt /requirements.txt

#install all requirements
RUN pip install -r /requirements.txt

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