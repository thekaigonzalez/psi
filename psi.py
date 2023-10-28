"""Copyright 2019-2023 Kai D. Gonzalez"""

import discord

from psilib import *
from psihelper import *

import importlib
from os import listdir as ls
from os.path import basename

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print(f"We have logged in as {client.user}")


class LexState:
    # keep track of lexer state
    state: int
    # statement to lex
    stat: str
    # temporary buffer
    tmp: str
    # depth (for nested statements)
    depth: int

    def __init__(self, stat: str):
        self.state = 0
        self.stat = stat
        self.tmp = ""
        self.depth = -1

    def update_state(self, state: int):
        """
        Update the state of the lexer.
        """
        self.state = state

    def update_tmp(self, char: str):
        """
        Update the temporary buffer.
        """
        self.tmp += char
    
    def get_tmp(self):
        """
        Get the temporary buffer.
        """
        return self.tmp

    def get_state(self):
        """
        Get the state of the lexer.
        """
        return self.state

    def clear_tmp(self):
        """
        Clear the temporary buffer.
        """
        self.tmp = ""

    def update_depth(self, char: str):
        """
        Update the depth of the lexer.
        """

        if (char == "("):
            self.depth += 1
        elif (char == ")"):
            self.depth -= 1

    def state_against(self, state: int):
        """
        Check if the state of the lexer matches the given state.
        """
        return self.state == state
    
    def nposisstr(self):
        """
        Check if the state of the lexer is not a string.
        """
        return self.state != STATE_STRING
            

### we are NOT using regex. i have a religious war with regex.
STATE_STRING = 0    # string " ... "
STATE_LIST   = 1    # list ( ... )
STATE_INIT   = 2    # initial state. why it's down here idk
STATE_VALUE  = 3    # value [key]:...

### tokenz
TOKEN_STRING = '"'
TOKEN_LIST   = '('
TOKEN_RLIST  = ')'
TOKEN_KEY    = ':'

### default values
GLOBAL_PREFIX_DEFAULT = "$"

class PsiGlobal:
    prefix = GLOBAL_PREFIX_DEFAULT

class PSI_ERROR:
    """
    simple psi brace matching error
    """
    pass

class PSI_ERROR_STRING:
    """
    simple psi string matching error
    """
    pass

class PSI_ERROR_LIST:
    """
    simple psi list matching error
    """
    pass

class PSI_ERROR_KEYVALUE:
    """
    simple psi value missing error
    """
    pass

def generate_type_based_on_argument(arg: str):
    arg = arg.strip()
    """
    simple function to generate a type based on the argument
    if the argument seems like its a number, turn it into one
    if the argument seems like its a boolean, turn it into one
    otherwise we shouldn't process it?
    """
    if (arg.isnumeric()):
        return int(arg)
    elif (arg.lower() == "true" or arg.lower() == "false"):
        return bool(arg)
    elif (arg.lower() == "yes" or arg.lower() == "no"):
        return True if arg.lower() == "yes" else False
    elif (arg.startswith("(")):
        return parse_args(arg[1:-1], optional_separator=",")
    else:
        return arg

