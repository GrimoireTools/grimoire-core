"""Clase Singleton para crear instancias únicas de clases."""

from typing import ClassVar, TypeVar, Any


T = TypeVar("T")


class Singleton(type):
    """Metaclass para crear instancias únicas de clases."""

    _instances: ClassVar[dict[type, object]] = {}

    def __call__(cls: type[T], *args: Any, **kwargs: Any) -> T:
        """Return the singleton instance of the class."""
        if cls not in Singleton._instances:
            Singleton._instances[cls] = super().__call__(*args, **kwargs)
        instance = Singleton._instances[cls]
        fetch_data = getattr(instance, "fetch_data", None)
        if callable(fetch_data):
            fetch_data()
        return instance  # type: ignore
