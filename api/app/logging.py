"""Small structured logger with credential-safe fields."""

import json
import logging
import re
from typing import Any


SECRET_KEY = re.compile(r"(?i)(password|secret|token|api[_-]?key|database[_-]?url|service[_-]?role)")


def safe_fields(fields: dict[str, Any]) -> dict[str, Any]:
    return {key: "[REDACTED]" if SECRET_KEY.search(key) else value for key, value in fields.items()}


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if isinstance(record.args, dict):
            payload.update(safe_fields(record.args))
        return json.dumps(payload, ensure_ascii=False)


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(JsonFormatter())
        logger.addHandler(handler)
        logger.propagate = False
    return logger

