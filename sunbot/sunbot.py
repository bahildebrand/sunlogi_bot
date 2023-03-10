import discord
import logging
import os
from discord import app_commands
from sunbot.database import SunDB
from sunbot.stockpiles import add_stockpile_commands


class MyClient(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.default())
        self.db = SunDB()
        self.tree = app_commands.CommandTree(self)

    async def on_ready(self):
        logging.info("Discord client connected.")

    async def setup_hook(self):
        # Copies global commands to guild, only needed in test environments
        guild_id = os.environ.get("TEST_GUILD")
        await self.db.init_models()
        if guild_id is not None:
            guild_id = discord.Object(id=guild_id)

            self.tree.copy_global_to(guild=guild_id)
            await self.tree.sync(guild=guild_id)
        else:
            await self.tree.sync()


def main():
    format_str = '[%(asctime)s] [%(filename)s:%(lineno)d] [%(levelname)s]: %(message)s'
    logging.basicConfig(
        level="INFO", format=format_str, datefmt='%Y-%m-%d:%H:%M:%S')
    client = MyClient()

    # add_commands(client)
    add_stockpile_commands(client)

    discord_token = os.environ.get("DISCORD_TOKEN")
    print(discord_token)
    client.run(discord_token, log_handler=None)
