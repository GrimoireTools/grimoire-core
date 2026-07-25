import os

from dotenv import load_dotenv

load_dotenv(dotenv_path=".env", encoding="utf-8-sig")


def get_env(varname: str) -> str:
    value = os.getenv(varname)
    if value is None:
        raise KeyError(f"Environment variable '{varname}' not found in .env")
    return value
