import json

def getCredentials(systemName):
    try:
        with open("auth.json") as auth_json:
            data = json.load(auth_json)
        return [data[systemName]["username"], data[systemName]["password"]]
    except KeyError:
        print("There is no credentials for " + systemName)




