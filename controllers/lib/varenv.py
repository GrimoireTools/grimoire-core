"""Helper function to acces .env values or local secrets."""

import os
import json

from typing import Any


def get_from_local(varname: str) -> Any:
    """Get a variable from the local secrets.json file."""
    with open("secrets.json") as f:
        dic = json.load(f)
        return dic[varname]


def get_var(varname: str) -> Any:
    """Get a variable from the environment or local secrets.json file."""
    if varname in os.environ:
        val = os.environ.get(varname)
        return val
    else:
        return get_from_local(varname)
