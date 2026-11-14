import asyncio
import multiprocessing
import flet as ft
from gui import gui_main
from paths import get_data_path
import botMain
import json
import requests
from pathlib import Path
import time
import data_sender
import math
from datetime import datetime, timezone

# TODO: add Mass RDM detection 3 kills in 20 second

RunAPI = False
BASE_DIR = Path(__file__).resolve().parent
configFile = BASE_DIR / "configuration.json"

with open(configFile, "r", encoding="utf-8") as file:
    configContent = json.load(file)

erlc_command_url = "https://api.erlc.gg/v2/server/command"
erlc_get_data_url = "https://api.erlc.gg/v2/server?Players=true&Queue=true&KillLogs=true&CommandLogs=true&ModCalls=true"

cfg = {}

with open(configFile, "r", encoding="utf-8") as f:
    cfg = json.load(f)

def handle_data(data):
    if "ingame_command" in data:
        command = data["ingame_command"]
        print(runIngameCommand(command))
    if "TicketNumber" in data:
        configContent["Ticket_Number"] = data["TicketNumber"]
        print(str(configContent["Ticket_Number"]) + " " + str(data))
        with open(configFile, "w") as f:
            json.dump(configContent, f, indent=4)



playerTracking = {}
oldTime = time.perf_counter()
hasFirstCheatLoopRan = False
async def processIngameInfo():
    counter = 0
    global RunAPI
    while RunAPI:
        newTime = time.perf_counter()
        await asyncio.sleep(0.1)
        global ERLC_Info
        ERLC_Info = await getIngameInfo()
        data_sender.botDataSender({"ERLC_Info": ERLC_Info})
       
        await asyncio.sleep(10)


        # for player in ERLC_Info["IngameInfo"]["Players"]: # TODO: try this anti cheat later
        #     playerID = player["Player"]

        #     newPointX = player["Location"]["LocationX"]
        #     newPointZ = player["Location"]["LocationZ"]
        #     newTime = time.time()

        #     if playerID not in playerTracking:
        #         playerTracking[playerID] = {
        #             "oldPointX": newPointX,
        #             "oldPointZ": newPointZ,
        #             "oldTime": newTime
        #         }
        #         continue

        #     oldData = playerTracking[playerID]

        #     distanceTravelled = math.dist(
        #         (newPointX, newPointZ),
        #         (oldData["oldPointX"], oldData["oldPointZ"])
        #     )

        #     timeDifference = newTime - oldData["oldTime"]

        #     if timeDifference > 0:
        #         studsPerSecond = distanceTravelled / timeDifference
        #         MPH = studsPerSecond * 0.28 * 3600 / 1609.344

        #         print(f"{playerID}: {MPH:.2f} MPH")
        #         print(f"{newPointX} {newPointZ}")

        #     playerTracking[playerID] = {
        #         "oldPointX": newPointX,
        #         "oldPointZ": newPointZ,
        #         "oldTime": newTime
        #     }


data_sender.data_callback = handle_data

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
    response = requests.post(erlc_command_url, json=payload, headers=headers)
    print(response.text)
    cfg["ERLC_Status"] = str(response.text)
    with open(configFile, "w") as file:
        json.dump(cfg, file, indent=4)
    return response


async def getIngameInfo():
    headers = {"server-key": str(cfg["ERLC_API_KEY"])}

    response = requests.get(erlc_get_data_url, headers=headers)

    
    reset_timestamp = int(response.headers["X-RateLimit-Reset"])

    remaining = reset_timestamp - datetime.now(timezone.utc).timestamp()

    minutes, seconds = divmod(int(remaining), 60)
    hours, minutes = divmod(minutes, 60)
    minutesRemaining = (hours * 60) + minutes + (seconds / 60)
    if int(response.headers["X-RateLimit-Remaining"]) <= 1:
        await asyncio.sleep(minutesRemaining + 0.05)
    print(response)
    return {
        "MinutesLeft": minutesRemaining,
        "AttemptsLeft": response.headers["X-RateLimit-Remaining"],
        "IngameInfo": response.json(),
        "response": response
    }



hasCommandLoopStarted = False

async def main(page: ft.Page):
    await gui_main(page, handle_action)

    global RunAPI
    RunAPI = False
    runBot = None
    async def handle_action(command: str):
        nonlocal runBot
        runningAPI = None

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

            elif command == "StartAPI":
                global RunAPI
                RunAPI = True
                if not hasCommandLoopStarted:
                    runningAPI = asyncio.create_task(processIngameInfo())
                    hasCommandLoopStarted = True

            elif command == "StopAPI":
                RunAPI = False
                print("button pressed stop")
                if runningAPI is not None:
                    print("cancel")
                    runningAPI.cancel()
                    runningAPI = None
                hasCommandLoopStarted = False



        
    

if __name__ == "__main__":
    multiprocessing.freeze_support()
    ft.run(main)
