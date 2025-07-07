import logging
import logging.config
import os
import uuid
from pathlib import Path

import psycopg
import redis
import yaml
from flask import Flask, Response, request

# Load the logging configuration
LOGGING_CONFIG = {}
with open(Path(__file__).parent / "logger_config.yaml", "r") as f:
    LOGGING_CONFIG = yaml.safe_load(f)
    logging.config.dictConfig(LOGGING_CONFIG)


app = Flask(__name__)


@app.route("/")
def index():
    return "running"


@app.route("/check")
def check():
    source = request.args.get("source")
    return Response(infra_check(source), content_type="text/event-stream")


def ping_redis(host, port=6379):
    message = f"pinding redis at {host}:{port}\n"
    try:
        r = redis.Redis(host=host, port=port, decode_responses=True)
        message += "connected\n"

        random_key = str(uuid.uuid4())
        test_value = f"test_{random_key}"
        r.set(random_key, test_value)
        message += f"set key {test_value}\n"

        retrieved_value = r.get(random_key)
        if retrieved_value == test_value:
            message += f"retrieved key {test_value} looks equal\n"
            r.delete(random_key)

    except Exception as e:
        message += f"error: {e}\n"

    return message + "\n"


def ping_postgres(database_url):
    message = f"pinding postgres at {database_url}\n"
    try:
        with psycopg.connect(database_url) as conn:
            message += "connected\n"
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT COUNT(*)
                    FROM information_schema.tables
                    WHERE table_schema = 'public'
                """)
                count = cur.fetchone()[0]  # pyright: ignore
                message += f"found {count} tables in public schema\n"

    except Exception as e:
        message += f"error: {e}\n"

    return message + "\n"


def infra_check(source):
    if not source:
        source = "all"

    if source in ["db", "all"]:
        db_url = os.environ.get("DATABASE_URL", "postgresql://@/edgar3")
        yield ping_postgres(db_url)

    if source in ["redis", "all"]:
        redis_svc = os.environ.get("REDIS_SVC", "localhost")
        yield ping_redis(redis_svc)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
