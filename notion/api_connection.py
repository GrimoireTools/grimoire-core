"""Helper functions for connecting to the Notion API."""

from typing import Any
from notion_client import Client
from controllers.lib.varenv import get_var

API_KEY = get_var("NOTION_API_KEY")
PJS_DB = "c74240fe08964455920860cbbc2caa98"
MISSIONS_DB = "c73bb2e886bd4aed9e9224934fdef6ce"

client = Client(auth=API_KEY)


def get_missions_db() -> Any:
    """Retrieve the Missions database."""
    return client.databases.retrieve(database_id=MISSIONS_DB)
