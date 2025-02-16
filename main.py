
#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import subprocess
import json

# Third-party libraries
try:
    import logging
    import discord
    from discord.ext import commands
    from colorama import init, Fore, Style
    # Initialize colorama for colored terminal output
    init(autoreset=True)
except Exception as e:
    print(e)


class ColorFormatter(logging.Formatter):
    """
    Custom logging formatter to add color to log messages based on severity.
    """
    COLORS = {
        'DEBUG': Fore.BLUE,
        'INFO': Fore.GREEN,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
        'CRITICAL': Fore.RED + Style.BRIGHT,
    }

    def format(self, record):
        log_color = self.COLORS.get(record.levelname, '')
        message = super().format(record)
        return f"{log_color}{message}{Style.RESET_ALL}"


def setup_logging():
    """
    Configure logging with colored output.
    """
    log_format = '[%(levelname)s] %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_format)
    for handler in logging.root.handlers:
        handler.setFormatter(ColorFormatter(log_format))


def load_config(config_path: str = 'config.json'):
    """
    Load configuration from the specified JSON file.
    """
    try:
        with open(config_path, 'r', encoding='utf-8') as config_file:
            return json.load(config_file)
    except Exception as e:
        logging.error(f"Error loading configuration: {e}")
        sys.exit(1)


def clear_screen():
    """
    Clear the terminal screen.
    """
    os.system('cls' if os.name == 'nt' else 'clear')


class SelfBot(commands.Bot):
    """
    A Discord selfbot that extends the commands.Bot class.
    """
    def __init__(self, command_prefix: str, token: str):
        super().__init__(command_prefix=command_prefix, self_bot=True)
        self.token = token
        self.remove_command("help")  # Remove default help command

    async def on_ready(self):
        """
        Called when the bot is ready.
        """
        logging.info("Ready! Awaiting your command... (Use !clear in DM or channel)")
        logging.info(f"Name: {self.user.name}")
        logging.info(f"ID: {self.user.id}")

    async def clear_messages(self, ctx: commands.Context, limit: int = None):
        """
        Clear messages sent by the bot in the current channel up to the specified limit.
        """
        passed = 0
        failed = 0
        async for msg in ctx.channel.history(limit=limit):
            if msg.author.id == self.user.id:
                try:
                    await msg.delete()
                    passed += 1
                except Exception as e:
                    logging.error(f"Failed to delete message: {e}")
                    failed += 1
        logging.info(f"Removed {passed} messages with {failed} failures.")

    def run_bot(self):
        """
        Log in to Discord and run the bot.
        """
        try:
            logging.info("Logging into Discord...")
            self.run(self.token, bot=False)
        except Exception as e:
            logging.error(f"Error logging into Discord: {e}")


def main():
    # Install requirements.
    if not os.getenv('requirements'):
        subprocess.Popen(['start', 'start.bat'], shell=True)
        sys.exit()

    """
    Main entry point of the script.
    """
    setup_logging()
    config = load_config()
    
    token = config.get("token")
    prefix = config.get("prefix")
    
    if not token or not prefix:
        logging.error("Token or prefix not found in configuration.")
        sys.exit(1)
    
    clear_screen()
    
    # Create the bot instance
    bot = SelfBot(command_prefix=prefix, token=token)
    
    @bot.command()
    async def clear(ctx: commands.Context, limit: int = None):
        """
        Command to clear messages sent by the bot in the current channel.
        Usage: !clear [limit]
        """
        await bot.clear_messages(ctx, limit)
    
    bot.run_bot()


if __name__ == "__main__":
    main()
