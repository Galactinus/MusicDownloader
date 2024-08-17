#!/bin/python3

import re
from pytube import YouTube  # library to donwload songs and urls
from pytube import Playlist  # library do donwload playlists
# library to gather ytmusic search results with urls, artworks and other metadatas
from ytmusicapi import YTMusic
from pydub import AudioSegment  # lib to convert audio formats
AudioSegment.converter = r"C:\Users\chadb\Downloads\ffmpeg.exe"
# execute os level commands, used to clean temporary files (webm) after download
import os
import music_tag  # lib to add tags and artworks to mp3 files
import wget  # (wget) gather files from the web
from PIL import Image  # image manipulation, used to crop artworks from yt canvas

ytmusic = YTMusic()

# check if the path variable is not define and ask the user to define one
if os.path.isfile("path.txt") == False:
    path = input("Paste here ur preferred download directory: ").strip()
    with open('path.txt', 'w') as f:
        f.write(path)
else:  # if the path_var is defined ask the user if he wanna update it
    with open('path.txt', 'r') as f:
        path = f.read().strip()
    if input(f"Current Download path: {path} - wanna update? (y/n)").strip() == "y":
        path = input("Paste here ur preferred download directory: ").strip()
        with open('path.txt', 'w') as f:  # write the new path_var to the file
            f.write(path)


def term_text(txt):  # formatting text to be terminal friendly
    if(os.name == 'nt'):
        txt = txt.replace(" ", "/ ")
        txt = txt.replace("(", "/(")
        txt = txt.replace(")", "/)")
    else:
        txt = txt.replace(" ", "\ ")
        txt = txt.replace("(", "\(")
        txt = txt.replace(")", "\)")
    return txt

def recurs_delete(path):
    if os.name == "nt":
        os.system(f"del /S {path}")  # clean webm files
    else:
        os.system(f"rm -r {term_text(file_path)}")  # clean webm files

def down_song(link):  # function to download songs
    yt = YouTube(link)
    print(f"\nDonwloading {yt.title}")
    file_path = f"{path}{yt.author.replace(' - Topic', '')} - {yt.title.replace('/','-')}.webm"
    print(yt.streams)
    yt.streams.filter(only_audio=True, abr="160kbps").first().download(
        output_path=f"{path}", filename=f"{yt.author.replace(' - Topic', '')} - {yt.title.replace('/','-')}.webm")
    try:
        mp3_conv(file_path, file_path.replace("webm", "mp3"))
        tags_and_art(file_path.replace("webm", "mp3"),
                     yt.title, None, yt.author.replace(' - Topic', ''), None, yt.thumbnail_url)

    except Exception as e:
        return("mp3_conv or tags_and_art failed: ", e)
    recurs_delete(term_text(file_path))

    print("\nDONE\n")


def down_plist(link):  # function do download playlists
    full_pattern = re.compile('[^/-_ a-zA-Z0-9\\/]')
    p = Playlist(link)
    title = p.title.replace("Album - ", "")      
    title = title.replace('/','-')
    title = title.replace(' ', '_')
    title = re.sub(full_pattern, '', title)
    numb = 1
    print(f"Downloading {title}\n")


    for song in p.videos:
        # Format song title
        song_title = song.title.replace('/','-')
        song_title = song_title.replace(' ', '_')
        song_title = re.sub(full_pattern, '', song_title)

        # format song author
        song_author = song.author.replace(' - Topic', '')
        song_author = song_author.replace('/','-')
        song_author = song_author.replace(' ', '_')
        song_author = re.sub(full_pattern, '', song_author)
        # temp path
        temp_path = f"{path}temp_{song_author}-{title}/webm/"
        webm_file_name = f"{song_title}.webm"
        final_file_name = f"{song_title}.mp3"
        print(f"temp_path:{temp_path}")
        print(f"webm_file_name:{webm_file_name}")
        print(f"final_file_name:{final_file_name}")
        print(f"\nDownloading {song_title} by {song_author}")
        song.streams.filter(only_audio=True, abr="160kbps").first().download(
            output_path=temp_path, filename=webm_file_name)
        
        print("Download finished, converting")
        
        try:
            mp3_conv(f"{temp_path}{webm_file_name}",
                     f"{path}{final_file_name}")

        except Exception as e:
            print("Failed to convert to mp3")
            print(f"Source: {temp_path}{webm_file_name} | dest: {path}{final_file_name}")
            return("mp3_conv failed: ", e)
        print("Conversion finished, writing metadata")
        try:
            tags_and_art(f"{path}{final_file_name}",
                         song.title.replace('_', ' '), title, song.author.replace(' - Topic', ''), str(numb), song.thumbnail_url)
        except Exception as e:
            print("Failed setting mp3 tags" + e)
            return("mp3 tags_and_art failed: ", e)
        print(f"Track {numb} finished: {song_title}")
        numb += 1
        # if os.name == 'nt':
        #     os.system(f"move {temp_path}\\{final_file_name} {path}\\")
        # else:
        #     os.system(f"mv {file_path}/{song_title}.mp3 {path}/")
            


        recurs_delete(temp_path)
    print("\nDONE\n")  # clean webm files


