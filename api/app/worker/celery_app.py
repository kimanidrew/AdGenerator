import ssl
from urllib.parse import urlsplit

from celery import Celery

from app.config import settings


redis_scheme = urlsplit(settings.redis_url).scheme
redis_tls_options = (
    {"ssl_cert_reqs": ssl.CERT_REQUIRED}
    if redis_scheme == "rediss"
    else None
)

celery_app = Celery(
    "kenyaads",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["app.worker.tasks"],
)

celery_options = {
    "task_serializer": "json",
    "accept_content": ["json"],
    "result_serializer": "json",
    "timezone": "Africa/Nairobi",
    "enable_utc": True,
    "result_expires": 3600,
    "broker_connection_timeout": 10,
    "broker_transport_options": {
        "socket_connect_timeout": 10,
        "socket_timeout": 10,
        "retry_on_timeout": True,
    },
    "result_backend_transport_options": {
        "socket_connect_timeout": 10,
        "socket_timeout": 10,
        "retry_on_timeout": True,
    },
}

# Upstash requires TLS. Configure TLS for both the Celery broker and
# result backend when REDIS_URL uses the rediss:// scheme.
if redis_tls_options:
    celery_options["broker_use_ssl"] = redis_tls_options
    celery_options["redis_backend_use_ssl"] = redis_tls_options

celery_app.conf.update(**celery_options)
