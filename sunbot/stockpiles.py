import discord
import json
from discord import app_commands
from typing import List
from sunbot.database import SunDB

db = SunDB()


async def depot_autocomplete(
    interaction: discord.Interaction,
    current: str
) -> List[app_commands.Choice[str]]:
    depot_file = open("depots.json", "r")
    depots = json.load(depot_file)
    depots = list(depots.values())
    depots = [depot for depotList in depots for depot in depotList]

    depots_filtered = list(
        filter(lambda depot: current.lower() in depot.lower(), depots))
    return [
        app_commands.Choice(name=depot, value=depot)
        for depot in depots_filtered[:25]
    ]


async def update_listing_message(client, channel_id):
    msg_id = db.getMessageId(channel_id)
    print(msg_id)
    channel = client.get_channel(channel_id)
    stockpiles = db.getAllStockpiles()
    if msg_id is None:
        print("Message not found")
        msg = await channel.send(content=stockpiles)
        db.setMessageId(channel_id, msg.id)
    else:
        print("Message found")
        msg = await channel.fetch_message(msg_id[0])
        await msg.edit(content=stockpiles)


@app_commands.command(description='Adds a stockpile')
@app_commands.autocomplete(depot=depot_autocomplete)
async def addstockpile(interaction: discord.Interaction, depot: str, name: str, code: int):
    db.addStockPile(name, depot, code)

    await interaction.response.send_message(content=f'depot: {depot} - name: {name} code: {code}', ephemeral=True)
    await update_listing_message(interaction.client, interaction.channel_id)


@app_commands.command(description='Lists all stockpiles')
async def liststockpiles(interaction: discord.Interaction):
    stockpiles = db.getAllStockpiles()
    await interaction.response.send_message(content=f'{stockpiles}', ephemeral=True)


async def stockpile_autocomplete(
    interaction: discord.Interaction,
    current: str
) -> List[app_commands.Choice[str]]:
    stockpiles = db.getAllStockpiles()

    stockpiles_filtered = list(
        map(lambda stockpile: stockpile[0], stockpiles))

    stockpiles_filtered = list(
        filter(lambda stockpile: current.lower()
               in stockpile.lower(), stockpiles_filtered)
    )
    return [
        app_commands.Choice(name=stockpile, value=stockpile)
        for stockpile in stockpiles_filtered[:25]
    ]


@app_commands.command(description='Delete a stockpile')
@app_commands.autocomplete(name=stockpile_autocomplete)
async def deletestockpile(interaction: discord.Interaction, name: str):
    db.deleteStockpile(name)

    await interaction.response.send_message(content=f'Deleted stockpile: {name}', ephemeral=True)

    await update_listing_message(interaction.client, interaction.channel_id)



def add_stockpile_commands(client):
    client.tree.add_command(addstockpile)
    client.tree.add_command(liststockpiles)
    client.tree.add_command(deletestockpile)
