import discord
from discord.ext import commands
import json
import os
import re
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents = intents)

# Used for thumbnails

char_ids = {
    "01": "akira",
    "02": "pai", 
    "03": "lau", 
    "04": "wolf", 
    "05": "jeffry", 
    "06": "kage", 
    "07": "sarah", 
    "08": "jacky",
    "09": "shun",
    "10": "lion", 
    "11": "aoi", 
    "12": "lei", 
    "13": "vanessa",
    "14": "brad",
    "15": "goh", 
    "16": "eileen",
    "17": "blaze",
    "18": "taka",
    "19": "jean",
    "20": "dural",
}

id_char_lookup = {i: j for j, i in char_ids.items()}

# Below includes stuff to fix user inputs

written_input_fixes = {
    "hcf": "41236",
    "hcf+": "41236",
    "hcb": "63214",
    "hcb+": "63214",
    "qcf": "236",
    "qcf+": "236",
    "qcb": "214",
    "qcb+": "214",
    "f": "6",
    "df": "3",
    "d": "2",
    "db": "1",
    "b" : "4",
    "ub": "7",
    "u": "8",
    "uf": "9",
}

numerical_input_fixes = {
    "426": "41236",
    "624": "63214",
}

def normalize_written(command):
    command = command.lower()
    for text, num in written_input_fixes.items():
        command = command.replace(text, num)

    return command

def normalize_numerical(command):
    numbered = "".join(dig for dig in command if dig.isdigit())

    if numbered in numerical_input_fixes:
        fix = numerical_input_fixes[numbered]
        return command.replace(numbered, fix)

    return command

# Adjusts command input for crouch dash. In VF, ws inputs can be done with crouch dash (33). 
def normalize_crouchdash(command):
    # If already in proper ws format (e.g. 2_6P+K), keep as is
    if "_" in command:
        return command

    m = re.match(r"33([12346789]?)(.*)", command)
    if not m:
        return command

    post_cd = m.group(1)
    remainder = m.group(2)

    # If input is simple 33X, sets post cd direction to 3 so it'll simply to 2_3X.
    if (post_cd == ""):
        post_cd = "3";

    return f"2_{post_cd}{remainder}"

def final_normalize(command):
    command = command.strip()
    command = normalize_written(command)
    command = normalize_numerical(command)
    command = normalize_crouchdash(command)
    command = command.upper()
    return command

# Below is loading the frame data from the jsons 

FD = {}

def load_frame_data():
    for filename in os.listdir("moves"):
        if filename.endswith(".json"):
            character = filename.replace(".json", "")
            with open(f"moves/{filename}", "r") as d:
                FD[character] = json.load(d)

load_frame_data()

# Creates the discord embed

def move_box(character, move):
    embed = discord.Embed(
        title = f"{move['name']}",
        description = f"{move['command']}",
        color = discord.Color.blue()
    )

    thumbnail_id = id_char_lookup.get(character, None)
    embed.set_thumbnail(url=f"https://virtua-fighter.com/revo/en/character/images/chara{thumbnail_id}.png")
    embed.add_field(name="Level", value=f"{move['level']}", inline = True)
    embed.add_field(name="Damage", value=f"{move['damage']}", inline = True)
    embed.add_field(name="Startup", value=f"{move['startup']}", inline = True)
    embed.add_field(name="Block", value=f"{move['onGuard']}", inline = True)
    embed.add_field(name="Hit", value=f"{move['onHit']}", inline = True)
    embed.add_field(name="Counter Hit", value=f"{move['onCounterHit']}", inline = True)
    embed.add_field(name="Evade", value=move.get("evade", "-"), inline = True)
    if move["notes"]:
        embed.add_field(name="Notes", value=move["notes"], inline = False)

    return embed

# The bot command.

@bot.command()
async def fd(ctx, character: str, *, command: str):
    character = character.lower()
    if character not in FD:
        await ctx.send("Unknown character!")
        return

    command_true = final_normalize(command)

    for move in FD[character]:
        if move["command"] == command_true:
            embed = move_box(character, move)
            await ctx.send(embed=embed)
            return

    await ctx.send(f"No such move {command_true} found for {character}")

bot.run(TOKEN)