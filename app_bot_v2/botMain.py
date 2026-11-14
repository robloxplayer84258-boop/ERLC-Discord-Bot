import os
import discord
from discord.ext import commands, tasks
from discord import app_commands, ui
from dotenv import load_dotenv, set_key
from discord.ui import View, Select
import io
import asyncio
import json
from pathlib import Path
import requests
import data_sender


load_dotenv()

configContent = {
    "Ticket_Log_Channel": "0",
    "Ticket_Category": "1567274240695341106",
    "Ticket_Number": 0,
    "Bot_Status": "Offline",
}

BASE_DIR = Path(__file__).resolve().parent
configFile = BASE_DIR / "configuration.json"
configContent = {}
dotenv_path = BASE_DIR / ".env"

lastTime = 0

def handle_data(data):
    print(data)
    if "ingamePlayerCount" in data:
        global ingamePlayerCount
        ingamePlayerCount = data["ingamePlayerCount"]

    if "ERLC_Info" in data:
        ERLC_Data = data["ERLC_Info"]
        global maxPlayerCount
        maxPlayerCount = ERLC_Data["MaxPlayers"]
        ingamePlayerCount.value = str(len(ERLC_Data["Players"])) + "/" + str(maxPlayerCount)


try:
    data_sender.data_callback = handle_data
except Exception as e:
    print(e)

async def updateConfig():
    await asyncio.sleep(0.1)
    while True:
        with open(configFile, "w") as f:
            json.dump(configContent, f, indent=4)
        await asyncio.sleep(60)

def check_config(obj):

    if isinstance(obj, dict):

        for key, value in obj.items():

            if value == "":
                obj[key] = "0"

            elif isinstance(value, (dict, list)):
                check_config(value)

    elif isinstance(obj, list):

        for i, value in enumerate(obj):

            if value == "":
                obj[i] = "0"

            elif isinstance(value, (dict, list)):
                check_config(value)

with open(configFile, "r", encoding="utf-8") as file:
    #configContent["GUILD_ID"]
    try:
        configContent = json.load(file)
    except json.decoder.JSONDecodeError:
        configContent = {}
    check_config(configContent)
    JSON_GUILD_ID = configContent.setdefault("GUILD_ID", None)
    JSON_ERLC_API_KEY = configContent.setdefault("ERLC_API_KEY", None)
    JSON_TOKEN = configContent.setdefault("TOKEN", None)
        
    noQuote_TOKEN = JSON_TOKEN.strip("'\"")
    noQuote_ERLC_API_KEY = JSON_ERLC_API_KEY.strip("'\"")
    noQuote_GUILD_ID = JSON_GUILD_ID.strip("'\"")

with open(configFile, "w") as f:
    json.dump(configContent, f, indent=4)

    set_key(dotenv_path, "TOKEN", noQuote_TOKEN, quote_mode="never")
    set_key(dotenv_path, "GUILD_ID", noQuote_GUILD_ID, quote_mode="never")
    set_key(dotenv_path, "ERLC_API_KEY", noQuote_ERLC_API_KEY, quote_mode="never")
    load_dotenv(dotenv_path, override=True)


infractAddRole = False
if configContent["Infract_Add_Roles"] == True:
    infractAddRole = True

ticketLogChannel = int(configContent["Ticket_Log_Channel"])
ticketNumber = int(configContent["Ticket_Number"])

GUILD_ID = int(os.getenv("GUILD_ID")) if os.getenv("GUILD_ID") else None
ERLC_API_KEY = os.getenv("ERLC_API_KEY")
TOKEN = os.getenv('TOKEN')
intents = discord.Intents.default()
intents.all()

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):

        guild = discord.Object(id=GUILD_ID)
        self.tree.copy_global_to(guild=guild)

        self.tree.clear_commands(guild=guild)
        await self.tree.sync(guild=guild)

        await self.tree.sync()
        



bot = MyBot()

