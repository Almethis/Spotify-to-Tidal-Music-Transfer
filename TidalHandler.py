import json
import tidalapi
from tidalapi import Track
import time
import random



def create_playlist(session, playlistname):
    #Creates a tidal playlist
    descrption="Playlist ported over Via Almethis' FREE Music Transfer on Github."
    playlist = session.user.create_playlist(playlistname, descrption)

    return playlist

def build_playlist(session, tidal_playlist, spotify_playlist):
    #Takes Spotify Playlist json and turns into a tidal playlist

    tidal_tracks = []
    for song in range(len(spotify_playlist["items"])):

        tracks = spotify_playlist["items"][song]["track"]

        

        name= tracks['name']
        artist = tracks['artists'][0]['name']
        #album = tracks['album']['name']
        query = name + " " + artist
        try:
            results = session.search(query=query, models=[Track])
        except AttributeError as e:
            print(f"I got the following exception : {e}")
            if e == "JSONDecodeError":
                print("Since I got a json error for to many request in a short time im going to take a nap! ")
                time.sleep(10)
                print("Resuming")
            results = session.search(query=query, models=[Track])


        found = False

        for result in results["tracks"]:
            if result.name == name and result.artist.name == artist:
                # This is the matching Tidal track
                tidal_track = result
                tidal_tracks.append(tidal_track.id)
                found = True
                break

        if found == False:
            print(" I was unable to locate: " , name , " by ", artist)
            #To Do add a album search method to see if we can locate it

    

    #We just made 100 Api request in like.. a second this gives the server a break so our authenticaion does not get revoked.
    print("Sleeping for up to 5 secs")
    time.sleep(random.randint(1,5))
    print("Waking back up")

    tidal_playlist.add(tidal_tracks)




def login():
    #Logs us into our Tidal Account
    session = tidalapi.Session()
    session.login_oauth_simple()


    print("\n\nNow Authenticating to Tidal")

    print("Token Type: ", session.token_type)
    print("\n Access Token: ", session.access_token)
    print("Token Expires: ", session.expiry_time)

    return session


