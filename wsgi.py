from flask_app import app
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk import capture_message

import logging.config
import logging
from os import path

log_file_path = path.join(path.dirname(path.abspath(__file__)), "logging.conf")

logging.config.fileConfig(log_file_path, disable_existing_loggers=False)

sentry_sdk.init(
    dsn="https://51db7ee73f9d431dba99fe94a659e5c0@o611000.ingest.sentry.io/5748041",
    integrations=[FlaskIntegration()],
    # Set traces_sample_rate to 1.0 to capture 100% of transactions
    traces_sample_rate=1.0,
)
sentry_logging = LoggingIntegration(
    level=logging.INFO,  # Capture info and above as breadcrumbs
    event_level=logging.INFO,  # Send Info as events
)


capture_message("Starting the flask app")
app.run(debug=False)
