import requests
import json

from env import config
from requests_toolbelt.multipart.encoder import MultipartEncoder


s = requests.Session()
s.headers.update({
    "Content-Type": "application/x-www-form-urlencoded",
    'Authorization': f"Bearer {config['WEBEX_ACCESS_TOKEN']}"
})
WEBEX_BASE_URL = config['WEBEX_BASE_URL']
desiredRoom = "CSAP Programmability CTF - Team 1"
participants = ["mneiding@cisco.com","frewagne@cisco.com"]

# Verify api access
def verifyAccess():
    url = f"{WEBEX_BASE_URL}/v1/people/me"

    resp = s.get(url)

    if resp.status_code == 200:
        print("Webex Access verified")

# Get list of all rooms
def getRooms():
    room_url = f"{WEBEX_BASE_URL}/v1/rooms?type=group"
    resp = s.get(room_url)
    parsed = json.loads(resp.text)

    if resp.status_code == 200:
        print("Webex rooms succesfully collected")
    else:
        print(f"Webex status code: {resp.status_code}")

    #print(json.dumps(parsed, indent=4,sort_keys=True))
    return parsed

# Find room id for specific room
def findRoomId(data, theRoom):
    for entry in data["items"]:
            if theRoom == entry["title"]:
                return entry["id"]

# Write dictionary into JSON file
def write_json(data):
    with open("getSomeRooms" + ".json", "w") as f:
        try:
            f.write(json.dumps(data, indent=4, sort_keys=True))
        except:
            print("Something went wrong")
    f.close()
    print("Result written to " + "getSomeRooms" + ".json")

# Creates a new room with the name from the input
def createRoom(roomName):
    url = f"{WEBEX_BASE_URL}/v1/rooms"
    payload = {"title": roomName}
    response = s.post(url, data=payload)

    if response.status_code == 200:
        print("Webex room " + roomName + " succesfully created")
    else:
        print(f"Webex status code: {response.status_code}")

    return response.json()["id"]

# Adds new users stored in user_emails
def addUsers(user_emails, roomId):
    for user_email in user_emails:
        url = f"{WEBEX_BASE_URL}/v1/memberships"
        payload = {"roomId": roomId, "personEmail": user_email}
        response = s.post(url, data=payload)

    if response.status_code == 200:
        print("Users added to the room")
    else:
        print(f"Webex status code: {response.status_code}")

# Sends a message to a room
def sendMessage(message, roomId):
    url = f"{WEBEX_BASE_URL}/v1/messages"
    #payload = {"roomId": roomId, "text": message}
    payload = MultipartEncoder({"roomId": roomId, "text": message, "files": ('josef.jpg', open('josef.jpg', 'rb'),'image/jpeg')})
    s.headers = {
        "Authorization": f"Bearer {config['WEBEX_ACCESS_TOKEN']}",
        "Content-Type": payload.content_type
    }
    response = s.post(url, data=payload)

    if response.status_code == 200:
        print("Message succesfully send")
    else:
        print(f"Webex status code: {response.status_code}")

# Create meeting 
def createMeeting():
    url = f"{WEBEX_BASE_URL}/v1/meetings"
    s.headers = {
        "Authorization": f"Bearer {config['WEBEX_ACCESS_TOKEN']}",
        "Content-Type": "application/json"
    }
    payload = {
        "title": "Pace appreciation event",
        "start": "2021-03-11 07:00:00",
        "end": "2021-03-11 07:11:00",
        "enabledAutoRecordMeeting": False,
        "invitees": [
            {
            "email": "stienvan@cisco.com",
            "displayName": "Queen of the Cheerleaders",
            "coHost": False
            }
        ]
    }
    response = s.post(url, json=payload)
    print(response.text)
    print(response.status_code)


# Get list of meetings 
def getMeetings():
    url = f"{WEBEX_BASE_URL}/v1/meetings"
    s.headers.update({
        "Content-Type": "application/json"
    })
    # payload = {
    #     "from": "2020-08-11 07:00:00",
    #     "to": "2021-03-11 07:11:00",
    #     "current": False,
    #     "state": "expired"
    # }

    response = s.get(url) #, json = payload)
    parsed = json.loads(response.text)
    return parsed

# Retrieve all messages from all rooms
def msgCount(data):
    nb_list = {}
    for entry in data["items"]:
        roomName = entry["title"]
        roomId = entry["id"]

        url = f"{WEBEX_BASE_URL}/v1/messages?roomId={roomId}"
        response = s.get(url)
        parsed = json.loads(response.text)

        nb_list[roomName] = len(parsed["items"])
        print(nb_list[roomName])
    return nb_list
        


# MAIN
verifyAccess()
rooms = getRooms()
# roomId = findRoomId(rooms, desiredRoom)
# print(roomId)
# config['PRODUCTION_ROOM'] = roomId


# newRoom = createRoom("Stories from an ancient time")
# addUsers(participants, newRoom)
# sendMessage("Let's get some juicy stories on the table about this guy <3", newRoom)

# createMeeting()
# meetinglist = getMeetings()
# print(len(meetinglist["items"]))
# print(json.dumps(meetinglist, indent=4, sort_keys=True))

numberOfMessages = msgCount(rooms)
print(numberOfMessages)