@bot.event
async def on_ready():
    print(f"logged in successfully as {bot.user}")
    with open(configFile, "w") as statusFile:
        configContent["Bot_Status"] = "Online"
        json.dump(configContent, statusFile, indent=4)
        data_sender.botDataSender("test test e 234 rt edgr")
    await updatePlayerCount()
    await updateConfig()

@bot.tree.command(name="infract") # TODO: Add roles 
@app_commands.choices(punishment=[
    app_commands.Choice(name="Verbal Warning", value="Verbal Warning"),
    app_commands.Choice(name="Warning 1", value="Warning 1"),
    app_commands.Choice(name="Warning 2", value="Warning 2"),
    app_commands.Choice(name="Warning 3", value="Warning 3"),
    app_commands.Choice(name="Strike 1", value="Strike 1"),
    app_commands.Choice(name="Strike 2", value="Strike 2"),
    app_commands.Choice(name="Strike 3", value="Strike 3"),
    app_commands.Choice(name="Termination", value="Termination"),
    app_commands.Choice(name="Activity Notice", value="Activity Notice"),
    app_commands.Choice(name="Staff Blacklist", value="Staff Blacklist"),
    app_commands.Choice(name="Demotion", value="Demotion")
])
async def infract(interaction: discord.Interaction, infracted: discord.Member, punishment: str, reason: str, notes: str): 
    colorString = configContent["Infract"]["Color"]
    colorList = [int(x) for x in colorString.split(",")]
    INFRACTED = infracted.mention
    PUNISHMENT = punishment
    NOTES = notes
    USER = interaction.user.mention
    REASON = reason
    title = configContent["Infract"]["Title"]
    description = str(configContent["Infract"]["Description"])
    description = description.replace("{INFRACTED}", infracted.mention)
    description = description.replace("{PUNISHMENT}", punishment)
    description = description.replace("{NOTES}", notes)
    description = description.replace("{USER}", interaction.user.mention)
    description = description.replace("{REASON}", reason)

    infractEmbed = discord.Embed(
        color=discord.Color.from_rgb(*colorList),
        title=f"{title}",
        description=f"{description}"
    )
    if configContent["Infract"]["Image"] != "":
        infractEmbed.set_image(url=configContent["Infract"]["Image"])
    await interaction.response.send_message(embed=infractEmbed) # TODO: send in the promotions channel and ADD that to GUI

@bot.tree.command(name="promote")
async def promote(interaction: discord.Interaction, promoted: discord.Member, new_rank: discord.Role, reason: str, notes: str):
    colorString = configContent["Promote"]["Color"]
    colorList = [int(x) for x in colorString.split(",")]

    title = configContent["Promote"]["Title"]
    description = str(configContent["Promote"]["Description"])

    placeholders = {
        "{PROMOTED}": promoted.mention,
        "{NEW_RANK}": new_rank.mention,
        "{NOTES}": notes,
        "{USER}": interaction.user.mention,
        "{REASON}": reason
    }

    for placeholder, value in placeholders.items():
        description = description.replace(placeholder, value)

    promoteEmbed = discord.Embed(
        color=discord.Color.from_rgb(*colorList),
        title=title,
        description=description
    )
    if configContent["Promote"]["Image"] != "":
        promoteEmbed.set_image(url=configContent["Promote"]["Image"])
    await interaction.response.send_message(embed=promoteEmbed, content=promoted.mention)



    
    
options = [

]

if configContent["Tickets"]["InternalAffairs"]["Enabled"] == True:
    IA_Option = discord.SelectOption(
        label="Internal Affairs",
        description=""
    )
    options.append(IA_Option)


if configContent["Tickets"]["DiscordModerationTeam"]["Enabled"] == True:
    DMT_Option = discord.SelectOption(
        label="Discord Moderation Team",
        description=""
    )
    options.append(DMT_Option)

if configContent["Tickets"]["Media"]["Enabled"] == True:
    Media_Option = discord.SelectOption(
        label="Media",
        description=""
    )
    options.append(Media_Option)


if configContent["Tickets"]["Management"]["Enabled"] == True:
    MGMT_Option = discord.SelectOption(
        label="Management",
        description=""
    )
    options.append(MGMT_Option)


