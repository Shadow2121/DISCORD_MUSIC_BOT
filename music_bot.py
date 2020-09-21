import youtube_dl
import discord
from discord.ext import commands
from discord.utils import get
import os


token = "NzQ2MjQ2NzU2NzYwNjgyNTg4.Xz9icw.t7mI0hQ8Ky_Vjcg61Q8mpH317o0"
bot_prefix = ">"

bot = commands.Bot(command_prefix=bot_prefix)

@bot.event
async def on_ready():
    print("Loged in as: " + bot.user.name + "\n")

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

@bot.command(pass_context=True, alianes=['l', 'lea'])
async def leave(ctx):
    global voice
    channel = ctx.message.author.voice.channel
    voice = get(bot.voice_clients, guild=ctx.guild)

    if voice and voice.is_connected():
        await voice.disconnect()
        print(f"bot has left the  {channel}")
        await ctx.send(f"Left the {channel}")
    else:
        print("Bot is not in any channel")
        await ctx.send("Don't think I am in any channel")

@bot.command(pass_context=True, alianes=['p', 'pla'])
async def play(ctx, url: str):
    song_there = os.path.isfile("song.mp3")
    try:
        if song_there:
            os.remove("song.mp3")
            print("Removed old song file\n")
    except PermissionError:
        print("Trying to delet song file, but it is playing")
        await ctx.send("Error: Song is currently playing")
        return

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

@bot.command(pass_context=True, alianes=['pa', 'pau'])
async def pause(ctx):

    voice = get(bot.voice_clients, guild = ctx.guild)

    if voice and voice.is_playing():
        voice.pause()
        print("music paused")
        await ctx.send("Music paused")
    else:
        print("Song is not playing")
        await ctx.send("Song is not playing [Failed Pause]")


@bot.command(pass_context=True, alianes=['r', 'res'])
async def resume(ctx):

    voice = get(bot.voice_clients, guild=ctx.guild)

    if voice and voice.is_paused():
        voice.resume()
        print("Song is resumed")
        await ctx.send("Song resumed")
    else:
        print("Song is not paused")
        await ctx.send("Song is not paused [Resume Failed]")


@bot.command(pass_context=True, alianes=['s', 'sto'])
async def stop(ctx):
    voice = get(bot.voice_clients, guild=ctx.guild)

    if voice and (voice.is_playing() or voice.is_paused()):
        voice.stop()
        print("music stoped")
        await ctx.send("Music stoped")
    else:
        print("Song is not playing")
        await ctx.send("Song is not playing [Stop Failed]")




bot.run(token)