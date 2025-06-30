# Build stage
FROM python:3.12-slim AS builder
WORKDIR /app
COPY requirements.txt ./
# Install dependencies using pip
RUN pip install --no-cache-dir --user -r requirements.txt

# Runtime stage  
FROM python:3.12-slim
WORKDIR /app
# Copy Python packages from builder
COPY --from=builder /root/.local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /root/.local/bin /usr/local/bin
# Copy app files
COPY . .
EXPOSE 8080
# Set BASE_PATH for subdirectory deployment
ENV BASE_PATH=/dicto
CMD ["gunicorn", "-b", "0.0.0.0:8080", "app:app"]