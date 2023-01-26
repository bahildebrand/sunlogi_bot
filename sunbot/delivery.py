import discord
import json
from discord import app_commands
from typing import List


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


async def item_autocomplete(
    interaction: discord.Interaction,
    current: str
) -> List[app_commands.Choice[str]]:
    item_file = open("item_list.json", "r")
    item_list = json.load(item_file)

    filtered_item_list = list(
        filter(lambda item: current.lower() in item.lower(), item_list))

    return [
        app_commands.Choice(name=item, value=item)
        for item in filtered_item_list[:25]
    ]


@app_commands.command(description='Requests a delivery')
@app_commands.autocomplete(depot=depot_autocomplete, item=item_autocomplete)
async def request(interaction: discord.Interaction, depot: str, item: str, quantity: int):
    await interaction.response.send_message(f'depot: {depot} item: {item} quantity: {quantity}')


def add_commands(client):
    client.tree.add_command(request)
