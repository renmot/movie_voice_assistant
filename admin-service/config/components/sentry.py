import os

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

sentry_dsn = os.getenv("SENTRY_DSN")

if sentry_dsn:
    sentry_sdk.init(
        dsn=sentry_dsn, integrations=[DjangoIntegration()], traces_sample_rate=1.0
    )
