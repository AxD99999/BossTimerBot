# Import necessary libraries
import discord
from discord.ext import commands
import asyncio
import time

from botTokens import LiveToken as Token

# Set up the bot's intents (events it can respond to)
intents = discord.Intents.default()
intents.message_content = True

# Initialize the bot with a command prefix and the defined intents
bot = commands.Bot(command_prefix='!', intents=intents)

# Define the durations for various edl timers
edl_timers_perm = {
    '155': 3810,
    '160': 4110,
    '165': 4410,
    '170': 4710,
    '180': 5400,
    '185': 4800,
    '190': 5400,
    '195': 6000,
    '200': 6510,
    '205': 6900,
    '210': 7500,
    '215': 8100,
    'prot': 64800,
    # 'test': 30
}
edl_timers = edl_timers_perm.copy()

# Define the durations for various raid timers
raid_timers_perm = {
    'dino': 223200,  # 62 hours
    'gele': 216000,  # 60 hours
    'bt': 223200,  # 62 hours
    'mord': 129600,  # 36 hours
    'hrung': 136800,  # 38 hours
    'necro': 136800,  # 38 hours
    'aggy': 129600, # 36 hours
    # 'test': 30
}
raid_timers = raid_timers_perm.copy()

# Set role id
role_id = {
    'prot': 1222364156846669896,
    'bt': 1222361960864153600,
    'gele': 1222362251923820636,
    'dino': 1222362334702342197,
    'aggy': 1222547945467940864,
    #'test': 1222422903551950879

}

# Initialize a dictionary for event timers
event_timers = {}
event_timers_window = {}
event_flag = {}

# Initialize a dictionary to keep track of running timers
running_timers = {}

# Event handler for when the bot is ready
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}!')

