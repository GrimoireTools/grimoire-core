"""Clase Singleton para crear instancias únicas de clases."""

from typing import Any


from typing import ClassVar


class Singleton(type):
    """Metaclass para crear instancias únicas de clases."""

    _instances: ClassVar[dict] = {}

    def __call__(cls, *args: Any, **kwargs: Any) -> Any:
        """Return the singleton instance of the class."""
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        instance = cls._instances[cls]
        if hasattr(instance, "fetch_data"):
            instance.fetch_data()
        return instance
