import discord
from discord import app_commands
import os

from sunbot.delivery import add_commands
from sunbot.stockpiles import add_stockpile_commands

MY_GUILD = discord.Object(id=610626278214860800)


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

    add_commands(client)
    add_stockpile_commands(client)

    discord_token = os.environ.get("DISCORD_TOKEN")
    print(discord_token)
    client.run(discord_token)
