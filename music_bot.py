import youtube_dl
import discord
from discord.ext import commands
from discord.utils import get
import os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ActionChains
import time
import speech_recognition as sr
import threading
import asyncio
import pyttsx3

PATH = "C:\Program Files (x86)\chromedriver.exe"

def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

def get_audio():
    print("get_audio started")
    r = sr.Recognizer()
    r.energy_threshold = 4000
    with sr.Microphone() as source:
        audio = r.listen(source)
        said = ""

        try:
            said = r.recognize_google(audio)
        except Exception as e:
            print(e)
        print(said)
    return said.lower()



token = ''  ## put your bot's token
bot_prefix = ">"

bot = commands.Bot(command_prefix=bot_prefix)

@bot.event
async def on_ready():
    print("Loged in as: " + bot.user.name + "\n")

async def my_task(ctx):
    while True:
        tt = False
        text = get_audio()
        t = text.split(" ")
        if t[0] == "join":
            await join(ctx)
            tt = True
        if t[0] == "leave" or t[0] == "live":
            await leave(ctx)
            tt = True
        if t[0] == "pause":
            await pause(ctx)
            tt = True
        if t[0] == "resume":
            await resume(ctx)
            tt = True
        if t[0] == "stop":
            await stop(ctx)
            tt = True
        if t[0] == "play":
            temp = t[1:]
            song_name = " ".join(temp)
            await play (ctx, song_name)
        if not tt:
            await asyncio.sleep(10)

@bot.command()
async def start_bot(ctx):
    bot.loop.create_task(my_task(ctx))

@bot.command(pass_context=True, alianes=['j', 'joi'])
async def join(ctx):
    # server = ctx.message.server
    # print(server)

    global voice
    channel = ctx.message.author.voice.channel
    voice = get(bot.voice_clients, guild=ctx.guild)

    if voice and voice.is_connected():
        await voice.move_to(channel)
    else:
        voice = await channel.connect()
        print(f"the bot has connected to {channel}\n")
    await ctx.send(f"Joind {channel}")

    await voice.disconnect()

    if voice and voice.is_connected():
        await voice.move_to(channel)
    else:
        voice = await channel.connect()
    
    speak("Joined the channel")


@bot.command(pass_context=True, alianes=['l', 'lea'])
async def leave(ctx):
    speak("leaving the channel")
    global voice
    channel = ctx.message.author.voice.channel
    voice = get(bot.voice_clients, guild=ctx.guild)

    if voice and voice.is_connected():
        await voice.disconnect()
        print(f"bot has left the  {channel}")
        await ctx.send(f"Left the {channel}")
    else:
        print("Bot is not in any channel")
        speak("Don't think I am in any channel")
        await ctx.send("Don't think I am in any channel")

@bot.command(pass_context=True, alianes=['p', 'pla'])
async def play(ctx, url: str):
    song_there = os.path.isfile("song.mp3")
    try:
        if song_there:
            os.remove("song.mp3")
            print("Removed old song file\n")
    except PermissionError:
        print("Trying to delete song file, but it is playing")
        await ctx.send("Error: Song is currently playing")
        return

    speak("Getting everything ready now")
    await ctx.send("Getting everything ready now.")
    voice = get(bot.voice_clients, guild = ctx.guild)

    ydl_opts = {
        'format' : 'bestaudio/best',
        'postprocessors' : [{
            'key' : 'FFmpegExtractAudio',
            'preferredcodec' : 'mp3',
            'preferredquality' : '192',
        }],
    }
    driver = webdriver.Chrome(PATH)
    driver.get("https://www.youtube.com")

    search_bar = driver.find_element_by_xpath('/html/body/ytd-app/div/div/ytd-masthead/div[3]/div[2]/ytd-searchbox/form/div/div[1]/input')
    search_bar.send_keys(url)
    search_bar.send_keys(Keys.RETURN)

    first_video = driver.find_element_by_xpath('/html/body/ytd-app/div/ytd-page-manager/ytd-search/div[1]/ytd-two-column-search-results-renderer/div/ytd-section-list-renderer/div[2]/ytd-item-section-renderer/div[3]/ytd-video-renderer[1]/div[1]/ytd-thumbnail/a/yt-img-shadow/img')

    action = ActionChains(driver)

    action.move_to_element(first_video).click()
    time.sleep(2)
    action.perform()
    uurl = driver.current_url
    url = uurl
    driver.quit()

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        print("Downloding audio now\n")
        ydl.download([url])

    for file in os.listdir("./"):
        if file.endswith(".mp3"):
            name = file
            os.rename(file, "song.mp3")
            print(f"Rename file {name}\n")

    voice.play(discord.FFmpegPCMAudio("song.mp3"), after = lambda e:print(f"{name} has stoped playing\n"))
    voice.source = discord.PCMVolumeTransformer(voice.source)
    voice.source.volume = 0.2

    nname = name.rsplit("-", 2)
    await ctx.send(f"Playing: {nname[0]}")
    print("Playing")
    speak("Playing the song")

@bot.command(pass_context=True, alianes=['pa', 'pau'])
async def pause(ctx):

    voice = get(bot.voice_clients, guild = ctx.guild)

    if voice and voice.is_playing():
        voice.pause()
        print("music paused")
        speak("Song paused")
        await ctx.send("Music paused")
    else:
        print("Song is not playing")
        speak("Song is not playing")
        await ctx.send("Song is not playing [Failed Pause]")


@bot.command(pass_context=True, alianes=['r', 'res'])
async def resume(ctx):

    voice = get(bot.voice_clients, guild=ctx.guild)

    if voice and voice.is_paused():
        voice.resume()
        print("Song is resumed")
        speak("Resuming song")
        await ctx.send("Song resumed")
    else:
        print("Song is not paused")
        speak("Song is not paused")
        await ctx.send("Song is not paused [Resume Failed]")


@bot.command(pass_context=True, alianes=['s', 'sto'])
async def stop(ctx):
    voice = get(bot.voice_clients, guild=ctx.guild)

    if voice and (voice.is_playing() or voice.is_paused()):
        voice.stop()
        print("music stoped")
        await ctx.send("Music stoped")
        speak("Song Stopped")
    else:
        print("Song is not playing")
        await ctx.send("Song is not playing [Stop Failed]")
        speak("Song is not playing")
    


bot.run(token)
