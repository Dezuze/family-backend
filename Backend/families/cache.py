from __future__ import annotations

import logging

from django.conf import settings
from django.core.cache import cache

TREE_CACHE_VERSION_KEY = "families:tree:version"
TREE_CACHE_KEY_PREFIX = "families:tree:payload"
logger = logging.getLogger(__name__)


def get_tree_cache_version() -> int:
    try:
        version = cache.get(TREE_CACHE_VERSION_KEY)
    except Exception:
        logger.exception("Unable to read family tree cache version.")
        return 1
    if version is None:
        try:
            cache.set(TREE_CACHE_VERSION_KEY, 1, None)
        except Exception:
            logger.exception("Unable to initialize family tree cache version.")
        return 1
    try:
        return int(version)
    except (TypeError, ValueError):
        try:
            cache.set(TREE_CACHE_VERSION_KEY, 1, None)
        except Exception:
            logger.exception("Unable to reset family tree cache version.")
        return 1


def make_tree_cache_key(root_id: int | None) -> str:
    root_part = root_id if root_id else "anonymous"
    return f"{TREE_CACHE_KEY_PREFIX}:v{get_tree_cache_version()}:root:{root_part}"


def get_cached_tree_payload(root_id: int | None) -> dict | None:
    try:
        return cache.get(make_tree_cache_key(root_id))
    except Exception:
        logger.exception("Unable to read family tree payload cache.")
        return None


def set_cached_tree_payload(root_id: int | None, payload: dict) -> None:
    try:
        cache.set(
            make_tree_cache_key(root_id),
            payload,
            getattr(settings, "FAMILY_TREE_CACHE_TIMEOUT", 60 * 60 * 24 * 30),
        )
    except Exception:
        logger.exception("Unable to write family tree payload cache.")


def invalidate_family_tree_cache() -> None:
    try:
        cache.incr(TREE_CACHE_VERSION_KEY)
    except ValueError:
        try:
            cache.set(TREE_CACHE_VERSION_KEY, 2, None)
        except Exception:
            logger.exception("Unable to initialize family tree cache version during invalidation.")
    except Exception:
        logger.exception("Unable to invalidate family tree cache.")
