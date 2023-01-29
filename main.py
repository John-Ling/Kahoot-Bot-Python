from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

import random
import time
import sys
import re
# Kahoot bot 2 Electric Boogaloo
# A revamp of my kahoot bot using selenium library from september of 2019, its currently september of 2021
# now with better programming


def main():
    if len(sys.argv) < 4:
        print("Please provide 3 arguments: Lobby ID, Bot Name, Number of Bots")
        quit()

    lobbyID = str(sys.argv[1])

    if len(lobbyID) > 7 or re.search("[^A-Za-z0-9]", lobbyID): # check if id is not exclusively alphanumeric characters and right length
        print("Lobby ID must be 7 or fewer characters containing only numbers and letters")
        quit()

    botName = str(sys.argv[2])

    totalBotNumber = int(sys.argv[3])
    numberOfDigits = len(str(totalBotNumber))

    while (len(botName) + numberOfDigits > 15):
        print(f"Bot name should be under 13 characters")
        quit()

    host = Host(lobbyID, botName)

    updatedBotNumber = totalBotNumber
    for i in range(totalBotNumber):
        print(f"Adding bot {i}...")
        if i > 0:
            host.driver.execute_script("window.open()")  # open new tab
            host.driver.switch_to.window(host.driver.window_handles[i])
        if i < 6:
            joinSuccessful = host.join_game(botNumber=i, delay=False)
        else:
            print("Applying delay...")
            joinSuccessful = host.join_game(botNumber=i, delay=True)

        if not joinSuccessful:  # check if bot was able to join game
            updatedBotNumber -= 1

    # update total number of bots
    totalBotNumber = updatedBotNumber
    print(f"Total number of bots is {totalBotNumber}")
    time.sleep(3)
    # wait until game starts
    print("Waiting for game to begin...")
    host.wait_for_url_change()
    print("Game has started")
    host.wait_for_url_change()

    # answer kahoot question of quiz until game ends
    END_URL = "https://kahoot.it/v2/ranking"
    while host.driver.current_url != END_URL:
        host.wait_for_url_change()
        print("Answering question")
        time.sleep(1)
        availableButtons = host.remove_options()
        for i in range (len(host.bots)):
            bot = host.bots[i]
            if bot.joinSuccessful == True:
                host.driver.switch_to.window(host.driver.window_handles[i])
                host.answer_question(availableButtons)

        host.wait_for_url_change()
        host.wait_for_url_change()

    # shutdown
    print("Game has ended")
    input("End program? ")
    print("Terminating bots... ")
    host.driver.quit()

    for bot in host.bots:
        del bot

    del host


class Bot():  # custom datatype for different traits such as their join status
    def __init__(self, name, joinSuccessful):
        self.name = name
        self.joinSuccessful = joinSuccessful


class Host():  # control bot for all player bots under it
    def __init__(self, lobbyID, botName):
        self.lobbyID = lobbyID
        self.botName = botName
        try:
            # webdriver to automatically control web browser
            self.driver = webdriver.Firefox()
        except AttributeError:  # web driver is not in path
            raise AttributeError("Attribute Error: Add webdriver to path")
        self.bots = []  # all bots currently in existence

    def join_game(self, botNumber, delay):
        # create a bot and send it to a kahoot lobby
        # create bot
        # original bot name with its number attached to it
        KAHOOT_URL = "https://kahoot.it/"

        numberedBotName = self.botName + str(botNumber)
        bot = Bot(name=numberedBotName, joinSuccessful=False)

        joinSuccessful = False
        self.driver.get(KAHOOT_URL)

        try:
            # delay workaround since kahoot blocks bots
            # the blocks seem to be timer based
            # refreshing the page to create a brief pause seems to be the quickest way to bypass this
            WORKAROUND_DELAY = 0.5
            if delay:
                self.driver.refresh()
                time.sleep(WORKAROUND_DELAY)
            # while this workaround does prevent most bots from being blocked
            # rate of bot joining reduces slightly and on average 2 bots will fail to join since the join cooldown time appears to fluctuate randomly

            # enter lobby ID
            WebDriverWait(self.driver, 3).until(
                EC.element_to_be_clickable((By.ID, "game-input")))
            gamePinTextBox = self.driver.find_element_by_id("game-input")
            gamePinTextBox.send_keys(self.lobbyID + Keys.ENTER)

            # enter name
            WebDriverWait(self.driver, 3).until(
                EC.element_to_be_clickable((By.ID, "nickname")))
            nicknameTextBox = self.driver.find_element_by_id("nickname")
            nicknameTextBox.send_keys(numberedBotName + Keys.ENTER)

            joinSuccessful = True
            bot.joinSuccessful = True
        except TimeoutException:
            print(f"Bot {botNumber} has failed to join game")

        self.bots.append(bot)
        return joinSuccessful

    def remove_options(self):
        # remove buttons that are not present in the question (such as a true or false question with only two options)
        # this is done by searching for their html class names and discarding them if not found
        buttonClasses = ["fFONXg", 
                        "hZGSQg", 
                        "cckBYR", 
                        "epOaBR"]

        tmp = ["fFONXg", 
                "hZGSQg", 
                "cckBYR", 
                "epOaBR"]

        for className in buttonClasses:
            try:
                self.driver.find_element_by_class_name(className)
            except NoSuchElementException:
                tmp.remove(className)

        buttonClasses = tmp
        return buttonClasses

    def answer_question(self, availableAnswers):
        # gets a bot to select an answer from a kahoot question
        print(len(availableAnswers) - 1)
        button = random.randint(0, len(availableAnswers) - 1)
        availableAnswers = list(availableAnswers)
        print(f"Answering")
        try:
            WebDriverWait(self.driver, 1.5).until(EC.element_to_be_clickable((By.CLASS_NAME, availableAnswers[button])))
            button = self.driver.find_element_by_class_name(availableAnswers[button])
            button.click()
        except TimeoutException:
            print("Failed to answer")

    def wait_for_url_change(self):
        # pause until the page changes to a new url
        # i.e wait for the lobby screen to change to the block selection screen
        currentURL = self.driver.current_url
        while currentURL == self.driver.current_url: pass


if __name__ == "__main__":
    main()
