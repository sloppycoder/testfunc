import logging
import logging.config
import os
import time
from pathlib import Path

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


def infra_check(source):
    if not source:
        source = "all"

    if source in ["db", "all"]:
        db_url = os.environ.get("DATABASE_URL", "")
        yield f"DATABASE_URL={db_url}\n\n"
        time.sleep(0.5)

    if source in ["redis", "all"]:
        redis_svc = os.environ.get("REDIS_SVC", "redis-standalone")
        yield f"REDIS_SVC={redis_svc}\n\n"
        time.sleep(0.5)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
