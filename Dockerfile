# stage 1: build
FROM python:3.12-bookworm AS builder
LABEL org.opencontainers.image.source=https://github.com/sloppycoder/testfunc
LABEL org.opencontainers.image.description="Test Function for Knative"

# install packages needed by python packages
RUN apt-get update \
    && apt-get install --yes --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

# create virtualenv and install dependencies
RUN python -m venv /app/venv
ENV PATH="/app/venv/bin:$PATH"
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# stage 2: runtime
FROM python:3.12-slim-bookworm

# create user
RUN addgroup --system app && adduser --system --group app
USER app
WORKDIR /app

# copy virtualenv from builder
COPY --chown=app:app --from=builder /app/venv /app/venv
# copy application code. update .dockerignore to files that shouldn't be copied
COPY --chown=app:app . .

EXPOSE 8080

ENV PATH="/app/venv/bin:$PATH"
CMD  ["/bin/sh", "/app/entrypoint.sh"]
