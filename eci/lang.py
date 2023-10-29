"""Copyright 2019-2023 Kai D. Gonzalez"""

# commands for the programming language builtin to psi

from psilib import *
from psihelper import *
from discord import Message

async def stringify(message: Message, args: list):
    """stringify [value] - convert a value to a string"""
    value = args

    if (value == PSI_INVALID):
        await message.channel.send(f"i don't know how to stringify {value}")
        return
    
    embe = psi_send_embed("Stringified value", f"{str(value)}", Colour.orange())

    await message.channel.send(embed=embe)
    


class ECIMain(PsiECI):
    desc = """builtin AST commands"""
    cmds = {
        "stringify": stringify
    }
