######Oktobot#####
#Bot developed by Luna, MJ & Blai

#######IMPORTS#######
import os
import discord
import random
from discord.utils import get #esto es necesario? no lo usamos
from discord.ext import commands
from intra import ic
from bs4 import BeautifulSoup
import requests
from datetime import date

###Discord config####
intents = discord.Intents.all()
intents.members = True  
bot = commands.Bot(command_prefix='!', intents=intents)

######FUNCTIONS######
#Get soup
def get_soup(user):
  link = f"https://bigmom.42barcelona.com/?login={user}"
  soup = BeautifulSoup(requests.get(link).text, 'lxml')
  data = {
    "vidas":soup.find_all("h2", {"id":"login"})[1].text,
    "inicio": soup.find_all("h3")[2].text,
    "final": soup.find_all("h3")[3].text
  }
  return data

#Get login - ONLY TO BE USED WHEN user != None
def get_login(ctx, user):
  login = ""
  if user.startswith("<@") and user.endswith(">"):
    user = user.replace("<@", "")
    user = user.replace(">", "")
    user : discord.Member = ctx.guild.get_member(int(user))
    login = user.display_name
  else:
    login = user
  return login

#######EVENTS########
@bot.event
async def on_ready():
    print("uff")
    await bot.change_presence(activity=discord.Game(name="Dar segfaults"))

@bot.event
async def on_message(message):
  await bot.process_commands(message)


######COMMANDS#######
#Bigmom - enseña la informacion relevante de bigmom del usuario
@bot.command(aliases=["bm"], brief="Enseña la informacion relevante de bigmom del usuario")
async def bigmom(message, target_user = None):
  user = message.author.display_name if target_user is None else get_login(message, target_user)
  data = ic.get(f"https://api.intra.42.fr/v2/users?filter[login]={user}").json()
  
  try:
    bigmom_data = get_soup(user)
  except IndexError:
    await message.send("User no encontrado. Has escrito bien el nombre?")
    return None
    
  msg = discord.Embed(title="Big Mom", color=0xe74c3c)

  msg.add_field(name="Vidas", value=bigmom_data["vidas"], inline=False)
  msg.add_field(name="Inicio Milestone", value=bigmom_data["inicio"], inline=False)
  msg.add_field(name="Final Milestone", value=bigmom_data["final"], inline=False)
  msg.set_author(name= user, icon_url=data[0]["image"]["link"], url=f"https://profile.intra.42.fr/users/{user}")
  
  await message.channel.send(embed=msg)

#Info - Enseña información sobre el usuario especificado
@bot.command(brief="Enseña información sobre el usuario especificado")
async def info(message, user = None):
  user = message.author.display_name if user is None else get_login(message, user)
  try:
    info = ic.get(f"https://api.intra.42.fr/v2/users?filter[login]={user}")
  except Exception:
    await message.send("User no encontrado. Has escrito bien el nombre?")
    return

  if info.status_code == 200:
    try:
        data = info.json()
        aaa = data[0]["correction_point"]
        mon = data[0]["wallet"]
        loc = data[0]["location"]
        idd = data[0]["id"]
        coal = ic.get(f"https://api.intra.42.fr/v2/users/{idd}/coalitions")
        coal = coal.json()
        col = coal[0]["color"]
        coal = coal[0]["name"]
        if loc == None:
            loc = "Fuera del campus"
    except IndexError:
        await message.send("User no encontrado o no tiene perfil. Has escrito bien el nombre?")

    msg = discord.Embed(title="Info", description=f"Puntos: {aaa}\nMonedas: {mon}₳\nEsta en: {loc}\nCoalicion: {coal}", color=int(col[1: ].lower(), 16))
    msg.set_author(name = user, icon_url=data[0]["image"]["link"], url=f"https://profile.intra.42.fr/users/{user}")
    
    await message.channel.send(embed=msg)

#Days - Enseña los dias restantes para el proximo checkpoint y la milestone actual del usuario especificado
@bot.command(brief="Enseña los dias restantes para el proximo checkpoint y milestone")
async def days(message, user = None):
  if random.randint(1, 100) <= 5:
    await message.send("Aprende a contar anda, que tienes la info en !bigmom")
    return

  user = message.author.display_name if user is None else get_login(message, user)
  data = ic.get(f"https://api.intra.42.fr/v2/users?filter[login]={user}").json()

  try:
    bigmom_data = get_soup(user)
  except IndexError:
    await message.send("User no encontrado. Has escrito bien el nombre?")
    return None
    
  info_f = bigmom_data["final"].split(" ")
  final = info_f[1].split("-")
  
  d_actual = date.today()
  d_checkpoint = date(d_actual.year, d_actual.month + 1, 1)
  d_final = date(int(final[0]), int(final[1]), int(final[2]))

  checkpoint = (d_checkpoint - d_actual).days
  milestone = (d_final - d_actual).days
  if int(checkpoint) < 5 or int(milestone) < 14:
    msg = discord.Embed(title="Contador de dias", description=f"Proximo checkpoint: {checkpoint}\nFinal del milestone: {milestone}", color=0xe74c3c)
  else:
    msg = discord.Embed(title="Contador de dias", description=f"Proximo checkpoint: {checkpoint}\nFinal del milestone: {milestone}", color=0x2ecc71)
  msg.set_author(name = user, icon_url=data[0]["image"]["link"], url=f"https://profile.intra.42.fr/users/{user}")
    
  await message.channel.send(embed=msg)

#Ping - Pinguea al bot y devuelve los ms
@bot.command(brief="Pinguea al bot y devuelve los ms")
async def ping(ctx):
  await ctx.send(f"Pong! ({int(bot.latency * 1000)}ms)")

#AskStaff - up2you
@bot.command(brief="up2you")
async def ask_staff(ctx):
  await ctx.send("Up to you")

#pfp - Enseña la foto de la intra del usuario especificado
@bot.command(brief="Enseña la foto de la intra del usuario especificado")
async def pfp(message, user = None):
  user = message.author.display_name if user is None else get_login(message, user)
  data = ic.get(f"https://api.intra.42.fr/v2/users?filter[login]={user}").json()
  await message.send(data[0]["image"]["link"])

#####TOKEN & RUN#####
token = os.environ['token']
bot.run(token)
