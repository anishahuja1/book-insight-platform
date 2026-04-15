import sys
from django.core.cache import cache

def get_cache(key):
    return cache.get(key)

def set_cache(key, value, timeout=86400):
    cache.set(key, value, timeout)
