FROM python:3.11
WORKDIR /app
COPY requirements.txt requirements.txt
# for building some libs
RUN pip3 install --upgrade setuptools
# install project dependencies
RUN pip3 install -r requirements.txt
RUN chmod 755 .
COPY . .
