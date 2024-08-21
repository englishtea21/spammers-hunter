FROM python:3.11
WORKDIR /app
COPY requirements.txt requirements.txt
# Install Python's venv module and create a virtual environment
RUN python -m venv venv
# Activate the virtual environment and install dependencies
RUN /bin/bash -c "source venv/bin/activate"
# for building some libs
RUN pip3 install --no-cache-dir --upgrade setuptools
# install project dependencies
RUN pip3 install --no-cache-dir -r requirements.txt
RUN chmod 755 .
COPY . .
