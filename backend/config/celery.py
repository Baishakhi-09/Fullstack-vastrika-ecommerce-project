from __future__ import annotations

import os

from celery import Celery
from kombu import Exchange
from kombu import Queue


os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "config.settings",
)

app = Celery( "config" )

app.config_from_object(
    "django.conf:settings",
    namespace="CELERY",
)

app.autodiscover_tasks()


# =========================================================
# CELERY CONFIGURATION
# =========================================================
app.conf.update(
    timezone="Asia/Kolkata",

    enable_utc=True,

    accept_content=[
        "json",
    ],

    task_serializer="json",

    result_serializer="json",

    task_track_started=True,

    task_ignore_result=False,

    result_expires=3600,

    task_time_limit=30 * 60,

    task_soft_time_limit=25 * 60,

    #  WORKER OPTIMIZATION
    worker_prefetch_multiplier=1,

    task_acks_late=True,

    worker_disable_rate_limits=False,

    # RETRY / CONNECTION
    broker_connection_retry_on_startup=True,

    broker_pool_limit=10,

    # TASK ROUTING
    task_default_queue="default",

    task_default_exchange="default",

    task_default_routing_key="default",

    # QUEUES
    task_queues=(

        Queue(
            "default",
            Exchange(
                "default"
            ),
            routing_key="default",
        ),

        Queue(
            "emails",
            Exchange(
                "emails"
            ),
            routing_key="emails",
        ),

        Queue(
            "notifications",
            Exchange(
                "notifications"
            ),
            routing_key="notifications",
        ),

        Queue(
            "reports",
            Exchange(
                "reports"
            ),
            routing_key="reports",
        ),

        Queue(
            "media",
            Exchange(
                "media"
            ),
            routing_key="media",
        ),
    ),

    # TASK ROUTES
    task_routes={

        # EMAIL TASKS
        (
            "apps.notifications.tasks.*"
        ): {
            "queue": "notifications",
        },

        # REPORT TASKS
        (
            "apps.reports.tasks.*"
        ): {
            "queue": "reports",
        },

        # MEDIA TASKS
        (
            "apps.social_images.tasks.*"
        ): {
            "queue": "media",
        },
    },

    # BEAT SCHEDULER
    beat_scheduler=(
        "django_celery_beat.schedulers:"
        "DatabaseScheduler"
    ),
)


# =========================================================
# DEBUG TASK
# =========================================================
@app.task(
    bind=True,
)
def debug_task(
    self,
) -> None:
    """
    Debug Celery task.
    """

    print(
        (
            "Celery Request: "
            f"{self.request!r}"
        )
    )