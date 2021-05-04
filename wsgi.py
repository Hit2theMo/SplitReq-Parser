from flask_app import app
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
import logging.config, logging

logging.config.fileConfig("logging.conf", disable_existing_loggers=False)

sentry_sdk.init(
    dsn="https://51db7ee73f9d431dba99fe94a659e5c0@o611000.ingest.sentry.io/5748041",
    integrations=[FlaskIntegration()],
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    # We recommend adjusting this value in production.
    traces_sample_rate=1.0,
)

app.run(debug=False)
