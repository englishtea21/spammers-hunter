FROM python:3.11
WORKDIR /app
COPY requirements.txt requirements.txt
# Install Python's venv module and create a virtual environment
RUN python -m venv venv
# Activate the virtual environment and install dependencies
# Combining into one RUN command to ensure venv is activated
RUN /bin/bash -c "source venv/bin/activate && pip install --no-cache-dir --upgrade setuptools && pip install --no-cache-dir -r requirements.txt"
RUN chmod 755 .
COPY . .
