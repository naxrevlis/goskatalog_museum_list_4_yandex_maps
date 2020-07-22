import requests
from modules.credentials import (
    API_SECRETS,
    GK_ALL_MUSEUM_LIST,
    GK_SINGLE_MUSEUM_URL,
    MONGO,
)

from requests.auth import HTTPBasicAuth
from modules.functions import get_credentials
from dictor import dictor
from pymongo import MongoClient
from datetime import datetime

YANDEX_RUBRIC_ID = "184105894"
COUNTRY = "Россия"
SINGLE_COLLECTION_MUSEUM_URL = "https://goskatalog.ru/portal/#/museums?id="


class Museum:
    def __init__(self, data):
        self.data = data
        self.gk_museum_id = dictor(data, "id")
        self.museum_inn = None
        self.gk_username, self.gk_password = get_credentials(
            API_SECRETS["webGoskatalog"]
        )
        self.single_museum_data = None
        self.cols_name = [
            "museum_gk_id",
            "inn",
            "company-id",
            "name",
            "country",
            "address",
            "phone",
            "email",
            "url",
            "booking-url",
            "workingTime",
            "rubric-id",
            "added_time" "update_time",
        ]

    def is_valid(self):
        _get_single_museum_data(self.gk_museum_id)
        if not self.single_museum_data:
            return False
        if not (
            dictor(self.single_museum_data, "regDate") is None
            or len(dictor(self.single_museum_data, "identifiers")) == 0
        ):
            for identifier in self.single_museum_data["identifiers"]:
                if identifier["type"] == "INN":
                    self.museum_inn = str(identifier["value"])
                    return True
        return False

    def _get_single_museum_data(self):
        try:
            self.single_museum_data = requests.get(
                GK_SINGLE_MUSEUM_URL + str(self.museum_gk_id),
                auth=HTTPBasicAuth(self.gk_username, self.gk_password),
            ).json()
            return True
        except Exception as err:
            print(err)
            return False

    def is_exist(self, conn):
        if self.gk_museum_id is None:
            return False
        if conn.find_one({"gk_museum_id": self.gk_museum_id}):
            return True
        return False

    def add(self, conn):
        try:
            data_to_append = [
                self.museum_gk_id,
                self.museum_inn,
                _get_museum_id(),
                _get_museum_name(),
                COUNTRY,
                _get_museum_address(),
                _get_museum_contacts(type="phone"),
                _get_museum_contacts(type="email"),
                _get_museum_contacts(type="url"),
                _get_museum_exhibits_url(),
                None,
                YANDEX_RUBRIC_ID,
                datetime.utcnow(),
                None,
            ]
            conn.insert_one(dict(zip(self.cols_name, data_to_append)))
            return True

        except Exception as err:
            print(err)
            return False

    def _get_museum_exhibits_url(self):
        return SINGLE_COLLECTION_MUSEUM_URL + _get_gk_museum_id()

    def _get_museum_contacts(self, type):
        """
            1:Phone
            2:Email
            3:WebSite
            4:Address
        Returns:
            str: Museum contact depending on type
        """

        item_type = {"phone": 1, "email": 2, "url": 3, "address": 4}
        value = None

        for item in dictor(self.data, "contacts"):
            if item["id"] == item_type[type]:
                value = item["contactValue"]
        return value

    def _get_museum_address(self):
        return dictor(self.data, "addressString")

    def _get_museum_name(self):
        return dictor(self.data, "name")

    def _get_museum_id(self):
        return dictor(self.data, "fullUin")

    def _get_data_from_gk(self):
        try:
            return [
                self.museum_gk_id,
                self.museum_inn,
                _get_museum_id(),
                _get_museum_name(),
                COUNTRY,
                _get_museum_address(),
                _get_museum_contacts(type="phone"),
                _get_museum_contacts(type="email"),
                _get_museum_contacts(type="url"),
                _get_museum_exhibits_url(),
                None,
                YANDEX_RUBRIC_ID,
                datetime.utcnow(),
                None,
            ]
        except Exception as err:
            print(err)
            return False

    def _get_data_from_db(self, conn):
        try:
            return conn.fing_one({self.cols_name[0]: self.gk_museum_id})
        except Exception as err:
            print(err)
            return False

    def update(self, conn):
        data_in_db = _get_data_from_db(conn)
        data_to_compare = _get_data_from_gk()
        if data_in_db or data_to_compare is False:
            return False
        if data_in_db[:-2] == data_to_compare[:-2]:
            return False
        if not data_in_db and not data_to_compare:
            # len -2 to not include added time and update time
            for i in range(len(data_to_compare) - 2):
                if data_in_db[i] is None and data_to_compare[i] is not None:
                    data_in_db[i] = data_to_compare[i]
            conn.update_one(
                {self.cols_name[0]: self.gk_museum_id},
                dict(zip(self.cols_name, data_in_db)),
            )
            return True
        return False


def update_museum_list_gk():
    """Updating museum list in database
    Returns:
        boolead: True if successfull
    """

    uri = "mongodb://{}:{}@{}:{}/{}".format(
        MONGO["username"], MONGO["password"], MONGO["host"], MONGO["port"], MONGO["db"]
    )
    client = MongoClient(uri)
    db = client[MONGO["db"]]
    mongo_conn = db["museumsList"]

    gk_data = get_data_from_gk()
    if gk_data is False:
        return False

    museums_updated = 0
    museums_added = 0
    museums_iterated = 0
    museums_total = len(gk_data)

    for item in gk_data:
        museums_iterated += 1
        museum = Museum(item)
        if not museum.is_valid():
            continue
        if museum.is_exist(mongo_conn):
            if museum.update(mongo_conn):
                museums_updated += 1
            continue
        if museum.add(mongo_conn):
            museums_added += 1

    print("Total museums is {}".format(museums_total))
    print(
        "Iterated {}. Updated {}. Added new {}.".format(
            museums_iterated, museums_updated, museums_added
        )
    )
    return True


def get_data_from_gk():
    username, password = get_credentials("webGoskatalog")

    print("Getting data from GK")
    try:
        goskatalogData = requests.get(
            GK_ALL_MUSEUM_LIST, auth=HTTPBasicAuth(username, password)
        ).json()["museums"]
        print("Received data from Goskatalog")
        return goskatalogData
    except Exception as err:
        print("There was an error. {}".format(err))
        return False


# TODO add function that check all the museums by last update date
def check_if_museum_alive():
    pass
