FROM python:3-alpine

# Arguments passed during the build
ARG SECRET_KEY

WORKDIR /app/polls

# Environment variables
ENV SECRET_KEY=${SECRET_KEY}
ENV DEBUG=True
ENV TIMEZONE=UTC

# Test for secret key during build
RUN if [ -z "$SECRET_KEY" ]; then echo "No secret key specified in build-arg"; exit 1; fi

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN chmod +x ./entrypoint.sh

EXPOSE 8000
CMD ["./entrypoint.sh"]
