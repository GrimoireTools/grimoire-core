"""Clase Singleton para crear instancias únicas de clases."""

from typing import TypeVar

T = TypeVar("T")


class Singleton(type):
    """Metaclass para crear instancias únicas de clases."""

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        instance = cls._instances[cls]
        if hasattr(instance, "fetch_data"):
            instance.fetch_data()
        return instance
