import os
from dotenv import load_dotenv

if os.path.isfile(".env"):
    load_dotenv()

MONGO = {
    "host": os.environ.get("ENV_MONGO_HOST"),
    "port": os.environ.get("ENV_MONGO_PORT"),
    "db": os.environ.get("ENV_MONGO_DB"),
    "username": os.environ.get("ENV_MONGO_USERNAME"),
    "password": os.environ.get("ENV_MONGO_PW"),
}

API_SECRETS = {
    "webGoskatalog": {
        "username": os.environ.get("ENV_GK_USERNAME"),
        "password": os.environ.get("ENV_GK_PASSWORD"),
        },
    "esb": {
            "username": os.environ.get("ENV_ESB_USERNAME"),
            "password": os.environ.get("ENV_ESB_PASSWORD"),
        }
    }

ESB_URL = os.environ.get("ENV_ESB_URL")
GK_ALL_MUSEUM_URL = os.environ.get("ENV_GK_ALL_MUSEUM_URL")
GK_SINGLE_MUSEUM_URL = os.environ.get("ENV_GK_SINGLE_MUSEUM_URL")