# Event handler for when a message is received
@bot.event
async def on_message(message):
    #print(message)
    try:
        if message.channel.name == '⏰timer': # Check if the message is in the '⏰timer' channel
            # Split the message content into words
            content = message.content.lower().split()
            if content:
                # Check if the first word is a key in edl_timers
                if content[0] in edl_timers:
                    # Get the duration for the timer
                    duration = edl_timers[content[0]]
                    # If there's a second word and it ends with 'm', adjust the duration
                    if len(content) > 1 and content[1].endswith('m'):
                        minutes = int(content[1][:-1])
                        duration -= minutes * 60
                    # React to the message with a '⏰' emoji
                    await message.add_reaction('⏰')
                    # Calculate the expiry time for the timer
                    expiry_time = int(time.time() + duration)
                    # Send a message to the channel indicating the timer has started
                    await message.channel.send(f"A timer for **{content[0]}** has started. It will be due in <t:{expiry_time}:f>(<t:{expiry_time}:R>).")
                    # Start the timer
                    await start_edl_timers(message, content[0], duration)
                # Check if the first word is a key in raid_timers
                elif content[0] in raid_timers:
                    # Get the duration for the raid timer
                    duration = raid_timers[content[0]]
                    # If there's a second word and it ends with 'm', adjust the duration
                    if len(content) > 1 and content[1].endswith('m'):
                        minutes = int(content[1][:-1])
                        duration -= minutes * 60
                    # React to the message with a '⏰' emoji
                    await message.add_reaction('⏰')
                    # Calculate the expiry time for the raid timer
                    expiry_time = int(time.time() + duration)
                    # Send a message to the channel indicating the raid timer has started
                    if content[0] == 'gele' or content[0] == 'aggy' or content[0] == 'mord':
                        additional = 2*60*60
                    # elif content[0] == 'test':
                    #     additional = 10
                    else:
                        additional = 3*60*60 
                    if duration>raid_timers[content[0]]/2:
                        await message.channel.send(f"A raid timer for **{content[0]}** has started. Window will be open in <t:{int(expiry_time - raid_timers[content[0]]/2 + additional )}:f>(<t:{int(expiry_time - raid_timers[content[0]]/2 + additional)}:R>).")
                    else:
                        await message.channel.send(f"A raid timer for **{content[0]}** has started. Window is open and will close in <t:{int(expiry_time)}:f>(<t:{int(expiry_time)}:R>).")
                    # Start the raid timer
                    await start_raid_timer(message, content[0], duration)
                # Check if the first word is 'soon'
                elif content[0] == 'soon':
                    # React to the message with a '⏰' emoji
                    await message.add_reaction('⏰')
                    # Display the running timers
                    await display_running_timers(message.channel)
                # Check if the first word is 'reset'
                elif content[0] == 'reset' and len(content)==1:
                    # Clear the running timers
                    await clear_all()
                    # React to the message with a '⏰' emoji
                    await message.add_reaction('⏰')
                    # Send a message to the channel indicating all timers have been reset
                    await message.channel.send("All timers have been reset.")
                elif content[0] == 'reset':
                    await message.add_reaction('⏰')
                    await message.channel.send("Only type 'reset' to reset all timers. If you are trying to delete a certain timer use 'Delete'. Example: To delete 180 timer, type: 'Delete 180'.")
                elif len(content) > 1 and content[1] in running_timers and content[0] == 'delete':
                    await message.add_reaction('⏰')
                    await message.channel.send(f'Timer for {content[1]} has been deleted.')
                    del running_timers[content[1]]
                elif (content[0] == 'set') and (content[1] in raid_timers or content[1] in edl_timers or content[1] in event_timers):
                    if (len(content) == 5) and (content[2].endswith('h')) and (content[3] == 'to') and (content[4].endswith('h')):
                        if content[1] in running_timers:
                            del running_timers[content[1]]
                            await message.channel.send(f"Running timer for **{content[1]}** has been stopped.")
                        if content[1] in raid_timers:
                            del raid_timers[content[1]]
                        elif content[1] in edl_timers:
                            del edl_timers[content[1]]
                        else:
                            del event_timers[content[1]]
                        event_timers[content[1]] = 3600*float(content[2].rstrip('h'))
                        event_timers_window[content[1]] = 3600*float(content[4].rstrip('h')) - 3600*float(content[2].rstrip('h'))
                        await message.add_reaction('⏰')
                        await message.channel.send(f"An event timer for **{content[1]}** has been created and set to {float(content[2].rstrip('h'))} hours to {float(content[4].rstrip('h'))} hours. Please type **'{content[1]}'** to start the timer.")
                    elif (len(content) == 3) and (content[2].endswith('h')):
                        if content[1] in running_timers:
                            del running_timers[content[1]]
                            await message.channel.send(f"Running timer for **{content[1]}** has been stopped.")
                        if content[1] in raid_timers:
                            del raid_timers[content[1]]
                        elif content[1] in edl_timers:
                            del edl_timers[content[1]]
                        else:
                            del event_timers[content[1]]
                        event_timers[content[1]] = 3600*float(content[2].rstrip('h'))
                        await message.add_reaction('⏰')
                        await message.channel.send(f"An event timer for **{content[1]}** has been created and set to {float(content[2].rstrip('h'))} hours. Please type **'{content[1]}'** to start the timer.")
                    else:
                        await message.channel.send("Invalid syntax.")
                elif content[0] in event_timers:
                    # Get the duration for the raid timer
                    duration = event_timers[content[0]]
                    if content[0] in event_timers_window:
                        window = event_timers_window[content[0]]
                    # If there's a second word and it ends with 'm', adjust the duration
                    if len(content) > 1 and content[1].endswith('m'):
                        minutes = int(content[1][:-1])
                        duration -= minutes * 60
                    # React to the message with a '⏰' emoji
                    await message.add_reaction('⏰')
                    # Calculate the expiry time for the event timer
                    expiry_time = int(time.time() + duration)
                    # Send a message to the channel indicating the raid timer has started
                    await message.channel.send(f"An event raid timer for **{content[0]}** has started. It will expire in <t:{int(expiry_time)}:f>(<t:{int(expiry_time)}:R>).")
                    # Start the raid timer
                    if content[0] not in event_timers_window:
                        await start_event_timer(message, content[0], duration)
                    else:
                        await start_event_timer_window(message, content[0], duration, window)
    except AttributeError:
        if not message.author == bot.user:
            await message.channel.send("?? Get outa here bozo")
async def clear_all():
    global edl_timers, edl_timers_perm, raid_timers, raid_timers_perm, event_timers, running_timers
    running_timers.clear()
    event_timers.clear()
    event_timers_window.clear()
    event_flag.clear()
    edl_timers = edl_timers_perm.copy()
    raid_timers = raid_timers_perm.copy()