def parse_args(arg: str, optional_separator=" "):
    """
    simple function to generate an array that handles argument strings
    supports the following types of arguments:

        * strings, numbers and booleans. "yes" or "no" are parsed as booleans as
          well as true and false.

        * lists, so if you run the command: "$foo (a, 2, true)" the arguments
          will have a list of ["a", 2, True]

        * very simplistic key-value pairs, so if you have the command: "$foo
          a:this" then argument 0 will be ["a": "this"]

    NOTE: strings are a bit buggy.
    NOTE: also generates errors but will not print them directly to allow them
    to be handled by the caller.
    """

    TOKEN_WHITESPACE = optional_separator
    
    lexer = LexState(arg) # create a lexer

    lexer.update_state(STATE_INIT)

    previous_state = STATE_INIT
    tmpkvn = "" # the name of the keyvalue pair
    
    new = [] # array of arguments

    i = 0

    for token in arg:
        lexer.update_depth(token)

        if (token == TOKEN_WHITESPACE 
            and not lexer.state_against(STATE_LIST) 
            and lexer.nposisstr() 
            and lexer.state_against(STATE_INIT)): # there's a space and it isnt in a string
            
            lexer.tmp = lexer.tmp.strip()

            new.append(generate_type_based_on_argument(lexer.get_tmp()))
            
            lexer.clear_tmp()

        elif (token == TOKEN_WHITESPACE and lexer.state_against(STATE_VALUE)):
            lexer.tmp = lexer.tmp.strip()

            tmpkvn = tmpkvn.strip()
            new.append({tmpkvn:  generate_type_based_on_argument(lexer.get_tmp())})

            lexer.clear_tmp()
            tmpkvn = ""
        
        elif (token == TOKEN_STRING and not lexer.state_against(STATE_STRING)): # if its a string
            previous_state = lexer.state
            lexer.update_state(STATE_STRING)

        elif (token == TOKEN_STRING and lexer.state_against(STATE_STRING)):
            lexer.update_state(previous_state)
            
        
        elif (token == TOKEN_LIST and lexer.nposisstr() and lexer.depth == 0): 
            lexer.update_state(STATE_LIST)
            lexer.update_tmp(token)
        
        
        elif (token == TOKEN_RLIST and lexer.nposisstr() and lexer.depth == 0):
            lexer.update_state(STATE_INIT)
            lexer.depth = -1
            lexer.update_tmp(token)
        

        elif (token == TOKEN_KEY and lexer.nposisstr()):
            lexer.update_state(STATE_VALUE)
            tmpkvn = lexer.get_tmp()
            lexer.clear_tmp()

        else:
            lexer.update_tmp(token)
        i += 1

    if (lexer.depth >= 0):
        return PSI_ERROR
    
    if (lexer.state_against(STATE_STRING)):
        return PSI_ERROR_STRING
    
    # if (lexer.state_against(STATE_LIST)):
    #     return PSI_ERROR_LIST
    
    if (lexer.state_against(STATE_VALUE) and lexer.get_tmp().strip() == ""):
        return PSI_ERROR_KEYVALUE
    
    if (lexer.get_tmp().strip() != "" and not lexer.state_against(STATE_VALUE)):
        new.append(generate_type_based_on_argument(lexer.get_tmp()))

    elif (lexer.get_tmp().strip() != "" and lexer.state_against(STATE_VALUE)):
        tmpkvn = tmpkvn.strip();
        new.append({tmpkvn:  generate_type_based_on_argument(lexer.get_tmp())})

    for i in new:
        if (i is PSI_ERROR):
            return PSI_ERROR

    return new

def get_error(arg: int):
    if (arg == PSI_ERROR):
        return ("psi: '(' or ')' were never closed. are you missing a ')'?")
    elif (arg == PSI_ERROR_STRING):
        return ("psi: string was never completed. are you missing a '\"'?")

    elif (arg == PSI_ERROR_LIST):
        return ("psi: list was never closed. are you missing a ')'?")
    
    elif (arg == PSI_ERROR_KEYVALUE):
        return ("psi: key-value pair was never completed. are you missing a value?")

"""
NOTE: copy this py-cord embed example
@bot.command()
async def hello(ctx):
    embed = discord.Embed(
        title="My Amazing Embed",
        description="Embeds are super easy, barely an inconvenience.",
        color=discord.Colour.blurple(), # Pycord provides a class with default colors you can choose from
    )
    embed.add_field(name="A Normal Field", value="A really nice field with some information. **The description as well as the fields support markdown!**")

    embed.add_field(name="Inline Field 1", value="Inline Field 1", inline=True)
    embed.add_field(name="Inline Field 2", value="Inline Field 2", inline=True)
    embed.add_field(name="Inline Field 3", value="Inline Field 3", inline=True)
 
    embed.set_footer(text="Footer! No markdown here.") # footers can have icons too
    embed.set_author(name="Pycord Team", icon_url="https://example.com/link-to-my-image.png")
    embed.set_thumbnail(url="https://example.com/link-to-my-thumbnail.png")
    embed.set_image(url="https://example.com/link-to-my-banner.png")
 
    await ctx.respond("Hello! Here's a cool embed.", embed=embed) # Send the embed with some text


"""

