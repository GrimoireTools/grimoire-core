"""This module provides a function to retrieve environment variables from a .env file."""

import os

from dotenv import load_dotenv

load_dotenv(dotenv_path=".env", encoding="utf-8-sig")


def get_env(varname: str) -> str:
    """Get the value of an environment variable from the .env file."""
    value = os.getenv(varname)
    if value is None:
        raise KeyError(f"Environment variable '{varname}' not found in .env")
    return value
