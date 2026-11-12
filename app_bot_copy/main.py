import asyncio
import multiprocessing
import flet as ft
from gui import gui_main
from paths import get_data_path
import botMain
import sys
from botMain import botDataSender
import json
import requests
from pathlib import Path
import time
BASE_DIR = Path(__file__).resolve().parent
configFile = BASE_DIR / "configuration.json"

with open(configFile, "r", encoding="utf-8") as file:
    configContent = json.load(file)

erlc_url = "https://api.erlc.gg/v2/server/command"
cfg = {}

with open(configFile, "r", encoding="utf-8") as f:
    cfg = json.load(f)

def handle_discord_command(data):
    if "ingame_command" in data:
        command = data["ingame_command"]
        print(runIngameCommand(command))
    if "TicketNumber" in data:
        configContent["Ticket_Number"] = data["TicketNumber"]
        print(str(configContent["Ticket_Number"]) + " " + str(data))
        with open(configFile, "w") as f:
            json.dump(configContent, f, indent=4)
        
        

botMain.data_callback = handle_discord_command

def start_bot_process():

    try:
        botMain.bot.run(cfg["TOKEN"])
    except Exception as e:
        cfg["Bot_Status"] = str(e)
        with open(configFile, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=4)

ERLC_Status = None

def runIngameCommand(command):
    payload = {"command": command}
    headers = {
        "server-key": str(cfg["ERLC_API_KEY"]),
        "Content-Type": "application/json"
    }
    response = requests.post(erlc_url, json=payload, headers=headers)
    print(response.text)
    cfg["ERLC_Status"] = str(response.text)
    with open(configFile, "w") as file:
        json.dump(cfg, file, indent=4)
    return response

async def main(page: ft.Page):
    runBot = None

    async def handle_action(command: str):
        nonlocal runBot

        if command == "RunBot":
            with open(configFile, "r", encoding="utf-8") as file:
                cfg = json.load(file)
                file.seek(0)
            with open(configFile, "w", encoding="utf-8") as file:
                json.dump(cfg, file, indent=4)

            if runBot is None or not runBot.is_alive():
                runBot = multiprocessing.Process(target=start_bot_process, daemon=True)
                runBot.start()

        
        elif command == "StopBot":
            if runBot is not None and runBot.is_alive():
                runBot.terminate()
                runBot.join()
                runBot = None
                with open(configFile, "r", encoding="utf-8") as file:
                    cfg = json.load(file)
                    cfg["Bot_Status"] = "Offline"
                    file.seek(0)
                with open(configFile, "w", encoding="utf-8") as file:
                    json.dump(cfg, file, indent=4)



        
    await gui_main(page, handle_action)

if __name__ == "__main__":
    multiprocessing.freeze_support()
    ft.run(main)
