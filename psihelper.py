"""Copyright 2019-2023 Kai D. Gonzalez"""

# helper functions

from discord import Embed, Colour, Message

class PSI_INVALID:
    pass

def psi_generate_embed_with_code(code: str, desc: str, color: Colour = Colour.green()):
    emb = Embed(title="psi", description=desc + "\n```python\n" + code + "\n```", color=color)

    return emb

def psi_send_embed(title: str, message: str, color: Colour = Colour.orange()):
    emb = Embed(title=title, description=f"```basic\n{message}\n```", color=color)

    return emb

def psi_checkarg(arg: list, pos: int):
    if (len(arg) <= pos):
        return PSI_INVALID

    return arg[pos]

def psi_send_error(errorname: str, message: str):
    emb = psi_send_embed(errorname, message, Colour.red())

    return emb
