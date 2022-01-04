from discord.ext import commands
from discord.ext import tasks
import discord
from itertools import cycle
import os
from dotenv import load_dotenv
import asyncio
from ytsearch import searchr
from discord.utils import get
from discord import FFmpegPCMAudio
from youtube_dl import YoutubeDL
from pafys import pafy

list_to_play = []
paused = False
queue = False

load_dotenv()
TOKEN = os.getenv("TOKEN")

bot = commands.Bot(command_prefix='-')
@bot.event
async def on_ready():
  for guild in bot.guilds:
    print(
    f'{bot.user} is connected to the following guild(s):\n'
    f'{guild.name}(id: {guild.id})'
    )
  change_status.start()
  play_the_list.start()
  
status = cycle(['Music is here!','More features soon!'])

@tasks.loop(seconds=10)
async def change_status():
  await bot.change_presence(activity=discord.Game(next(status)))

#verbose: True

async def playa(ctx,url):
    await stop(ctx)
    YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist':   'True','verbose': 'True'}
    FFMPEG_OPTIONS = {
          'before_options': '-reconnect 1   -reconnect_streamed 1 -reconnect_delay_max 5',  'options': '-vn'}

    voice = get(bot.voice_clients, guild=ctx.guild)
    with YoutubeDL(YDL_OPTIONS) as ydl:
          info = ydl.extract_info(url, download=False)
          URL = info['url']
          voice.play(FFmpegPCMAudio(URL, **FFMPEG_OPTIONS))
          voice.is_playing()


@tasks.loop(seconds=3)
async def play_the_list():
  global list_to_play
  global paused
  global queue
  
  try:

    if paused == False:
      
        if len(list_to_play) != 0:
          ctx = list_to_play[0][1]
          url = list_to_play[0][0]

          voice = get(bot.voice_clients, guild=ctx.guild)
          if queue == True and voice.is_playing() == False:

              await playa(list_to_play[0][1],list_to_play[0][0])
              del list_to_play[0]
              
              ttl = await getitle(url)

              vgid = await get_id_ov(url)
              embed=discord.Embed(title="**Now playing:**", color=0xFF0000,url=url)
              embed.add_field(name=ttl, value = f"by {await getauth(url)}", inline=False)
              tmb = f"https://img.youtube.com/vi/{vgid}/default.jpg"
              embed.set_thumbnail(url=tmb)

              await ctx.send(embed=embed)

          elif len(list_to_play) == 1 and queue == False:
              await playa(list_to_play[0][1],list_to_play[0][0])
              del list_to_play[0]
              ttl = await getitle(url)

              vgid = await get_id_ov(url)
              embed=discord.Embed(title="**Now playing:**", color=0xFF0000,url=url)
              embed.add_field(name=ttl, value = f"by {await getauth(url)}", inline=False)
              tmb = f"https://img.youtube.com/vi/{vgid}/default.jpg"
              embed.set_thumbnail(url=tmb)

              await ctx.send(embed=embed)

  except:
    pass


async def getitle(url):    
  video = pafy.new(url)
  return video.title

async def getauth(url):    
  video = pafy.new(url)
  return video.author


#youtu.be/[id]
#youtube.com/watch?v=[id]
#youtube.com/v/[id]
#youtube.com/embed/[id]


async def get_id_ov(url):
  
  strtr = url[12:]
  strtr2 = ""
  strtr3 = ""

  for i in list(strtr):
    if i == "/":
      break
    else:
      strtr2 += i

  strtr3 = strtr[(len(strtr2)+1):]

  if strtr2 == "youtu.be":
    return strtr3[:11]
  elif strtr3[:8] == "watch?v=":
    return strtr3[8:19]
  elif strtr3[:2] == "v/":
    return strtr3[2:13]
  elif strtr3[:6] == "embed/":
    return strtr3[6:17]
  

@bot.command(name="play",help="Plays the first Youtube result from the input you give. Usage:   -play [search here]   Example:   -play Never Gonna Give You Up",aliases=["p"])
async def play(ctx,*args):
  global list_to_play
  global queue
  queue = False
  plyinp = ""
  inpvalid = True
  result = []
  
  if len(args) != 0:
    for i in args:
      plyinp += f'{i} '
  else:
    await ctx.send("Invalid input.")
    inpvalid = False
  
  if inpvalid == True:

    result = searchr(plyinp,1)
    vidurl = result[0][1]

    list_to_play = [[vidurl, ctx]]
    
      
      
  

