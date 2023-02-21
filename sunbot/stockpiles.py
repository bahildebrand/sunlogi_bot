import discord
import json
from discord import app_commands
from typing import List
from sunbot.database import SunDB
from collections import defaultdict
import yaml
from yaml.representer import Representer
import logging

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

        self.depot_set = set(self.depot_list)

    def depotList(self):
        return self.depot_list

    def depotMap(self):
        return self.depot_map

    def checkDepot(self, depot: str) -> bool:
        return depot in self.depot_set


depots = Depots()


# Stupid work around for yaml indenting
class YamlDumper(yaml.Dumper):
    def increase_indent(self, flow=False, *args, **kwargs):
        return super().increase_indent(flow=flow, indentless=False)


async def depot_autocomplete(
    _: discord.Interaction,
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


async def update_listing_message(client: discord.Client, channel_id: int):
    msg_id = db.getMessageId(channel_id)
    logging.debug(
        f'Channel ID: {channel_id}, Message ID: {msg_id[0].message_id}')
    channel = client.get_channel(channel_id)
    stockpiles = db.getAllStockpiles(channel_id)
    formatted_stockpiles = format_stockpiles(stockpiles)
    if msg_id is None:
        msg = await channel.send(content=formatted_stockpiles)
        db.setMessageId(channel_id, msg.id)
    else:
        msg = await channel.fetch_message(msg_id[0].message_id)
        await msg.edit(content=formatted_stockpiles)


async def clear_listing_messages(client):
    msg_ids = db.getAllMessageIds()
    logging.debug(msg_ids)
    for id in msg_ids:
        logging.debug(f'Channel ID {id.channel_id}')
        await update_listing_message(client, id.channel_id)


@app_commands.command(description='Adds a stockpile')
@app_commands.autocomplete(depot=depot_autocomplete)
async def addstockpile(interaction: discord.Interaction, depot: str, name: str, code: int):
    if depots.checkDepot(depot):
        db.addStockPile(interaction.channel_id, name, depot, code)

        await update_listing_message(interaction.client, interaction.channel_id)
        await interaction.response.send_message(content=f'Created depot: {depot}', ephemeral=True)
    else:
        await interaction.response.send_message(content=f'Invalid depot: {depot}. Please select one from the list', ephemeral=True)


async def stockpile_autocomplete(
    interaction: discord.Interaction,
    current: str
) -> List[app_commands.Choice[str]]:
    stockpiles = db.getAllStockpiles(interaction.channel_id)

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
    stockpile_deleted = db.deleteStockpile(name, interaction.channel_id)

    if stockpile_deleted:
        await interaction.response.send_message(content=f'Deleted stockpile: {name}', ephemeral=True)
        await update_listing_message(interaction.client, interaction.channel_id)
    else:
        await interaction.response.send_message(content=f'Stockpile {name} not found. Please use a stockpile from the suggested list', ephemeral=True)


@app_commands.command(description='Delete all stockpiles associated with this channel.')
async def clearstockpiles(interaction: discord.Interaction):
    db.clearStockpiles()

    await update_listing_message(interaction.client, interaction.channel_id)
    await interaction.response.send_message(content='Deleted all stockpiles', ephemeral=True)


def add_stockpile_commands(client):
    client.tree.add_command(addstockpile)
    client.tree.add_command(deletestockpile)
    client.tree.add_command(clearstockpiles)
