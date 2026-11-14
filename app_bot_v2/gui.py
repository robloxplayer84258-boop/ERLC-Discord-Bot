import flet as ft
import json
import asyncio
from pathlib import Path
import data_sender
import time
import shutil
import os

discordServerLink = "https://discord.gg/xnR3BTN84"
IPv6VerifyThing = "https://api.erlc.gg/server-owners"
BASE_DIR = Path(__file__).resolve().parent
configFile = BASE_DIR / "configuration.json"
discord_token = 0
ERLC_key = 0
configContent = {}
running = False
hasUpdateStatusStarted = False

ERLC_Data = {}
async def gui_main(page: ft.Page, data):
    with open(configFile, "r", encoding="utf-8") as file:
        configContent = json.load(file)

    def handle_data(data):
        if "ERLC_Info" in data:
            ERLC_Data = data["ERLC_Info"]["IngameInfo"]
            ingameServerName.value = ERLC_Data["Name"]
            ingamePlayerCount.value = str(len(ERLC_Data["Players"])) + "/" + str(ERLC_Data["MaxPlayers"])

    data_sender.data_callback = handle_data

    async def updateStatus(discordStatus: ft.Text, erlcStatus: ft.Text):
        while True:
            await asyncio.sleep(0.25)
            try:
                with open(configFile, "r") as status:
                    statusJSON = json.load(status)
                    currentStatus = statusJSON["Bot_Status"]
                    erlcStatusValue = statusJSON["ERLC_Status"]
                if discordStatus.value != currentStatus:
                    discordStatus.value = currentStatus
                    page.update()
                if erlcStatus.value != erlcStatusValue:
                    erlcStatus.value = erlcStatusValue
                    page.update()
                
            except Exception as e:
                print(e)
                continue

    botStatus = ft.Text("Status: ", color=ft.Colors.AMBER_400)
    erlcStatus = ft.Text("Status: ", color=ft.Colors.AMBER_400)

    task = asyncio.create_task(updateStatus(botStatus, erlcStatus))
    page.title = "ERLC Bot Dashboard"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#10131C"
    page.padding = 0
    page.window.width = 1150
    page.window.height = 760

    ACCENT = "#7289DA"
    PANEL = "#191F2D"
    MUTED = "#929BAD"

    def make_button(text, icon=None, on_click=None):
        return ft.Button(
            text,
            icon=icon,
            style=ft.ButtonStyle(
                bgcolor=ACCENT,
                color="white",
                shape=ft.RoundedRectangleBorder(radius=9),
            ),
            on_click=on_click
        )

    def make_field(label, password=False, hint=None, on_click=None, visible=None):
        return ft.TextField(
            label=label,
            hint_text=hint,
            password=password,
            can_reveal_password=password,
            border_color="#343D50",
            focused_border_color=ACCENT,
            bgcolor="#151A25",
            border_radius=10,
            on_click=on_click,
            visible=visible
        )

    def make_entry(label, hint=None, on_click=None, visibility=None):
        return ft.TextField(
            label=label,
            hint_text= hint,
            multiline=True,
            min_lines=4,
            max_lines=7,
            border_radius=10,
            border_color="#343D50",
            focused_border_color=ACCENT,
            bgcolor="#151A25",
            visible=visibility,
            on_click=on_click
        )
    def make_card(title, controls):
        return ft.Container(
            content=ft.Column(
                [
                    ft.Text(title, size=19, weight="bold"),
                    *controls,
                ],
                spacing=15,
            ),
            bgcolor=PANEL,
            padding=22,
            border_radius=14,
            width=760,
        )

    content = ft.Column(
        scroll=ft.ScrollMode.AUTO,
        expand=True,
        spacing=20,
    )
    

    def dashboard():

        async def run_bot(e):
            runButton.disabled = True
            stopButton.disabled = True
            runButton.bgcolor = "#1ab315"  

            page.update()
            if callable(data):
                await data("RunBot")
            await asyncio.sleep(10)
            stopButton.disabled = False
            stopButton.bgcolor = "#d80b0b" 
            page.update()


        async def stop_bot(e):
            runButton.disabled = True
            stopButton.disabled = True
            stopButton.bgcolor = "#9e0b0b"  
            page.update()
            if callable(data):
                await data("StopBot")
            await asyncio.sleep(10)
            
            runButton.disabled = False
            runButton.bgcolor = "#21e11b" 
            page.update()

      
        runButton = ft.Button(
            "Run Bot",
            on_click=run_bot,
            bgcolor="#21e11b",
            color="#ffffff"
        )
        stopButton = ft.Button(
            "Stop Bot",
            on_click=stop_bot,
            bgcolor="#d80b0b",
            color="#ffffff"
        )

        async def API_Start(e):
            runAPI.bgcolor = "#1ab315"
            stopAPI.bgcolor = "#d80b0b"
            if callable(data):
                await data("StartAPI")

        runAPI = ft.Button(
            "Start ER:LC API",
            on_click=API_Start,
            bgcolor="#21e11b",
            color="#ffffff"
        )

        async def API_Stop(e):
            runAPI.bgcolor = "#21e11b"
            stopAPI.bgcolor = "#9e0b0b"
            if callable(data):
                await data("StopAPI")
            
        
        stopAPI = ft.Button(
            "Stop ER:LC API",
            on_click=API_Stop,
            bgcolor="#d80b0b",
            color="#ffffff"
        )                
        

        content.controls = [
            ft.Text("Dashboard", size=30, weight="bold"),

            ft.Row(
                [
                    
                    # ft.Container(
                    #     content=ft.Column([
                    #         ft.Text("Discord Bot", color=MUTED),
                    #         botStatus,
                    #     ]),
                    #     bgcolor=PANEL,
                    #     padding=22,
                    #     border_radius=12,
                    #     expand=True,
                    # ),
                    ft.Container(
                        content=ft.Row([
                            ft.Column([
                                ft.Text("Discord Bot Controls", color=MUTED),
                                runButton,
                                stopButton,
                            ]),
                            ft.Column([
                                ft.Text("Controls", color=MUTED),
                                runAPI,
                                stopAPI,
                            ]),                      
                        ]),
                        bgcolor=PANEL,
                        padding=22,
                        border_radius=12,
                        expand=True,
                    )
                ]
            ),
            ft.Row([
                ft.Container(
                    content=ft.Column([
                        ft.Text("Discord Status", color=MUTED),
                        botStatus,
                    ]),
                    bgcolor=PANEL,
                    padding=22,
                    border_radius=12,
                    expand=True,
                ),     
                ft.Container(
                    content=ft.Column([
                        ft.Text("ERLC Status", color=MUTED),
                        ft.Text("If status is [4000], go to this link to verify your IPv6 address:"),
                        ft.TextButton(
                            content=ft.Text(
                                IPv6VerifyThing, 
                                style=ft.TextStyle(
                                    color=ft.Colors.BLUE, 
                                    decoration=ft.TextDecoration.UNDERLINE
                                )
                            ),
                            action=ft.CopyToClipboard(IPv6VerifyThing),
                        ),
                        erlcStatus,
                    ]),
                    bgcolor=PANEL,
                    padding=22,
                    border_radius=12,
                    expand=True,
                ),              
        ])

        ]
        page.update()

    def API_Save(e):
        ERLC_key = API_Entry.value
        with open(configFile, "w", encoding="utf-8") as file:
            configContent["ERLC_API_KEY"] = ERLC_key
            json.dump(configContent, file, indent=4)
    def loadKey(e):
        API_Entry.value = configContent["ERLC_API_KEY"]
    API_Entry = make_field(
        "ER:LC API Key",
        password=True,
        hint="Enter your private server API key",
        on_click=loadKey
    )
    global ingameServerName
    ingameServerName = ft.Text(value="Not loaded")
    ingamePlayerCount = ft.Text(value="Not Loaded")

    saveAPI = make_button("Save API Key", "save", on_click=API_Save)
    def erlc_settings():
        content.controls = [
            ft.Text("ER:LC Settings", size=30, weight="bold"),
            ft.Text("Configure your ER:LC API information.",
                    color=MUTED),
            make_card("API Configuration", [
                API_Entry,
                ft.Row([
                    saveAPI
                ]),
            ]),

            make_card(
                "In-Game Info",
                [
                    ft.Text(
                        "Run the discord bot to get in-game data.", 
                        color=MUTED,
                        size=12,
                    ),   
                    ingameServerName,
                    ingamePlayerCount
                    
                ]
            )
        ]
        page.update()

        

    def discord_settings():
        def loadToken(e):
            token_input.value = configContent["TOKEN"]
        def loadGuildID(e):
            guildID.value = configContent["GUILD_ID"]
        token_input = ft.TextField(
            label="Discord Bot Token",
            password=True,
            hint_text="Enter your bot token",
            can_reveal_password=True,
            on_click=loadToken
        )
        guildID = ft.TextField(
            label="Guild ID",
            hint_text="Enter your server's ID",
            on_click=loadGuildID
        )

        def tokenUpdate(e):
            discord_token = token_input.value
            with open(configFile, "w", encoding="utf-8") as file:
                configContent["TOKEN"] = discord_token
                configContent["GUILD_ID"] = guildID.value
                json.dump(configContent, file, indent=4)

        content.controls = [
            ft.Text("Discord Settings", size=30, weight="bold"),
            ft.Text("Configure your Discord bot.",
                    color=MUTED),
            make_card("Bot Configuration", [
                token_input,
                guildID,
                ft.Row([
                    ft.Button(
                        content="Save Token",
                        icon=None,
                        style=ft.ButtonStyle(
                            bgcolor=ACCENT,
                            color="white",
                            shape=ft.RoundedRectangleBorder(radius=9),
                        ),
                        on_click=tokenUpdate
                    ),
                ]),
            ]),
        ]
        page.update()


    def command_editor():

        async def infractValue(e):
            if e.control.value == True:
                if callable(data):
                    status = {"Infract_Add_Roles": e.control.value}
                    await data(status)
        
        def changeFields(e):

            selected_command = command_select.value
            if(selected_command == "Infract"):
                infract_card.visible = True
                variableText.value = "Variables:\n{INFRACTED} command field\n{PUNISHMENT} comand field\n {NOTES} command field\n {REASON} command field\n {USER} command sender"
            else:
                infract_card.visible = False
            if(selected_command == "CloseTicket"):
                messageSettings.visible = False
                embedImages.visible = False
                embedAppearance.visible = False
                ticketLogging.visible = True
            if(selected_command == "SessionVote"):
        # "{VOTES_REQUIRED}": str(votes_required),
        # "{VOTE_FOR}": vote_for,
        # "{SENT_BY}": interaction.user.mention,
        # "{CURRENT_VOTES}": str(currentVotes)

                variableText.value = "Variables:\n{VOTES_REQUIRED}"
            else:
                messageSettings.visible = True
                embedImages.visible = True
                embedAppearance.visible = True
                ticketLogging.visible = False

            if selected_command not in configContent:
                page.update()
                return
            if(selected_command == "Tickets"):
                embedAppearance.visible = False
                tickets_card.visible = True
                 
                field_1_switch.value = configContent["Tickets"]["Field_1"]["Enabled"]   
                field_1_title.value = configContent["Tickets"]["Field_1"]["Title"]
                field_1_entry.value = configContent["Tickets"]["Field_1"]["Description"]

                field_2_switch.value = configContent["Tickets"]["Field_2"]["Enabled"]   
                field_2_title.value = configContent["Tickets"]["Field_2"]["Title"]
                field_2_entry.value = configContent["Tickets"]["Field_2"]["Description"]

                field_3_switch.value = configContent["Tickets"]["Field_3"]["Enabled"]   
                field_3_title.value = configContent["Tickets"]["Field_3"]["Title"]
                field_3_entry.value = configContent["Tickets"]["Field_3"]["Description"]

                field_4_switch.value = configContent["Tickets"]["Field_4"]["Enabled"]   
                field_4_title.value = configContent["Tickets"]["Field_4"]["Title"]
                field_4_entry.value = configContent["Tickets"]["Field_4"]["Description"]
                
                field_5_switch.value = configContent["Tickets"]["Field_5"]["Enabled"]   
                field_5_title.value = configContent["Tickets"]["Field_5"]["Title"]
                field_5_entry.value = configContent["Tickets"]["Field_5"]["Description"]

                IA_Channel_Switch.value = configContent["Tickets"]["InternalAffairs"]["Enabled"]
                IA_Channel_Entry.value = configContent["Tickets"]["InternalAffairs"]["CategoryID"]

                DMT_Channel_Switch.value = configContent["Tickets"]["DiscordModerationTeam"]["Enabled"]
                DMT_Channel_Entry.value = configContent["Tickets"]["DiscordModerationTeam"]["CategoryID"]

                Media_Channel_Switch.value = configContent["Tickets"]["Media"]["Enabled"]
                Media_Channel_Entry.value = configContent["Tickets"]["Media"]["CategoryID"]

                MGMT_Channel_Switch.value = configContent["Tickets"]["Management"]["Enabled"]
                MGMT_Channel_Entry.value = configContent["Tickets"]["Management"]["CategoryID"]

                LD_Channel_Switch.value = configContent["Tickets"]["Leadership"]["Enabled"]
                LD_Channel_Entry.value = configContent["Tickets"]["Leadership"]["CategoryID"]

            

            else:
                embedAppearance.visible = True 
                tickets_card.visible = False                           
            command = configContent[selected_command]

            if(selected_command == "IngameCommand"):
                command_card.visible = True
                messageSettings.visible = False
                embedImages.visible = False
                embedAppearance.visible = False                
            else:
                command_card.visible = False
                messageSettings.visible = True
                embedImages.visible = True
                embedAppearance.visible = True

            if selected_command == "on_member_join":
                buttonConfig.visible = True
                joinButtonLabel.value = configContent["on_member_join"]["ButtonLabel"]
                joinButtonURL.value = configContent["on_member_join"]["ButtonURL"]
                joinChannelSend.value = configContent["on_member_join"]["send_channel"]
            else:
                buttonConfig.visible = False

      

            embed_title.value = command.get("Title", "")
            embed_description.value = command.get("Description", "")
            embed_image.value = command.get("Image", "")
            embed_color.value = command.get("Color", "")

            page.update()

        async def changeConfig(e):
            selected_command = command_select.value
            if "Title" in configContent[selected_command]:
                configContent[selected_command]["Title"] = embed_title.value

            if "Description" in configContent[selected_command]:
                configContent[selected_command]["Description"] = embed_description.value

            if "Image" in configContent[selected_command]:
                configContent[selected_command]["Image"] = embed_image.value

            if "Color" in configContent[selected_command]:
                configContent[selected_command]["Color"] = embed_color.value

            if "LogChannel" in configContent[selected_command]:
                configContent[selected_command]["LogChannel"] = ticketLogging.value

            if "Field_1" in configContent[selected_command]:
                configContent[selected_command]["Field_1"]["Enabled"] = field_1_switch.value
                configContent[selected_command]["Field_1"]["Title"] = field_1_title.value
                configContent[selected_command]["Field_1"]["Description"] = field_1_entry.value

            if "Field_2" in configContent[selected_command]:
                configContent[selected_command]["Field_2"]["Enabled"] = field_2_switch.value
                configContent[selected_command]["Field_2"]["Title"] = field_2_title.value
                configContent[selected_command]["Field_2"]["Description"] = field_2_entry.value

            if "Field_3" in configContent[selected_command]:
                configContent[selected_command]["Field_3"]["Enabled"] = field_3_switch.value
                configContent[selected_command]["Field_3"]["Title"] = field_3_title.value
                configContent[selected_command]["Field_3"]["Description"] = field_3_entry.value

            if "Field_4" in configContent[selected_command]:
                configContent[selected_command]["Field_4"]["Enabled"] = field_4_switch.value
                configContent[selected_command]["Field_4"]["Title"] = field_4_title.value
                configContent[selected_command]["Field_4"]["Description"] = field_4_entry.value


            if "Field_5" in configContent[selected_command]:
                configContent[selected_command]["Field_5"]["Enabled"] = field_5_switch.value
                configContent[selected_command]["Field_5"]["Title"] = field_5_title.value
                configContent[selected_command]["Field_5"]["Description"] = field_5_entry.value
            if "LogChannel" in configContent[selected_command]:
                configContent[selected_command]["LogChannel"] = commandLogEntry.value


            if "InternalAffairs" in configContent[selected_command]:
                configContent[selected_command]["InternalAffairs"]["CategoryID"] = IA_Channel_Entry.value
                configContent[selected_command]["InternalAffairs"]["Enabled"] = IA_Channel_Switch.value

            if "DiscordModerationTeam" in configContent[selected_command]:
                configContent[selected_command]["DiscordModerationTeam"]["CategoryID"] = DMT_Channel_Entry.value
                configContent[selected_command]["DiscordModerationTeam"]["Enabled"] = DMT_Channel_Switch.value

            if "Media" in configContent[selected_command]:
                configContent[selected_command]["Media"]["CategoryID"] = Media_Channel_Entry.value
                configContent[selected_command]["Media"]["Enabled"] = Media_Channel_Switch.value

            if "Management" in configContent[selected_command]:
                configContent[selected_command]["Management"]["CategoryID"] = MGMT_Channel_Entry.value
                configContent[selected_command]["Management"]["Enabled"] = MGMT_Channel_Switch.value

            if "Leadership" in configContent[selected_command]:
                configContent[selected_command]["Leadership"]["CategoryID"] = LD_Channel_Entry.value
                configContent[selected_command]["Leadership"]["Enabled"] = LD_Channel_Switch.value

            if "ButtonLabel" in configContent[selected_command]:
                configContent[selected_command]["ButtonLabel"] = joinButtonLabel.value

            if "ButtonURL" in configContent[selected_command]:
                configContent[selected_command]["ButtonURL"] = joinButtonURL.value 

            if "send_channel" in configContent[selected_command]["send_channel"]:
                configContent[selected_command]["send_channel"] = joinChannelSend         

            with open(configFile, "w", encoding="utf-8") as file:
                json.dump(configContent, file, indent=4)
            await asyncio.sleep(1)
        
        
        command_select = ft.Dropdown(
            label="Select Existing Command",
            hint_text="Choose a command to edit",
            options=[
                ft.dropdown.Option("Infract"),
                ft.dropdown.Option("SessionVote"),
                ft.dropdown.Option("Promote"),
                ft.dropdown.Option("Tickets"),
                ft.dropdown.Option("CloseTicket"),
                ft.dropdown.Option("IngameCommand"),
                ft.dropdown.Option("on_member_join"),
            ],
            on_select=changeFields
        )


        field_1_switch = ft.Switch(label="Field 1", value=True)
        field_1_title = make_field(hint="Enter the title for Field 1", label="Field 1 Title")
        field_1_entry = make_entry(hint="Enter the description for Field 1", label="Field 1 Description")

        field_2_switch = ft.Switch(label="Field 2", value=True)
        field_2_title = make_field(hint="Enter the title for Field 2", label="Field 2 Title")
        field_2_entry = make_entry(hint="Enter the description for Field 2", label="Field 2 Description")

        field_3_switch = ft.Switch(label="Field 3", value=True)
        field_3_title = make_field(hint="Enter the title for Field 3", label="Field 3 Title")
        field_3_entry = make_entry(hint="Enter the description for Field 3", label="Field 3 Description")

        field_4_switch = ft.Switch(label="Field 4", value=True)
        field_4_title = make_field(hint="Enter the title for Field 4", label="Field 4 Title")
        field_4_entry = make_entry(hint="Enter the description for Field 4", label="Field 4 Description")

        field_5_switch = ft.Switch(label="Field 5", value=True)
        field_5_title = make_field(hint="Enter the title for Field 5", label="Field 5 Title")
        field_5_entry = make_entry(hint="Enter the description for Field 5", label="Field 5 Description")
            # IA_Option,
            # DMT_Option,      
            # Media_Option,   
            # MGMT_Option,   
            # LD_Option   
        IA_Channel_Switch = ft.Switch(label="Create An Internal Affairs Ticket Option", value=True)
        IA_Channel_Entry = make_field(hint="Enter the category ID", label="Category ID")

        DMT_Channel_Switch = ft.Switch(label="Create A Discord Moderation Ticket Option", value=True)
        DMT_Channel_Entry = make_field(hint="Enter the category ID", label="Category ID")

        Media_Channel_Switch = ft.Switch(label="Create A Media Ticket Option", value=True)
        Media_Channel_Entry = make_field(hint="Enter the category ID", label="Category ID")

        MGMT_Channel_Switch = ft.Switch(label="Create A Management Ticket Option", value=True)
        MGMT_Channel_Entry = make_field(hint="Enter the category ID", label="Category ID")

        LD_Channel_Switch = ft.Switch(label="Create A Leadership Ticket Option", value=True)
        LD_Channel_Entry = make_field(hint="Enter the category ID", label="Category ID")

        commandLogEntry = make_field(hint="Enter the channel ID for in-game command logs.", label="Command log Channel")

        command_card = ft.Container(
            content=ft.Column([
                make_card(
                    title="In-Game Command Logs",
                    controls=[commandLogEntry]
                )
            ])
        )
        joinButtonLabel = make_field(label="Button Label", hint="Enter what you want the button to say.")
        joinButtonURL = make_field(label="Button URL", hint="Enter where you want the button to go.")
        joinChannelSend = make_field(label="Welcome Channel", hint="Enter your welcome channel ID.")
        buttonConfig = make_card(title="Configuration", controls=[
            joinButtonLabel,
            joinButtonURL,
            joinChannelSend
        ])
        buttonConfig.visible = False

        tickets_card = ft.Container(
            content=ft.Column(
                [
                    # make_card(
                    #     title="Category ID",
                    #     controls=[ft.Row(
                    #         [
                    #             ticketsCategoryField
                    #         ]
                    #     )]
                    # ),
                    make_card(
                        title="Field 1",
                        controls=[ft.Row(
                            [
                                field_1_switch,
                                field_1_title,
                                field_1_entry
                            ]
                        )]
                    ),

                    make_card(
                        title="Field 2",
                        controls=[ft.Row(
                            [
                                field_2_switch,
                                field_2_title,
                                field_2_entry,
                            ]
                        )]
                    ),  

                    make_card(
                        title="Field 3",
                        controls=[ft.Row(
                            [
                                field_3_switch,
                                field_3_title,
                                field_3_entry
                            ]
                        )]
                    ),

                    make_card(
                        title="Field 4",
                        controls=[ft.Row(
                            [
                                field_4_switch,
                                field_4_title,
                                field_4_entry
                            ]
                        )]
                    ),

                    make_card(
                        title="Field 5",
                        controls=[ft.Row(
                            [
                                field_5_switch,
                                field_5_title,
                                field_5_entry
                            ]
                        )]
                    ),           
                    make_card(
                        title="Embed Settings",
                        controls=[
                            ft.Row([
                                IA_Channel_Switch,
                                IA_Channel_Entry
                            ]),
                            ft.Row([
                                DMT_Channel_Switch,
                                DMT_Channel_Entry
                            ]),
                            ft.Row([
                                Media_Channel_Switch,
                                Media_Channel_Entry
                            ]),  
                            ft.Row([
                                MGMT_Channel_Switch,
                                MGMT_Channel_Entry
                            ]) ,
                            ft.Row([
                                LD_Channel_Switch,
                                LD_Channel_Entry
                            ])                                                                           
                        ]
                    )                                                           
                ]
            )
        )

        infract_card = ft.Container(
            visible=False,
            content=ft.Column(
                [
                    ft.Container(
                        content=ft.Row(
                            [
                                ft.Switch(
                                    label="Add Roles",
                                    value=False,
                                    on_change=infractValue,
                                ),
                                ft.Text(
                                    value="Add infraction roles when someone is infracted?"
                                )
                            ]
                        )
                    )
            
                ],
                spacing=15,
            ),
            bgcolor=PANEL,
            padding=22,
            border_radius=14,
            width=760,
        )

        embed_title = make_field(
            "Embed Title",
            hint="Enter embed title",
        )
        
        embed_description = ft.TextField(
            label="Embed Description",
            hint_text="Enter the message you want the bot to display",
            multiline=True,
            min_lines=4,
            max_lines=7,
            border_radius=10,
            border_color="#343D50",
            focused_border_color=ACCENT,
            bgcolor="#151A25",
        )

        embed_color = make_field(
            "Embed Color",
            hint="Example: #7289DA",
        )

        embed_image = make_field(
            "Embed Image URL",
            hint="https://example.com/image.png",
        )

        ticketLogging = make_field(
            "Ticket Log Channel ID",
            hint="Example: 123456789012345678",
            visible=False
        )

        commandSave = make_button(
            "Save Changes",
            on_click=changeConfig
        )
        variableText = ft.Text(
            "If you want to do something like session votes out of votes required, use these words.\n\n{SESSION_VOTES} {REQUIRED_VOTES} {INGAME_PLAYERS}", # TODO: add more variables later
            color=MUTED,
            size=12,
        ) 

        messageSettings = make_card("Message Settings", [
            variableText,
            embed_title,
            embed_description,
            
        ])

        embedAppearance = make_card("Embed Appearance", [
            embed_color,
        ])

        embedImages = make_card("Embed Images", [
            embed_image,
            ft.Text(
                "Enter an image URL from a place like File Garden",
                color=MUTED,
                size=12,
            ),
        ])

        content.controls = [
            ft.Text("Command Editor", size=30, weight="bold"),
            ft.Text(
                "Select a command and customize its message and embed.",
                color=MUTED,
            ),

            make_card("Select Command", [
                command_select,
                ft.Row([commandSave]),
            ]),

            messageSettings,

            infract_card,

            embedAppearance,

            embedImages,

            ticketLogging,

            tickets_card,

            command_card,

            buttonConfig
        ]

        page.update()

    def configPage():
        files = None

        async def handle_pick_files(e: ft.Event[ft.Button]):
            nonlocal files

            files = await ft.FilePicker().pick_files(
                allow_multiple=False,
                file_type=ft.FilePickerFileType.CUSTOM,
                allowed_extensions=["json"],
            )

        async def handle_save_file(e: ft.Event[ft.Button]):
            if files and files[0].path:
                picked_file = files[0]

                os.makedirs("configFolder", exist_ok=True)

                new_filename = "config.json"

                save_path = os.path.join("configFolder", new_filename)

                shutil.copy(picked_file.path, save_path)

                save_file_path.value = save_path

            save_file_path.update()
            
        content.controls = [

        
            ft.SafeArea(
                content=ft.Column(
                    controls=[
                        ft.Row(
                            controls=[
                                ft.Button(
                                    content="Pick files",
                                    icon=ft.Icons.UPLOAD_FILE,
                                    on_click=handle_pick_files,
                                ),
                                selected_files := ft.Text(),
                            ]
                        ),
                        ft.Row(
                            controls=[
                                ft.Button(
                                    content="Save file",
                                    icon=ft.Icons.SAVE,
                                    on_click=handle_save_file,
                                    disabled=page.web,  # disable this button in web mode
                                ),
                                save_file_path := ft.Text(),
                            ]
                        )
                    ],
                ),
            )
        ]
        page.update()

        
    def navigate(name):
        pages = {
            "Dashboard": dashboard,
            "ER:LC": erlc_settings,
            "Discord Token": discord_settings,
            "Commands": command_editor,
            "Configuration File": configPage
        }
        pages[name]()

    sidebar = ft.Container(
        width=225,
        bgcolor="#151A25",
        padding=18,
        content=ft.Column(
            [
                ft.Text(
                    "TESTING",
                    size=21,
                    weight="bold",
                    color=ACCENT,
                ),
                ft.Text(
                    "TESTING",
                    size=10,
                    color=MUTED,
                ),
                ft.Divider(color="#343D50"),

                ft.TextButton(
                    "Dashboard",
                    icon="dashboard",
                    on_click=lambda e: navigate("Dashboard"),
                ),
                ft.TextButton(
                    "ER:LC",
                    icon="gamepad",
                    on_click=lambda e: navigate("ER:LC"),
                ),
                ft.TextButton(
                    "Discord Token",
                    icon="smart_toy",
                    on_click=lambda e: navigate("Discord Token"),
                ),
                ft.TextButton(
                    "Commands",
                    icon="terminal",
                    on_click=lambda e: navigate("Commands"),
                ),

                ft.TextButton(
                    "Configuration File",
                    icon="terminal",
                    on_click=lambda e: navigate("Configuration File"),
                ),

                ft.Container(expand=True),

                ft.TextButton(
                    content=ft.Text(
                        discordServerLink, 
                        style=ft.TextStyle(
                            color=ft.Colors.BLUE, 
                            decoration=ft.TextDecoration.UNDERLINE
                        )
                    ),
                    action=ft.CopyToClipboard(discordServerLink),
                )
            ],
            spacing=12,
        ),
    )

    page.add(
        ft.Row(
            [
                sidebar,
                ft.Container(
                    content=content,
                    padding=28,
                    expand=True,
                ),
            ],
            expand=True,
            spacing=0,
        )
    )

    dashboard()

if __name__ == "__main__":
    ft.run(gui_main)
