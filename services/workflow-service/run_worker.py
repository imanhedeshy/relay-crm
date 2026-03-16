import os
import time

import django
import structlog

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "workflow_service.settings")
django.setup()

from workflows.consumer import poll_forever

logger = structlog.get_logger("workflow-worker")


if __name__ == "__main__":
    while True:
        try:
            poll_forever()
        except Exception as error:
            logger.error("worker_restart", error=str(error))
            time.sleep(2)
