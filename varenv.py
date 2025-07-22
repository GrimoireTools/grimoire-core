"""This module provides functions to retrieve environment variables or local variables from a JSON file.

It checks the environment first, and if the variable is not found, it retrieves it from a local file named 'secrets.json'.
"""

import os
import json

from typing import Any


def get_from_local(varname: str) -> Any:
    """Retrieve a variable from a local JSON file named 'secrets.json'.

    The file should contain a dictionary with variable names as keys.
    """
    with open("secrets.json") as f:
        dic = json.load(f)
        return dic[varname]


def get_var(varname: str) -> Any:
    """Retrieve a variable from the environment or from a local JSON file."""
    if varname in os.environ:
        val = os.environ.get(varname)
        return val
    else:
        return get_from_local(varname)