async def start_edl_timers(message, keyword, duration):
    if (keyword in running_timers) and (running_timers[keyword][0]+running_timers[keyword][1]>time.time()):  # Check if a timer with the same keyword is already running
        embed = discord.Embed(title=f"A timer for **{keyword}** was already running.", description="It will be replaced by the new timer.", color=discord.Color.blue())
        await message.channel.send(embed=embed)
    start_time = time.time()
    running_timers[keyword] = (start_time, duration)
    await asyncio.sleep(duration - 180)  # Sleep until 3 minutes before the timer ends
    if running_timers.get(keyword) == (start_time, duration):  
        if keyword in role_id:
            await asyncio.sleep(180)
            await message.channel.send(f"**{keyword}** is due! <@&{role_id[keyword]}>")
        else:
            await message.channel.send(f"**{keyword}** will be due in 3 minutes! <@&1203363951056789525>")
            await asyncio.sleep(180)  
            await message.channel.send(f"**{keyword}** is due! <@&1203363951056789525>")

async def start_raid_timer(message, keyword, duration):
    if (keyword in running_timers):  # Check if a timer with the same keyword is already running
        embed = discord.Embed(title=f"A raid timer for **{keyword}** was already running.", description="It will be replaced by the new timer.", color=discord.Color.blue())
        await message.channel.send(embed=embed)
    start_time = time.time()
    running_timers[keyword] = (start_time, duration)
    if keyword=='gele' or keyword=='aggy' or keyword == 'mord':
        additional = 2*60*60
    # elif keyword=='test':
    #     additional = 10
    else:
        additional = 3*60*60    
    await asyncio.sleep(duration - raid_timers[keyword]/2 + additional)  # Sleep until timer reaches half
    if running_timers.get(keyword) == (start_time, duration):  # Check if the current timer is still running
        if keyword in role_id:
            await message.channel.send(f"Window for **{keyword}** is open! <@&{role_id[keyword]}>")
        else:
            await message.channel.send(f"Window for **{keyword}** is open!")
        await asyncio.sleep(duration / 2 - additional)  # Sleep for the remaining half of the timer
        if running_timers.get(keyword) == (start_time, duration):  # Check again if the current timer is still running
            if keyword in role_id:
                await message.channel.send(f"Window for **{keyword}** is closed! <@&{role_id[keyword]}>")
            else:
                await message.channel.send(f"Window for **{keyword}** is closed!")
            del running_timers[keyword]

async def start_event_timer(message, keyword, duration):
    if (keyword in running_timers):  # Check if a timer with the same keyword is already running
       embed = discord.Embed(title=f"An event raid timer for **{keyword}** was already running.", description="It will be replaced by the new timer.", color=discord.Color.blue())
       await message.channel.send(embed=embed)
    start_time = time.time()
    running_timers[keyword] = (start_time, duration)
    await asyncio.sleep(duration)
    if running_timers.get(keyword) == (start_time, duration):  # Check again if the current timer is still running
        if keyword in role_id:
            await message.channel.send(f"Event timer for **{keyword}** has expired! <@&{role_id[keyword]}>")
        else:
            await message.channel.send(f"Event timer for **{keyword}** has expired!")
        del running_timers[keyword]

async def start_event_timer_window(message, keyword, duration, window):
    if (keyword in running_timers):  # Check if a timer with the same keyword is already running
       embed = discord.Embed(title=f"An event raid timer for **{keyword}** was already running.", description="It will be replaced by the new timer.", color=discord.Color.blue())
       await message.channel.send(embed=embed)
    start_time = time.time()
    running_timers[keyword] = (start_time, duration)
    event_flag[keyword] = 'open'
    await asyncio.sleep(duration)
    if running_timers.get(keyword) == (start_time, duration):  # Check again if the current timer is still running
        if keyword in role_id:
            await message.channel.send(f"Window for **{keyword}** is open! <@&{role_id[keyword]}>")
        else:
            await message.channel.send(f"Window for **{keyword}** is open!")
        del running_timers[keyword]
        start_time = time.time()
        running_timers[keyword] = (start_time, window)
        event_flag[keyword] = 'close'
        await asyncio.sleep(window)
    if running_timers.get(keyword) == (start_time, window):  # Check again if the current timer is still running
        if keyword in role_id:
            await message.channel.send(f"Window for **{keyword}** is closed! <@&{role_id[keyword]}>")
        else:
            await message.channel.send(f"Window for **{keyword}** is closed!")
        del running_timers[keyword]
        del event_flag[keyword]
        #print(running_timers)

