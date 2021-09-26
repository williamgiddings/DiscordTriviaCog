DiscordTriviaBot (Cog)
==========
   
A trivia game provider developed on the [discord.py](https://github.com/Rapptz/discord.py) Python API wrapper written for 3.5 and above*
**3.8 and above recommended though!*

**Recommended for use with my [Discord Bot Stub](https://github.com/williamgiddings/SuperMinimalDiscordBot)!**

Usage
----------

![alttext](https://i.imgur.com/BO9RFQR.jpg)

Requirements
----------
**Discord py**
```
# Linux/macOS
python3 -m pip install -U discord.py

# Windows
py -3 -m pip install -U discord.py
```

Installing
----------
1. Download this source file and place in the same directory as the [Discord Bot Stub](https://github.com/williamgiddings/SuperMinimalDiscordBot)
2. Import *Trivia* into the bot stub
    ```python
    # https://github.com/williamgiddings/SuperMinimalDiscordBot
    from discord.ext import commands
    import config
    import discord
    import Trivia
    ```
3. Add the *Trivia* Cog to the cog collection
    ```python
    cfg = config.load_config()
    bot = commands.Bot(command_prefix=cfg['prefix'], description=cfg['description'], intents=discord.Intents.all())
    COGS = [Trivia.Trivia] # drop your cogs here! check out my github for some cool ones or use my stub cog to make your own
    ```
4. **All set!**
**Make sure that you have filled in the proveded *config.toml* file with the correct information to enable use of the bot in a guild.**

Sources
----------

All questions come from the [Open Trivia Database](https://opentdb.com/). Many thanks to all the generous contributors who update the database with new questions daily!