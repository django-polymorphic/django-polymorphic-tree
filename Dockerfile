FROM python:3

RUN pip3 install --upgrade pip

RUN apt-get -y update
RUN apt-get -y upgrade 
RUN apt-get -y install gettext

# Initialize
WORKDIR /data/app
# Prepare
COPY . /data/app/

RUN pip install -e .

RUN pip install tox django

RUN tox