async def display_running_timers(channel):
    timer_list = []
    edl_list = []
    raid_list = []
    event_list = []
    sorted_timers = sorted(running_timers.items(), key=lambda item: item[1][0] + item[1][1])
    for content, (start_time, duration) in sorted_timers:
        remaining_time = int(start_time + duration) - time.time()
        hours, remainder = divmod(remaining_time, 3600)
        minutes, seconds = divmod(remainder, 60)
        if content in raid_timers:
            if content=='gele' or content=='aggy' or content == 'mord':
                additional = 2*60*60
            # elif content=='test':
            #     additional = 10
            else:
                additional = 3*60*60
            if remaining_time > raid_timers[content] / 2 + additional:
                raid_list.append(f"* 🔴 **{content}:** Window closed. Opens <t:{int(start_time + duration - raid_timers[content]/2 + additional)}:R> - <t:{int(start_time + duration - raid_timers[content]/2 + additional)}:f>")
            else:
                raid_list.append(f"* 🟢 **{content}:** Window open. Closes <t:{int(start_time + duration + additional)}:R> - <t:{int(start_time + duration + additional)}:f>")
        elif content in event_timers_window:
            if event_flag[content] == 'open':
                event_list.append(f"* 🔴 **{content}:** Window closed. Opens <t:{int(start_time + duration)}:R> - <t:{int(start_time + duration)}:f>")                        
            else:
                event_list.append(f"* 🟢 **{content}:** Window open. Closes <t:{int(start_time + duration)}:R> - <t:{int(start_time + duration)}:f>")
        elif content in event_timers:
            remaining_time_str = f"{int(hours)}:{int(minutes)}:{int(seconds)}"
            event_list.append(f"* ✅ **{content}:** {remaining_time_str} remaining - Spawns <t:{int(start_time + duration)}:R> - <t:{int(start_time + duration)}:f>")
        else:
            if remaining_time>0:
                remaining_time_str = f"{int(hours)}:{int(minutes)}:{int(seconds)}"
                if content == 'prot':
                    raid_list.append(f"* ✅ **{content}:** {remaining_time_str} remaining - Due <t:{int(start_time + duration)}:R> - <t:{int(start_time + duration)}:f>")
                else:
                    edl_list.append(f"* ✅ **{content}:** {remaining_time_str} remaining - Due <t:{int(start_time + duration)}:R> - <t:{int(start_time + duration)}:f>")
            else:
                remaining_time = time.time() - int(start_time + duration)
                hours, remainder = divmod(remaining_time, 3600)
                minutes, seconds = divmod(remainder, 60)
                remaining_time_str = f"{int(hours)}:{int(minutes)}:{int(seconds)}"
                if content == 'prot':
                    raid_list.append(f"* ❌ **{content}:** {remaining_time_str} ago - Due <t:{int(start_time + duration)}:R> - **MISSING TIMER**")
                else:
                    edl_list.append(f"* ❌ **{content}:** {remaining_time_str} ago - Due <t:{int(start_time + duration)}:R> - **MISSING TIMER**")
    if len(edl_list) > 0:
        timer_list.append("**EDL TIMERS:**")
        for timer in edl_list:
            timer_list.append(timer)
    if len(raid_list) > 0:
        timer_list.append("**RAID TIMERS:**")
        for timer in raid_list:
            timer_list.append(timer)
    if len(event_list) > 0:
        timer_list.append("**EVENT TIMERS:**")
        for timer in event_list:
            timer_list.append(timer)
    timer_list_str = '\n'.join(timer_list)
    embed = discord.Embed(title="Currently running timers:", description=timer_list_str if running_timers else "No timers are currently running.", color=discord.Color.blue())
    await channel.send(embed=embed)
   
bot.run(Token)