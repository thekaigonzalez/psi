"""Copyright 2019-2023 Kai D. Gonzalez"""

# contains simple commands like "hello", "bye"

from psilib import *
from psihelper import *
from discord import Message

async def hello(message: Message, args: list):
    """hello [optional: name] - say hello to someone, or yourself"""
    name = psi_checkarg(args, 0)

    if (name == PSI_INVALID):
        await message.channel.send(f"Hello, {message.author.display_name}!")
        return
    
    await message.channel.send(f"Hello, {name}!")

async def bye(message: Message, args: list):
    """bye [ ... ] - say goodbye"""
    await message.channel.send(f"Bye, {message.author.display_name}!")

class ECIMain(PsiECI):
    desc = """contains simple commands like \"Hello\" and \"goodbye\"!"""
    cmds = {
        "hello": hello,
        "bye": bye
    }
