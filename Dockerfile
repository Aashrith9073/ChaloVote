
# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /code

# Copy the requirements file and install dependencies
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Copy the rest of the application code into the container
COPY ./app /code/app

# Command to run the application using uvicorn
# Vercel will override this, but it's good practice for local Docker runs
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]