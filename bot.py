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
import threading
from collections import Counter
from discord import app_commands
import time

###Discord config####
intents = discord.Intents.all()
intents.members = True  
intents.message_content = True
bot = discord.Client(intents=intents)
tree = app_commands.CommandTree(bot)
fav = ""

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

def favorite_place(user):
    global fav
    data = ic.get(f"https://api.intra.42.fr/v2/users/{user}/locations").json()
    fav = []
    for i in data:
        fav.append(i["host"])
    fav = Counter(fav)
    fav = fav.most_common(1)

#######EVENTS########
@bot.event
async def on_ready():
    await tree.sync(guild=discord.Object(id=1019664758099673191))
    print("Bot preparado para dar segfaults (imposible en python por la falta de estilo)")
    await bot.change_presence(activity=discord.Game(name="Dar segfaults"))


######COMMANDS#######
#Bigmom - enseña la informacion relevante de bigmom del usuario
@tree.command(name = "bigmom", description = "Muestra la informacion de bigmom del usuario", guild=discord.Object(id=1019664758099673191))
async def bigmom(interaction: discord.Interaction, user: str):
  data = ic.get(f"https://api.intra.42.fr/v2/users?filter[login]={user}").json()
  
  try:
    bigmom_data = get_soup(user)
  except IndexError:
    await interaction.response.send_message("User no encontrado. Has escrito bien el nombre?")
    return None
    
  msg = discord.Embed(title="Big Mom", color=0xe74c3c)

  msg.add_field(name="Vidas", value=bigmom_data["vidas"], inline=False)
  msg.add_field(name="Inicio Milestone", value=bigmom_data["inicio"], inline=False)
  msg.add_field(name="Final Milestone", value=bigmom_data["final"], inline=False)
  msg.set_author(name= user, icon_url=data[0]["image"]["link"], url=f"https://profile.intra.42.fr/users/{user}")
  
  await interaction.response.send_message(embed=msg)

#Info - Enseña información sobre el usuario especificado
@tree.command(name = "info", description = "Muestra la informacion del usuario", guild=discord.Object(id=1019664758099673191))
async def info(interaction: discord.Interaction, user: str):
  try:
    info = ic.get(f"https://api.intra.42.fr/v2/users?filter[login]={user}")
  except Exception:
    await interaction.response.send_message("User no encontrado. Has escrito bien el nombre?")
    return

  if info.status_code == 200:
    try:
        x1 = threading.Thread(target=favorite_place, args=[user])
        x1.start()
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
        await interaction.response.send_message("User no encontrado o no tiene perfil. Has escrito bien el nombre?")
    x1.join()
    msg = discord.Embed(title="Info", description=f"Puntos: {aaa}\nMonedas: {mon}₳\nEsta en: {loc}\nCoalicion: {coal}\nLugar favorito: {fav[0][0]}", color=int(col[1: ].lower(), 16))
    msg.set_author(name = user, icon_url=data[0]["image"]["link"], url=f"https://profile.intra.42.fr/users/{user}")
    
    await interaction.response.send_message(embed=msg)


#Days - Enseña los dias restantes para el proximo checkpoint y la milestone actual del usuario especificado
@tree.command(name = "days", description = "Muestra los dias que le faltan al usuario para completar el checkpoint y el milestone", guild=discord.Object(id=1019664758099673191))
async def days(interaction: discord.Interaction, user: str):
  if random.randint(1, 100) <= 5:
    await interaction.response.send_message("Aprende a contar anda, que tienes la info en !bigmom")
    return

  data = ic.get(f"https://api.intra.42.fr/v2/users?filter[login]={user}").json()

  try:
    bigmom_data = get_soup(user)
  except IndexError:
    await interaction.response.send_message("User no encontrado. Has escrito bien el nombre?")
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
    
  await interaction.response.send_message(embed=msg)

#Ping - Pinguea al bot y devuelve los ms
@tree.command(name = "ping", description = "Pinguea al bot y devuelve los ms", guild=discord.Object(id=1019664758099673191))
async def ping(interaction: discord.Interaction):
  await interaction.response.send_message(f"Pong! ({int(bot.latency * 1000)}ms)")

#AskStaff - up2you
@tree.command(name = "ask_staff", description = "La respuesta a todos tus problemas", guild=discord.Object(id=1019664758099673191))
async def ask_staff(interaction: discord.Interaction):
  await interaction.response.send_message("Up to you")

#pfp - Enseña la foto de la intra del usuario especificado
@tree.command(name = "pfp", description = "Enseña la foto de la intra del usuario especificado", guild=discord.Object(id=1019664758099673191))
async def pfp(interaction: discord.Interaction, user: str):
  data = ic.get(f"https://api.intra.42.fr/v2/users?filter[login]={user}").json()
  await interaction.response.send_message(data[0]["image"]["link"])

#log - Te dice cuanto tiempo ha durado tu ultima estancia en 42
@tree.command(name = "log", description = "Te dice cuanto tiempo ha durado tu ultima estancia en 42", guild=discord.Object(id=1019664758099673191))
async def log(interaction: discord.Interaction, user: str):
  data = ic.get(f"https://api.intra.42.fr/v2/users/{user}/locations").json()
  beg = []
  end = []
  d = 0
  for i in data:
    a = time.strptime(i["begin_at"][ : -5], "%Y-%m-%dT%H:%M:%S")
    b = time.strptime(i["end_at"][ : -5], "%Y-%m-%dT%H:%M:%S")
    if a.tm_mday > d:
      d = a.tm_mday
    if a.tm_mday < d:
      break
    beg.append(a)
    end.append(b)
  n = -1
  hh = []
  nn = []
  for i in beg:
    n += 1
    h = end[n].tm_hour - i.tm_hour
    m = end[n].tm_min - i.tm_min
    if m < 0:
      h -= 1
      m = 60 + m
    hh.append(h)
    nn.append(m)
  h = sum(hh)
  m = sum(nn)
  if m > 60:
    h += 1
    m = m - 60
  msg = discord.Embed(title="Ultima sesion", description=f"La ultima sesión ha sido de {h}h y {m}m", color=0x2ecc71)
  msg.set_author(name = user, icon_url=data[0]["user"]["image"]["link"], url=f"https://profile.intra.42.fr/users/{user}")
  await interaction.response.send_message(embed=msg)

#say - Oktobot manda el mensaje que le pidas
@tree.command(name = "say", description = "Di algo con el bot :3", guild=discord.Object(id=1019664758099673191))
@commands.has_role("/Oktobot Devs/")
async def say(interaction: discord.Interaction, mensaje: str):
      await interaction.response.send_message(f"{mensaje}")
#search - Te busca los logins a partir del nombre del alumno (solo de 42 barcelona)    
@tree.command(name = "search", description = "Te busca los logins a partir del nombre del alumno (solo de 42 barcelona)", guild=discord.Object(id=1019664758099673191))
async def search(interaction: discord.Interaction, nombre: str):
  mm = ""
  try:
    info = ic.get(f"https://api.intra.42.fr/v2/campus/46/users?filter[first_name]={user}")
  except Exception:
    await interaction.response.send_message("User no encontrado. Has escrito bien el nombre?")
    return
  if info.status_code == 200:
        data = info.json()
  for i in data:
    i = i["login"]
    mm = mm + f"\n{i}"
  msg = discord.Embed(title=f"Logins con {user}", description=mm)
  await interaction.response.send_message(embed=msg)


#####TOKEN & RUN#####
token = os.environ['token']
bot.run(token)
