FROM python:3.9-slim

WORKDIR /api

# Copy the requirements file
COPY ./requirements.txt /api/requirements.txt

# Update pip and install dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir --upgrade -r /api/requirements.txt

# Copy the application code
COPY . /api

# Set environment variables for Flask
ENV FLASK_APP=app
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=5000

# Set PYTHONPATH to include the root directory
ENV PYTHONPATH=/api

# Command to run the Flask application
CMD ["flask", "run", "--debug"]