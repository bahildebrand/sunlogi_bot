from enum import Enum
from typing import List, Literal
import discord
import json
from discord import app_commands
import os

MY_GUILD = discord.Object(id=610626278214860800)  # replace with your guild id


class MyClient(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.default())
        self.tree = app_commands.CommandTree(self)

    async def on_ready(self):
        print(f'Logged on as {self.user}!')

    async def on_message(self, message):
        print(f'Message from {message.author}: {message.content}')

    async def setup_hook(self):
        # This copies the global commands over to your guild.
        self.tree.copy_global_to(guild=MY_GUILD)
        await self.tree.sync(guild=MY_GUILD)


def main():
    client = MyClient()

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

    @ client.tree.command()
    @ app_commands.autocomplete(depot=depot_autocomplete, item=item_autocomplete)
    async def request(interaction: discord.Interaction, depot: str, item: str, quantity: int):
        await interaction.response.send_message(f'depot: {depot} item: {item} quantity: {quantity}')

    discord_token = os.environ.get("DISCORD_TOKEN")

    client.run(discord_token)
