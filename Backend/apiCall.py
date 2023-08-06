from googleapiclient.discovery import build
import pandas
import json
import datetime as dt
from dateutil import tz


api_key = ''
youtube = build(
    'youtube',
    'v3',
    developerKey=api_key
)

# FIRST OPPERATION IS LOAD CSV AND GET ALL CHANNEL IDS
df = pandas.read_csv('../Data/holodash.csv')

# THEN WE PASS ALL THE CHANNEL IDS INTO THE CHANNEL CALL


def getChannelsUploads():
    response = []
    for i, x in df.iterrows():
        request = youtube.channels().list(
            part="contentDetails",
            id=x['ChannelID'],
        )
        response.append(request.execute())
    with open('uploadsIDs.json', 'w+') as file:
        json.dump(response, file, indent=4)
    callPlaylist()

# THEN WE PASS UPLOADS IDS INTO PLAYLISTSITEMS CALL


def callPlaylist():
    response = []
    with open('uploadsIDs.json', 'r') as file:
        data = json.load(file)
    for x in range(len(data)):
        request = youtube.playlistItems().list(
            part="contentDetails",
            playlistId=data[x]['items'][0]['contentDetails']['relatedPlaylists']['uploads']
        )
        response.append(request.execute())

    with open('playlistdetails.json', 'w+') as file:
        json.dump(response, file, indent=4)
    videoCall()

# THEN WE PASS EACH ID INTO THE VIDEOS LIST CALL


def videoCall():
    videoIDs, response = [], []
    with open('playlistdetails.json', 'r') as file:
        data = json.load(file)
    for x in range(len(data)):
        for y in data[x]['items']:
            videoIDs.append(y['contentDetails']['videoId'])

    for k in videoIDs:
        request = youtube.videos().list(
            part="liveStreamingDetails,snippet",
            id=k
        )
        response.append(request.execute())
    with open('finalreturn.json', 'w+') as finalFile:
        json.dump(response, finalFile, indent=4)


results = []
with open('finalreturn.json', 'r+') as file:
    data = json.load(file)
    for x in range(len(data)):
        year = int(data[x]['items'][0]['snippet']['publishedAt'][:4])
        if year < 2023 or year > 2023:
            continue
        else:
            # THIS LOGIC WILL BE BROKEN OUT INTO A VIDEO TYPE CHECK SO I CAN RETURN SEARCH RESULTS
            try:
                startTime = data[x]['items'][0]['liveStreamingDetails']['scheduledStartTime']
            except:
                startTime = data[x]['items'][0]['snippet']['publishedAt']

            try:
                vidtype = data[x]['items'][0]['snippet']['liveBroadcastContent']
            except:
                vidtype = 'Unknown'
            ##
            fdate = dt.datetime.fromisoformat(startTime)
            fromzone = tz.gettz('UTC')
            tozone = tz.tzlocal()
            fdate = fdate.replace(tzinfo=fromzone)
            timez = fdate.astimezone(tozone)
            results.append([data[x]["items"][0]["snippet"]["channelTitle"], data[x]
                           ["items"][0]["snippet"]["title"], timez.strftime("%b %d %y, %I:%M %p"), vidtype])


getChannelsUploads()