if configContent["Tickets"]["Leadership"]["Enabled"] == True:
    LD_Option = discord.SelectOption(
        label="Leadership",
        description=""
    )
    options.append(LD_Option)

if options != []:
    class TicketOptions(discord.ui.Select):
        def __init__(self):


            super().__init__(
                placeholder="Choose an option...",
                options=options,
                custom_id="ticket_options"
            )

        async def callback(self, interaction: discord.Interaction): # TODO: make the ticket claiming thing
            chosen_option = self.values[0]
            guild = interaction.guild
            global ticketNumber
            ticketNumber += 1
            data_sender.botDataSender({"TicketNumber": ticketNumber})
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(view_channel=False),
                interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True),
                interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True),
            }

            buttonUser = str(interaction.user)
            ticketUsernameLower = buttonUser.lower()
            ticketChannelName = str(ticketUsernameLower)

            buttonUser = str(interaction.user)
            ticketUsernameLower = buttonUser.lower()
            ticketChannelName = str(ticketUsernameLower)
            DMT_Category = guild.get_channel(int(configContent["Tickets"]["DiscordModerationTeam"]["CategoryID"]))
            IA_Category = guild.get_channel(int(configContent["Tickets"]["InternalAffairs"]["CategoryID"]))
            Media_Category = guild.get_channel(int(configContent["Tickets"]["Media"]["CategoryID"]))
            Management_Category = guild.get_channel(int(configContent["Tickets"]["Management"]["CategoryID"]))
            Leadership_Category = guild.get_channel(int(configContent["Tickets"]["Leadership"]["CategoryID"]))
            if chosen_option == "Discord Moderation Team":
                ticketName = "dmt" + "_" + str(ticketNumber) + "_" + str(ticketChannelName)
                await guild.create_text_channel(name=ticketName, overwrites=overwrites, category=DMT_Category)
                await interaction.response.send_message(f"Created Ticket!", ephemeral=True)

            elif chosen_option == "Internal Affairs":
                ticketName = "ia" + "_" + str(ticketNumber) + "_" + str(ticketChannelName)
                await guild.create_text_channel(name=ticketName, overwrites=overwrites, category=IA_Category)
                await interaction.response.send_message(f"Created Ticket!", ephemeral=True)

            elif chosen_option == "Media":
                ticketName = "media" + "_" + str(ticketNumber) + "_" + str(ticketChannelName)
                await guild.create_text_channel(name=ticketName, overwrites=overwrites, category=Media_Category)
                await interaction.response.send_message(f"Created Ticket!", ephemeral=True)

            elif chosen_option == "Management":
                ticketName = "mgmt" + "_" + str(ticketNumber) + "_" + str(ticketChannelName)
                await guild.create_text_channel(name=ticketName, overwrites=overwrites, category=Management_Category)
                await interaction.response.send_message(f"Created Ticket!", ephemeral=True)

            elif chosen_option == "Leadership":
                ticketName = "ld" + "_" + str(ticketNumber) + "_" + str(ticketChannelName)
                await guild.create_text_channel(name=ticketName, overwrites=overwrites, category=Leadership_Category)
                await interaction.response.send_message(f"Created Ticket!", ephemeral=True)



if options != []:
    class DropdownView(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=None)
            self.add_item(TicketOptions())

TicketsField1 = configContent["Tickets"]["Field_1"]
TicketsField2 = configContent["Tickets"]["Field_2"]
TicketsField3 = configContent["Tickets"]["Field_3"]
TicketsField4 = configContent["Tickets"]["Field_4"]
TicketsField5 = configContent["Tickets"]["Field_5"]

