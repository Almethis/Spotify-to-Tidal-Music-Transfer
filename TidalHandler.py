import json
import tidalapi
from tidalapi import Track
from tidalapi import Album
from tidalapi import Artist
import time
import random
from fuzzywuzzy import fuzz
import re



def create_playlist(session, playlistname):
    #Creates a tidal playlist
    descrption= f"{playlistname} ported over Via Almethis' FREE Music Transfer on Github."
    playlist = session.user.create_playlist(playlistname, descrption)

    return playlist

def build_playlist(session, tidal_playlist, spotify_playlist, not_found):
    #Takes Spotify Playlist json and turns into a tidal playlist

    tidal_tracks = []
    for song in range(len(spotify_playlist["items"])):

        tracks = spotify_playlist["items"][song]["track"]


        

        t_name= tracks['name']
        artist = tracks['artists'][0]['name']
        album = tracks['album']['name']
        


        #1. Check for song
        #2. See if we can find it via the Album
        #3. See if we can find the Artist and then check agaisnt all their songs. Some Albums just are not on Tidal.

        if not find_track(session, t_name, artist, tidal_tracks):
            find_album(session, t_name, album, artist,tidal_tracks, not_found)
            
            # Future functionality if the API ever allows to see all the tracks that belong to the Artist    
                #if not find_artist(session, t_name, artist, tidal_tracks):
                #    print(" I was unable to locate: " , t_name , " by ", artist)
                    
    #We just made 100 Api request in like.. a second this gives the server a break so our authenticaion does not get revoked.
    time.sleep(random.randint(2,5))

    tidal_playlist.add(tidal_tracks)

    #print(f"DEBUG: Total # of tidal_tracks: {len(tidal_tracks)}")
    #print(f"DEBUG Tidal Tracks: {tidal_tracks}")
    #print(f"DEBUG: TIDAL PLAYLIST Sees: {tidal_playlist.tracks()}")
    #print(f"DEBUG: TIDAL PLAYLIST LEN: {len(tidal_playlist.tracks())}")

    return not_found

    


def check_name(song_name, possible_match):

    i_threashold = 95 #If its a near exact match just take it, otherwise it just spams you, Setting to 90% may result in "Live" versions sneaking in
    threshold = 80 # If were matching 80% of characters.
    similarity_score = fuzz.token_sort_ratio(song_name.lower(), possible_match.lower())

    if similarity_score > i_threashold: return True 

    if similarity_score > threshold: 
        print(f"Possible match between (Spotify) {song_name} and (Tidal) {possible_match}  {similarity_score}% please double check! Is this correct?: ")
        if input("y or n: ") == "y":
            return True
    else: return False


def login():
    #Logs us into our Tidal Account
    session = tidalapi.Session()
    session.login_oauth_simple()


    #print("Token Type: ", session.token_type)
    #print("\n Access Token: ", session.access_token)
    #print("Token Expires: ", session.expiry_time)

    return session

def find_track(session, track, artist, tidal_tracks):
    found = False
    
    query = re.sub(r'[^a-zA-Z0-9\s]', '', track) + " " + artist #removes special charcters for search
    
    try:
        results = session.search(query=query, models=[Track])
    except AttributeError as e:
        print(f"I got the following exception : {e}")
        if e == "JSONDecodeError":
            print("Since I got a json error for to many request in a short time im going to take a nap! ")
            time.sleep(10)
            print("Resuming")
        results = session.search(query=query, models=[Track])



    if "tracks" in results and len(results["tracks"]) !=0 :
        for result in results["tracks"]:
            if (result.artist.name == artist and result.name == track) or check_name(track, result.full_name):
                # This is the matching Tidal track
                tidal_track = result
                tidal_tracks.append(tidal_track.id)
                found = True
                break

    return found


def find_album(session, t_name, album, artist, tidal_tracks, not_found):
    found = False

    query = album + " " + artist

    try:
        results = session.search(query=query, models=[Album])
    except AttributeError as e:
        print("Since I got a json error for to many request in a short time im going to take a nap! ")
        time.sleep(10)
        print("Resuming")
        results = session.search(query=query, models=[Album])

    if "albums" in results and len(results["albums"]) !=0 : #Validating we didnt get nothing back from our search
        for album in results["albums"]: 
            if album.artist.name == artist: #If the album wasn't made by our artist skip it
                for track in album.tracks():
                    if (track.name == t_name and track.artist.name == artist)  or check_name(t_name, track.full_name) :
                        tidal_track = track
                        tidal_tracks.append(tidal_track.id)
                        found = True
                        
                        break
                if found == True: break
    if not found:
        not_found.append(f"Song: {t_name} Artist: {artist}")
        print(f"Unable to find {t_name} by {artist}")
    return found


#Unused, not currently functional as the Artist object does not contain all the tracks belonging to the Artist

def find_artist(session, t_name, artist, tidal_tracks):
    found = False
    query = artist

    try:
        results = session.search(query=query, models=[Artist])
    except AttributeError as e:
        print("Since I got a json error for to many request in a short time im going to take a nap! ")
        time.sleep(10)
        print("Resuming")
        results = session.search(query=query, models=[Artist])

    if "artists" in results and len(results["artists"]) != 0:
        for band in results["artists"]:
            if band.name == artist: #Make sure we have the right Artist before we begin
                for track in band.tracks():
                    if (track.name == t_name and track.artist.name == artist)  or check_name(t_name, track.full_name) :
                        tidal_track = track
                        tidal_tracks.append(tidal_track.id)
                        found = True
                        
                        break
                if found == True: break
    if not found: print(f"Artist: {artist} Song: {t_name} was unavailable or not found on Tidal!")
    return found
