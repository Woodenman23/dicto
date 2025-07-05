FROM python:3.12-slim

# Install Poetry and ffmpeg
RUN apt-get update && apt-get install -y ffmpeg && apt-get clean && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir poetry

# Set working directory
WORKDIR /app

# Copy only what Poetry needs first (for caching)
COPY pyproject.toml poetry.lock* /app/

# Install dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --no-dev --no-root

# Copy the rest of the app
COPY . /app/

EXPOSE 8080
# Set BASE_PATH for subdirectory deployment
ENV BASE_PATH=/dicto

CMD ["gunicorn", "-b", "0.0.0.0:8080", "app:app"]