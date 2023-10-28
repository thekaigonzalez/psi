"""Copyright 2019-2023 Kai D. Gonzalez"""

# contains simple math commands

from psilib import *
from psihelper import *
from discord import Message

async def add(message: Message, args: list):
    """add [num1] [num2] - add two numbers and ONLY two numbers"""
    num1 = psi_checkarg(args, 0)
    num2 = psi_checkarg(args, 1)

    if (num1 == PSI_INVALID or num2 == PSI_INVALID or type(num1) != int or type(num2) != int):
        await message.channel.send(f"i don't know how to add {num1} and {str(num2)}")
        return
    
    await message.channel.send(embed=psi_send_embed("Sum of two numbers", f"{num1} + {num2} = {num1 + num2}", Colour.green()))

class ECIMain(PsiECI):
    desc = """contains simple math commands"""
    cmds = {
        "add": add
    }