@bot.tree.command(name="tickets")
async def tickets(interaction: discord.Interaction):
    embed = discord.Embed(
        title="Michigan State Roleplay Tickets",
        color=0xe4b43c
    )
    if(TicketsField1["Enabled"] == True):
        embed.add_field(
            inline=False,
            name=TicketsField1["Title"],
            value=TicketsField1["Description"]
        )

    if(TicketsField2["Enabled"] == True):
        embed.add_field(
            inline=False,
            name=TicketsField2["Title"],
            value=TicketsField2["Description"]
        )


    if(TicketsField3["Enabled"] == True):
        embed.add_field(
            inline=False,
            name=TicketsField3["Title"],
            value=TicketsField3["Description"]
        )

    if(TicketsField4["Enabled"] == True):
        embed.add_field(
            inline=False,
            name=TicketsField4["Title"],
            value=TicketsField4["Description"]
        )

    if(TicketsField5["Enabled"] == True):
        embed.add_field(
            inline=False,
            name=TicketsField5["Title"],
            value=TicketsField5["Description"]
        )
    if options != []:
        view = DropdownView()
    else:
        view = None

    await interaction.channel.send(
        embed=embed,
        view=view
    )
    await interaction.response.send_message("Sent tickets", ephemeral=True)

@bot.tree.command(name="closeticket", description="deletes the channel ran in and logs everything")
async def closeticket(interaction: discord.Interaction, reason: str):

    loggingChannel = interaction.guild.get_channel(int(configContent["CloseTicket"]["LogChannel"]))
    DMT_Category = interaction.guild.get_channel(int(configContent["Tickets"]["DiscordModerationTeam"]["CategoryID"]))
    IA_Category = interaction.guild.get_channel(int(configContent["Tickets"]["InternalAffairs"]["CategoryID"]))
    Media_Category = interaction.guild.get_channel(int(configContent["Tickets"]["Media"]["CategoryID"]))
    Management_Category = interaction.guild.get_channel(int(configContent["Tickets"]["Management"]["CategoryID"]))
    Leadership_Category = interaction.guild.get_channel(int(configContent["Tickets"]["Leadership"]["CategoryID"]))

    checkCategory = [
        int(configContent["CloseTicket"]["LogChannel"]),
        int(configContent["Tickets"]["DiscordModerationTeam"]["CategoryID"]),
        int(configContent["Tickets"]["InternalAffairs"]["CategoryID"]),
        int(configContent["Tickets"]["Media"]["CategoryID"]),
        int(configContent["Tickets"]["Management"]["CategoryID"]),
        int(configContent["Tickets"]["Leadership"]["CategoryID"])   
    ]
    if int(interaction.channel.category_id) not in checkCategory: # TODO: Fix this saying not ticket category
        await interaction.response.send_message(content="This is not a ticket category!", ephemeral=True)
        return
    try:
        channel = interaction.channel
        log_channel = loggingChannel
        list = []
        await log_channel.send(content=f"`START {str(channel.name)} Reason for ticket close: {reason} ====================`")
        async for message in channel.history(limit=None, oldest_first=True):

            messageContent = message.content.replace("```", "'''")
            
            if message.attachments:
                files = [
                    await attachment.to_file()
                    for attachment in message.attachments
                ]

                messageText = str(channel.name)

                await log_channel.send(
                    files=files,
                    content=messageText
                )
                messageContent = "[BOT]: This message is just a file. Files are above this file."
                

            messageSendTime = message.created_at
            formatted_time = messageSendTime.strftime("[%d %H:%M:%S UTC]")
            messageSender = str(message.author)
            list.append(formatted_time + " " + messageSender + ": " + messageContent)
        
        logList = "\n".join(list)
        file_buffer = io.StringIO(logList)
        txtFile = discord.File(file_buffer, filename=f"{interaction.channel.name}.txt")
        await log_channel.send(file=txtFile)
        await log_channel.send(content=f"`END {str(channel.name)} ====================`")
        await interaction.channel.delete()
    except discord.HTTPException as e:
        if e.code == 429:
            await asyncio.sleep(5)
            
@bot.tree.command(name="run_ingame_command")
async def ingame_command(interaction: discord.Interaction, command: str):
    commandLogChannel = interaction.guild.get_channel(int(configContent["IngameCommand"]["LogChannel"]))
    data_sender.botDataSender({"ingame_command": command})

    logEmbed = discord.Embed(
        color=discord.Color.from_rgb(48, 193, 225),
        title=f"{interaction.user.name} has sent a remote command.",
        description=f"Command Sent:```{command}```"
    )

    await interaction.response.send_message("Running.", ephemeral=True)
    await commandLogChannel.send(embed=logEmbed)

