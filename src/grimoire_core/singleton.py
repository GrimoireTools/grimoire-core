"""Clase Singleton para crear instancias únicas de clases."""

from typing import Any, ClassVar, TypeVar

T = TypeVar("T")


class FetcherSingleton(type):
    """Metaclass for creating singleton classes."""

    _instances: ClassVar[dict[type[Any], Any]] = {}

    def __call__(cls, *args: Any, **kwargs: Any) -> Any:
        """Return the unique instance of the class, creating it if necessary."""
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)

        instance = cls._instances[cls]

        if hasattr(instance, "fetch_data"):
            instance.fetch_data()

        return instance


Singleton = FetcherSingleton