def kevinshtein_distence(a: str, b: str):
    """
    a simpler levenshtein distance calculator
    it technically isn't even a levenshtein distance but it still calculates the
    differences between strings.
    """

    distance = 0


    for i in range(len(a)):
        if (i >= len(b)):
            distance += 1
            continue
        if (a[i] != b[i]):
            distance += 1

    return distance

@client.event
async def on_message(message: discord.Message):
    if message.author == client.user:
        return
    
    if (not message.content.startswith("$")):
        return

    _arg = parse_args(message.content)
    

    _arg[0] = _arg[0][1:] # remove the prefix

    ext = ls("./eci")

    if (_arg[0] == "help"):
        if (len(_arg) < 2):
            emb = discord.Embed(
                title="psi help!",
                description=f"```note from developers: to use help efficiently, try typing in the module names listed here! for example, you can get help on commands like 'hello' in the 'simple' module.\nthe command would be: $help simple\n\nthere is a list of modules below this code block.\n```\n",
                color=discord.Colour.yellow(),
            )

            for i in ext:
                if (not i.endswith(".py")): continue
                i = i[0:i.find(".")] # remove the .py
                emb.add_field(name=i, value="", inline=False)

            await message.channel.send(embed=emb)
            return
        module_name = _arg[1]

        if (type(module_name) != str):
            emb = discord.Embed(
                title="psi error when trying to get your help!",
                description=f"module name must be a string!",
                color=discord.Colour.red(),
            )
            await message.channel.send(embed=emb)
            return

        if (not (module_name + ".py" in ext)):
            emb = discord.Embed(
                title="psi error when trying to get your help!",
                description=f"module {module_name} not found!",
                color=discord.Colour.red(),
            )
            await message.channel.send(embed=emb)
            return
        for i in ext:
                if (not i.endswith(".py")): continue
                i = i[0:i.find(".")] # remove the .py

                if (module_name == i):
                    mod = importlib.import_module("eci." + i)

                    ECIMain = mod.ECIMain

                    # ECIMain contains fields cmd and desc, using simple python
                    # methods we can get the docstring fields from the functions
                    # in cmds
                    emb = discord.Embed(
                        title="Help for psi module " + i,
                        description=ECIMain.desc,
                        color=discord.Colour.yellow(),
                    )

                    for j in ECIMain.cmds:
                        emb.add_field(name=j, value=ECIMain.cmds[j].__doc__, inline=False)

                    await message.channel.send(embed=emb)
                    
    else:
        Almost = 2
        found = False
        couldbe = ""

        for i in ext:
            if (not i.endswith(".py")): continue
            i = i[0:i.find(".")] # remove the .py

            mod = importlib.import_module("eci." + i)

            if (_arg[0] in mod.ECIMain.cmds):
                found = True
                await mod.ECIMain.cmds[_arg[0]](message, _arg[1:])
                break

            for cm in mod.ECIMain.cmds:
                if (kevinshtein_distence(_arg[0], cm) < 5):
                    found = Almost
                    couldbe = cm

        if (not found or found == Almost):
            helpstr = "" # see if there's any sort of recommendations for the user

            for i in ext:
                i = i[0:i.find(".")] # remove the .py

                if (i == _arg[0]):
                    helpstr = "the name " + i + " is a module name,\ndid you mean '$help " + i + "'?"

            if (found == Almost):
                helpstr = "did you mean '" + couldbe + "'?"

            emb = discord.Embed(
                title="psi could not find your command!",
                description=f"```basic\ncommand {_arg[0]} not found!\n{helpstr}```",
                color=discord.Colour.red(),
            )

            await message.channel.send(embed=emb)
            
            return

    if (type(_arg) != list): # error
        n = get_error(_arg) # get the error
        emb = discord.Embed(
            title="psi error!",
            description=f"{n}\n```basic\n{message.content}```",
            color=discord.Colour.red(),
        )
        await message.channel.send(embed=emb)
        return


client.run("MTA5NjYwNjAzNDM4ODMzNjY0MA.GAIG_T.B13li6oXLd_L9-1s3LKOtQ2hQnHu-Cd0M-Ko-g")