sessionVoters = []


currentVotes = 0
class voteButton(discord.ui.View):
  def __init__(self, label: str):
    super().__init__()

    button = discord.ui.Button(
        label=label,
        style=discord.ButtonStyle.primary,
        custom_id="voteButton",
        
    )
    button.callback = self.button_callback
    self.add_item(button)

  async def button_callback(self, interaction: discord.Interaction):
    global sessionVoters, voteEmbed, voteEmbedToEdit

    if interaction.user in sessionVoters:
        await interaction.response.send_message(
            "You have already voted!",
            ephemeral=True
        )
        return
    if interaction.user not in sessionVoters:
        sessionVoters.append(interaction.user)
        global currentVotes
        currentVotes += 1
        global votePlaceholders
        votePlaceholders = {
            "{VOTES_REQUIRED}": str(votes_required_global),
            "{VOTE_FOR}": vote_for_global,
            "{SENT_BY}": interaction.user.mention,
            "{CURRENT_VOTES}": str(currentVotes)
        }
        global voteDescription
        voteDescription = configContent["SessionVote"]["Description"]
        for placeholder, value in votePlaceholders.items():
            voteDescription = voteDescription.replace(placeholder, value)
            
        voteEmbed.description = voteDescription
        voteEmbed.title = configContent["SessionVote"]["Title"]
        voteEmbed.color = sessionVoteColor
        if configContent["SessionVote"]["Image"] != "0":
            voteEmbed.set_image(url=configContent["SessionVote"]["Image"])

        await voteEmbedToEdit.edit(embed=voteEmbed)

        await interaction.response.send_message(
            "Thanks for voting!",
            ephemeral=True
        )
    else:
        await interaction.response.send_message("Error.", ephemeral=True)


@bot.tree.command(name="session_vote")
async def session_vote(interaction: discord.Interaction, votes_required: int, vote_for: str):
    data_sender.botDataSender("Session vote")
    global vote_for_global
    vote_for_global = vote_for

    global votes_required_global
    votes_required_global = votes_required
    colorString = configContent["Infract"]["Color"]
    colorList = [int(x) for x in colorString.split(",")]
    global sessionVoteColor
    sessionVoteColor = discord.Color.from_rgb(*colorList)

    global votePlaceholders
    votePlaceholders = {
        "{VOTES_REQUIRED}": str(votes_required),
        "{VOTE_FOR}": vote_for,
        "{SENT_BY}": interaction.user.mention,
        "{CURRENT_VOTES}": str(currentVotes)
    }
    global voteDescription
    voteDescription = configContent["SessionVote"]["Description"]
    for placeholder, value in votePlaceholders.items():
        voteDescription = voteDescription.replace(placeholder, value)
    global voteEmbed
    voteEmbed = discord.Embed(
        title=configContent["SessionVote"]["Title"],
        description=f"{voteDescription}",
        color=sessionVoteColor
    )
    if configContent["SessionVote"]["Image"] != "0":
        voteEmbed.set_image(url=configContent["SessionVote"]["Image"])


    global voteEmbedToEdit
    voteEmbedToEdit = await interaction.channel.send(embed=voteEmbed, view=voteButton("Vote!"))
    await interaction.response.send_message("Session Vote Sent!", ephemeral=True)

ssuSentBy = None
ingamePlayerCount = "No Data"
ssuEmbedToEdit = None
@bot.tree.command(name="ssu")
async def ssu(interaction: discord.Interaction):
    colorString = configContent["SSU"]["Color"]
    colorList = [int(x) for x in colorString.split(",")]
    embedColor = discord.Color.from_rgb(*colorList)
    global ssuSentBy
    ssuSentBy = interaction.user.mention
    global ingamePlayerCount
    placeholders = {
        "{SENT_BY}": ssuSentBy,
        "{INGAME_COUNT}": str(ingamePlayerCount)
    }
    global ssuDescription
    ssuDescription = configContent["SSU"]["Description"]
    for placeholder, value in placeholders.items():
        ssuDescription = ssuDescription.replace(placeholder, value)
    global ssuEmbed
    ssuEmbed = discord.Embed(
        title=configContent["SSU"]["Title"],
        description=ssuDescription,
        color=embedColor
    )

    global ssuEmbedToEdit
    ssuEmbedToEdit = await interaction.channel.send(embed=ssuEmbed)

