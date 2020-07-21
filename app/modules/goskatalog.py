
import requests
from modules.credentials import (
    API_SECRETS,
    GK_ALL_MUSEUM_LIST,
    GK_SINGLE_MUSEUM_LIST,
    MONGO
    )
from modules.functions import get_credentials
from dictor import dictor
from pymongo import MongoClient

YANDEX_RUBRIC_ID = ""
COUNTRY = "Россия"
class Museum:
    def __init__(self, data):
        self.data = data
        self.gk_museum_id = None
        self.museum_inn = None

    def is_exist(self, conn):
        __get_gk_museum_id()
        if self.gk_museum_id is None:
            return False
        if conn.find_one({"gk_museum_id":self.gk_museum_id}):
            return True
        return False

    def has_inn(self):
        pass

    def add(self,conn):
        data_to_append = {
                "museum_gk_id": self.museum_gk_id,
                "inn": self.museum_inn,
                "company-id": __get_museum_id(),
                "name": __get_museum_name(),
                "country": COUNTRY,
                "address": __get_museum_address(),
                "phone": __get_museum_phone(),
                "email": __get_museum_email(),
                "url": __get_museum_website(),
                "booking-url": __get_museum_exhibits_url(),
                "workingTime": None,
                "rubric-id": YANDEX_RUBRIC_ID
            }
        conn.insert_one(data_to_append)

    def update(self, conn):
        pass
    
    def __get_gk_museum_id(self):
        self.gk_museum_id = dictor(data, "id")


def update_museum_list_gk():
    """Updating museum list in database

    Returns:
        boolead: True if successfull
    """ 

    uri = "mongodb://{}:{}@{}:{}/{}".format(
        MONGO["username"],
        MONGO["password"],
        MONGO["host"],
        MONGO["port"],
        MONGO["db"],
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
        museums_iterated +=1
        museum = Museum(item)
        if museum.is_exist(mongo_conn):
            if museum.update(mongo_conn):
                museums_updated += 1
            continue
        if museum.add(mongo_conn):
            museums_added+=1
    
    print ("Total museums is {}".format(museums_total))
    print ("Iterated {}. Updated {}. Added new {}.".format(museums_iterated, museums_updated, museums_added))
    return True

def get_data_from_gk():
    username, password = get_credentials("webGoskatalog")

    print ("Getting data from GK")
    try:
        goskatalogData = requests.get(
            GK_ALL_MUSEUM_LIST, auth=HTTPBasicAuth(username, password)
        ).json()["museums"]
        print("Received data from Goskatalog")
        return goskatalogData
    except Exception as err:
        print("There was an error. {}". format(err))
        return False


#TODO add function that check all the museums by last update date
def check_if_museum_alive():
    pass