@bot.command(name="search",help="Gets the top ten results for your search. Usage: -search [search here]  Example: -search Crab Rave",aliases=["s"])
async def search(ctx,*args):
  global list_to_play
  global queue
  queue = False
  plyinp = ""
  inpvalid = True
  sresult = []
  sendstr = ""
  sendstrint = 0
  
  if len(args) != 0:
    for i in args:
      plyinp += f'{i} '
  else:
    await ctx.send("Invalid input.")
    inpvalid = False
  if inpvalid == True:
    sendstr = f"Top results for {plyinp}:\n"
    sresult = searchr(plyinp,10)
    for i in sresult:
      sendstrint += 1
      sendstr += f"{sendstrint}.  {i[0]}\n"
    sendstr += "\nChoose one to continue:"

    def check(msg):
      return msg.author == ctx.author and msg.channel == ctx.channel and ("1" in msg.content or "2" in msg.content or "3" in msg.content or "4" in msg.content or "5" in msg.content or "6" in msg.content or "7" in msg.content or "8" in msg.content or "9" in msg.content or "10" in msg.content)

    await ctx.send(sendstr)

    try:
      nmessage = await bot.wait_for("message", check=check, timeout=20)
    except asyncio.TimeoutError:
      await ctx.send("Timed out.")
    else:

      vidurl = (sresult[int(nmessage.content)-1])[1]
      
    list_to_play = [[vidurl,ctx]]
      
      
      



@bot.command(name="join",help="Joins a vc. Usage: -join  Example: -join (use while in vc)")
async def join(ctx):
    channel = ctx.message.author.voice.channel
    voice = get(bot.voice_clients, guild=ctx.guild)
    if voice and voice.is_connected():
        await voice.move_to(channel)
    else:
        voice = await channel.connect()

@bot.command(name="leave",help="Leaves a vc. Usage: -leave  Example: -leave (use while in vc)")
async def leave(ctx):
    global list_to_play
    await ctx.voice_client.disconnect()
    list_to_play = []

@bot.command(name="resume",help="Resumes playig whatever it was before.")
async def resume(ctx):
    voice = get(bot.voice_clients, guild=ctx.guild)
    global paused

    if not voice.is_playing():
        voice.resume()
        paused = False


@bot.command()
async def pause(ctx):
    voice = get(bot.voice_clients, guild=ctx.guild)
    global paused

    if voice.is_playing():
        voice.pause()
        paused = True
        


@bot.command()
async def stop(ctx):
    voice = get(bot.voice_clients, guild=ctx.guild)
    global list_to_play
    
    if voice.is_playing():
        voice.stop()  
        list_to_play = []

  

@bot.command(name="url")
async def pburl(ctx,url):
  global list_to_play
  list_to_play = [[url,ctx]]


@bot.command(name="queue",help="usage: -queue")
async def queue(ctx,*args):
  global list_to_play
  global queue
  plyinp = ""
  inpvalid = True
  result = []
  sresult = []
  sendstr = ""
  sendstrint = 0

  if len(args) != 0:
    for i in args:
      plyinp += f'{i} '
  else:
    await ctx.send("Invalid input.")
    inpvalid = False

  if inpvalid == True:

    if len(args) != 0:

      if args[0] == "name":
        result = searchr(plyinp,1)
        vidurl = result[0][1]
        list_to_play.append([vidurl, ctx])
      elif args[0] == "url":
        vidurl = args[1]
        list_to_play.append([vidurl, ctx])
      elif args[0] == "clear":
        list_to_play = []
      elif args[0] == "search":
        sendstr = f"Top results for {plyinp}:\n"
        sresult = searchr(plyinp,10)
        for i in sresult:
          sendstrint += 1
          sendstr += f"{sendstrint}.  {i[0]}\n"
        sendstr += "\nChoose one to continue:"

        def check(msg):
          return msg.author == ctx.author and msg.channel == ctx.channel and ("1" in msg.content or "2" in msg.content or "3" in msg.content or "4" in msg.content or "5" in msg.content or "6" in msg.content or "7" in msg.content or "8" in msg.content or "9" in msg.content or "10" in msg.content)

        await ctx.send(sendstr)

        try:
          nmessage = await bot.wait_for("message", check=check, timeout=20)
        except asyncio.TimeoutError:
          await ctx.send("Timed out.")
        else:

          vidurl = (sresult[int(nmessage.content)-1])[1]

        list_to_play.append([vidurl,ctx])
        

@bot.command(name="next",help="-next outputs videos in queue")
async def qnxt(ctx):
  global list_to_play
  otp = ""

  if len(list_to_play) != 0:
    for i in list_to_play:
      otp += f"1)  {await getitle(i[0])}\n"
  else:
    otp = "Nothing in queue."
  await ctx.send(otp)

#Create playlists (maybe from yt playlist, somehow search in playlists?) probably just from -playlist add (name, url).

#play live vidoes... may be too hard... more research needed (into ffmpeg, youtube-dl ; read the docs)

#make the gui look better/give more responses for what its doing... in progress


bot.run(TOKEN) 