# add tags and artwork to the mp3 files
def tags_and_art(file_path, song_name, album, author, trk_nmbr, art_link):
    print(art_link)
    f = music_tag.load_file(file_path)
    f['title'] = song_name
    f['artist'] = author
    if album != None:
        f['album'] = album
    if trk_nmbr != None:
        f['tracknumber'] = trk_nmbr

    file_name = wget.download(art_link)
    image = Image.open(file_name)
    print("\nwidth = " + str(image.width) + " height = " + str(image.height))
    if image.height != image.width:
        if image.height > image.width:
            excess = image.height - image.width
            image = image.crop((0, (excess / 2),  image.width,(image.width + (excess / 2))))
        else:
            excess = image.width - image.height
            image = image.crop(((excess / 2), 0,  (image.height + (excess / 2)), image.height))

    print("\nwidth = " + str(image.width) + " height = " + str(image.height))
    if(image.height > 1200):
        image.resize((1200, 1200))
    print("\nwidth = " + str(image.width) + " height = " + str(image.height))
    image.save("img.jpg")
    with open("img.jpg", 'rb') as img_in:
        f['artwork'] = img_in.read()
    f.save()
    if os.name == "nt":
        os.system('del img.jpg')
        os.system(f'del {term_text(file_name)}')
    else:
        os.system('rm img.jpg')
        os.system(f'rm {term_text(file_name)}')

#convert webm to mp3


def mp3_conv(file_path, out_path):
    webm_audio = AudioSegment.from_file(
        f"{file_path}", format="webm")
    webm_audio.export(
        f"{out_path}", format="mp3")

#main function


def mdown(id, url):
    if id == None:
        link = url
        try:
            down_song(link)

        except Exception as e:
            print("down_song error: ", e)

            try:
                down_plist(link)
            except Exception as err:
                print("down_plist error: ", err)
    else:
        for i in id:
            link = "https://music.youtube.com/"+i
            try:
                down_song(link)

            except Exception as er:
                #print("down_song error: ", er)

                try:
                    down_plist(link)
                except Exception as e:
                    print("down_plist error: ", e)


while True:
    mode = input("Chose MODE album(a) song(s) url(u) quit(q) playlist(l): ")
    if mode.lower().strip() == "a":
        mode = "albums"
        key = "browseId"
    elif mode.lower().strip() == "s":
        mode = "songs"
        key = "videoId"

    elif mode.lower().strip() == "q":
        break
    elif mode.lower().strip() == "l":
        url = input("\n Paste URL here: ")
        down_plist(url)
        continue

    elif mode.lower().strip() == "u":
        url = input("\npaste URL here: ")
        id = None
        mdown(id, url)
        continue
    else:
        print("sorry try again")
        continue
    try:
        results = ytmusic.search(
            input("\nType the song/album name here (enter to go back) : "), filter=f"{mode}")
    except:
        continue
    print("\nHere's what we found: \n")
    n = 0
    for song in results:
        title = song['title']
        art = song['artists']
        artist = (art[0])['name']
        print(f" {n}: {title} by {artist}")
        n += 1
    sns = input(
        f"\nType in the song/album numbers (0 to {n-1}) separated by a space or search again (enter): ")
    if sns == "":
        continue
    sns = (sns.strip()).split(" ")
    if mode == "albums":
        id = []
        for s in sns:
            alb_dt = ytmusic.get_album(browseId=f"{(results[int(s)])[key]}")
            id.append("playlist?list=" + alb_dt['audioPlaylistId'])
        url = None
        mdown(id, url)
    else:
        id = []
        for s in sns:
            id.append("watch?v=" + (results[int(s)])[key])
        url = None
        mdown(id, url)