async def updatePlayerCount():
    while True:
        await asyncio.sleep(0.1)
        # if ssuEmbedToEdit != None:
        try:
            global ssuSentBy
            global ingamePlayerCount

            placeholders = {
                "{SENT_BY}": ssuSentBy,
                "{INGAME_COUNT}": str(ingamePlayerCount)
            }

            global ssuDescription
            ssuDescription = configContent["SSU"]["Description"]
            for placeholder, value in placeholders.items():
                if value == None:
                    value = "Value was None in updatePlayerCount function."
                ssuDescription = ssuDescription.replace(placeholder, value)
            ssuEmbed.description = ssuDescription
            colorString = configContent["SSU"]["Color"]
            colorList = [int(x) for x in colorString.split(",")]
            embedColor = discord.Color.from_rgb(*colorList)

            ssuEmbed.description = ssuDescription
            ssuEmbed.title = configContent["SSU"]["Title"]
            ssuEmbed.color = embedColor
            await asyncio.sleep(5.1)
            await ssuEmbedToEdit.edit(embed=ssuEmbed)
            print("embed edit ")
        except Exception as e:
            print(e)
            await asyncio.sleep(10)

class linkButton(discord.ui.View):
  def __init__(self, label: str, url: str):
    super().__init__()            
    button = discord.ui.Button(label=label, url=url)
    self.add_item(button)


@bot.event
async def on_member_join(member):
    colorString = configContent["on_member_join"]["Color"]
    colorList = [int(x) for x in colorString.split(",")]

    placeholders = {
        "{MEMBER}": str(member),
    }
    description = configContent["on_member_join"]["Description"]
    for placeholder, value in placeholders.items():
        description = description.replace(placeholder, value)
    
    memberJoinEmbed = discord.Embed(
        title=configContent["on_member_join"]["Title"],
        description=configContent["on_member_join"]["Description"],
        color=discord.Color.from_rgb(*colorList)
    )
    ping = member.mention
    if configContent["on_member_join"]["Image"] != "0":
        memberJoinEmbed.set_image(url=configContent["on_member_join"]["Image"])
    welcomeChannel = bot.get_channel(int(configContent["on_member_join"]["send_channel"]))
    URL = configContent["on_member_join"]["ButtonURL"]
    label = configContent["on_member_join"]["ButtonLabel"]
    await welcomeChannel.send(embed=memberJoinEmbed, content=ping, view=linkButton(label=label, url=URL))
@bot.tree.command(name="test_join")

async def test_join(interaction: discord.Interaction, member: discord.Member):
    await on_member_join(member)


cloudflareInvite_url = "https://invite.robloxplayer84258.workers.dev" 
async def getInvite():
    
    response = requests.get(url=cloudflareInvite_url, timeout=10)
    responseJson = json.loads(response.text)
    print(responseJson["discord_invite"])

    return responseJson

@bot.tree.command(name="info_about")
async def info_about(interaction: discord.Interaction):
    aboutEmbed = discord.Embed(
        title="About This Bot",
        color=discord.Color.from_rgb(163, 48, 225)
    )
    aboutEmbed.add_field(
        inline=False,
        name="Creator: RobloxPlayer84258",
        value=""
    )
    aboutEmbed.add_field(
        inline=False,
        name="Coded in: Python",
        value=""
    )
    data = await getInvite()
    supportServer = data["discord_invite"]
    try:
        await interaction.response.send_message(embed=aboutEmbed, view=linkButton(label="Support Server", url="https://" + supportServer))
    except Exception as e:
        print(e)

if __name__ == "__main__":
    bot.run(TOKEN)