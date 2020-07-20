
import requests
from modules.credentials import (
    API_SECRETS,
    GK_ALL_MUSEUM_LIST,
    GK_SINGLE_MUSEUM_LIST
    )
from modules.functions import get_credentials
from dictor import dictor

class Museum:
    def __init__(self, item):
        self.museum_gk_id_hash
        self.museum_gk_id = museum_gk_id
        self.inn = museum_inn
        self.company_id = dictor(item, "fullUin")
        self.name = dictor(item, "name")
        self.country = "Россия"
        self.address = dictor(item, "addressString")
        self.phone = getMuseumContacts(dictor(item, "contacts"), 1)
        self.email = getMuseumContacts(dictor(item, "contacts"), 2)
        self.url = getMuseumContacts(dictor(item, "contacts"), 3)
        self.booking_url = "https://goskatalog.ru/portal/#/museums?id="+ str(dictor(item, "id"))
        self.working_time = None
        self.rubric_id = "184105894"
    

# TODO add function that updates information about museums
def update_museum_list_gk():
    """Updating museum list in database

    Returns:
        boolead: True if successfull
    """ 

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