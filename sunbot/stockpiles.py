import discord
import json
from discord import app_commands
from typing import List
from sunbot.database import SunDB
from collections import defaultdict
import yaml
from yaml.representer import Representer

db = SunDB()


class Depots:
    def __init__(self):
        depot_file = open("depots.json", "r")
        self.depots_full = json.load(depot_file)

        depot_lists = list(self.depots_full.values())
        self.depot_list = [
            depot for depot_list in depot_lists for depot in depot_list]

        self.depot_map = {}
        for region, depot_list in self.depots_full.items():
            for depot in depot_list:
                self.depot_map[depot] = region

    def depotList(self):
        return self.depot_list

    def depotMap(self):
        return self.depot_map


depots = Depots()


# Stupid work around for yaml indenting
class YamlDumper(yaml.Dumper):
    def increase_indent(self, flow=False, *args, **kwargs):
        return super().increase_indent(flow=flow, indentless=False)


async def depot_autocomplete(
    interaction: discord.Interaction,
    current: str
) -> List[app_commands.Choice[str]]:
    depots_filtered = list(
        filter(lambda depot: current.lower() in depot.lower(), depots.depotList()))
    return [
        app_commands.Choice(name=depot, value=depot)
        for depot in depots_filtered[:25]
    ]


def format_stockpiles(stockpiles):
    stockpile_dict = defaultdict(lambda: defaultdict(list))
    depot_map = depots.depotMap()
    for stockpile in stockpiles:
        stockpile = stockpile[0]
        region = depot_map[stockpile.depot]
        stockpile_dict[region][stockpile.depot].append(
            {stockpile.stockpile_name: stockpile.code})

    yaml.add_representer(defaultdict, Representer.represent_dict)
    yaml_dump = yaml.dump(
        stockpile_dict, Dumper=YamlDumper)
    return '```\n' + yaml_dump + '```'


async def update_listing_message(client, channel_id):
    msg_id = db.getMessageId(channel_id)
    print(msg_id)
    channel = client.get_channel(channel_id)
    stockpiles = db.getAllStockpiles()
    formatted_stockpiles = format_stockpiles(stockpiles)
    if msg_id is None:
        msg = await channel.send(content=formatted_stockpiles)
        db.setMessageId(channel_id, msg.id)
    else:
        msg = await channel.fetch_message(msg_id[0].message_id)
        await msg.edit(content=formatted_stockpiles)


@app_commands.command(description='Adds a stockpile')
@app_commands.autocomplete(depot=depot_autocomplete)
async def addstockpile(interaction: discord.Interaction, depot: str, name: str, code: int):
    db.addStockPile(name, depot, code)

    await interaction.response.send_message(content=f'depot: {depot} - name: {name} code: {code}', ephemeral=True)
    await update_listing_message(interaction.client, interaction.channel_id)


@app_commands.command(description='Lists all stockpiles')
async def liststockpiles(interaction: discord.Interaction):
    stockpiles = db.getAllStockpiles()
    await interaction.response.send_message(content=f'{repr(stockpiles)}', ephemeral=True)


async def stockpile_autocomplete(
    _interaction: discord.Interaction,
    current: str
) -> List[app_commands.Choice[str]]:
    stockpiles = db.getAllStockpiles()
    print(stockpiles)

    stockpiles_filtered = list(
        map(lambda stockpile: stockpile[0].stockpile_name, stockpiles))

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
