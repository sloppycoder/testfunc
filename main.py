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
    source = request.args.get("source")  # 'redis' if ?source=redis
    print("source =", source)
    # Use `source` to select the event stream source
    return Response(infra_check(source), content_type="text/event-stream")


def infra_check(source):
    for i in range(3):
        time.sleep(0.5)
        yield f"checking: {i}..\n\n"


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
