import json
import SpotifyHandler
import TidalHandler

title = r"""
  _________              __  .__  _____          __           ___________.__    .___      .__    ___________                              _____             
 /   _____/_____   _____/  |_|__|/ ____\__.__. _/  |_  ____   \__    ___/|__| __| _/____  |  |   \__    ___/___________    ____   _______/ ____\___________ 
 \_____  \\____ \ /  _ \   __\  \   __<   |  | \   __\/  _ \    |    |   |  |/ __ |\__  \ |  |     |    |  \_  __ \__  \  /    \ /  ___/\   __\/ __ \_  __ \
 /        \  |_> >  <_> )  | |  ||  |  \___  |  |  | (  <_> )   |    |   |  / /_/ | / __ \|  |__   |    |   |  | \// __ \|   |  \\___ \  |  | \  ___/|  | \/
/_______  /   __/ \____/|__| |__||__|  / ____|  |__|  \____/    |____|   |__\____ |(____  /____/   |____|   |__|  (____  /___|  /____  > |__|  \___  >__|   
        \/|__|                         \/                                        \/     \/                             \/     \/     \/            \/     
                                                                                                                                by Almethis  
"""

print(title)

client_id = input("Please enter your Spotify Client ID (You get this from the devloper dashboard: ")
client_secret = input("Please enter your Client Secret: ")


print("Logging into Spotify")
#Spotify Login
spotify_login = SpotifyHandler.login(client_id, client_secret)

print("Logging into Tidal")
#Tidal login
tidal_login = TidalHandler.login()


choice = input("\nWhat would you like to do? \n1. Move all user playlist from Spotify to Tidal\n2. Move Single Playlist\n3. Exit program\n: ")

   

def single_playlist(playlist):


    name = SpotifyHandler.get_playlist_name(spotify_login, playlist)
    tidal_playlist = TidalHandler.create_playlist(tidal_login,name)
    spotify_playlist = SpotifyHandler.request_tracks(spotify_login, playlist)

    print(f"Begining Transfer of: {SpotifyHandler.get_playlist_name(spotify_login, playlist)}")


    total_songs = spotify_playlist["total"]
    total = total_songs
    not_found = []
    offset = 0

    while total_songs > 0:
        not_found = TidalHandler.build_playlist(tidal_login, tidal_playlist, spotify_playlist, not_found)
        offset = offset +100
        total_songs= total_songs - 100
        spotify_playlist = SpotifyHandler.request_tracks(spotify_login, playlist, offset)
        if 0 > total_songs:
            break
        print(f"Songs Remaining: {total_songs}")
    
    print(f"Playlist {tidal_playlist.name} Created! ")



    # STATS
    s_nfound = len(not_found)
    s_found = total - s_nfound
    if s_nfound != 0:
        s_fpercent = s_found / total
    else: s_fpercent = 100
    if s_fpercent == 100: s_fpercent = s_fpercent / 100 #This makes it so we dont have 10000% success rates 
    print(f"A total of {s_found} / {total} were successfully transferred at a rate of: {s_fpercent:.2%}")
    print("Unable to find the folowing: ")
    for x in range(len(not_found)):
        print(not_found[x])


def all_playlist(user_id):

    spotify_playlists = SpotifyHandler.request_all_playlist(spotify_login, user_id)

    for key in spotify_playlists.keys():
        print(f"Found the following Playlist: {key}")

    for key in spotify_playlists.keys():
        single_playlist(spotify_playlists[key])

     


while choice != "3":

    if choice == "1":
        all_playlist(input("Please enter your Spotify user id: You can get this from visting your profile. The URL will look like https://open.spotify.com/user/<Your user ID> : "))
    elif choice == "2":
        single_playlist(input("Please enter Playlist ID: "))

    choice = input("What would you like to do? \n1. Move all user playlist from Spotify to Tidal\n2. Move Single Playlist\n3. Exit program\n: ")
        


