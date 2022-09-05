from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

import random
import time

# Kahoot bot 2 Electric Boogaloo 
# A revamp of my kahoot bot using selenium library from september of 2019, its currently september of 2021
# now with better programming 

def main():

    lobbyID = str(input("Enter lobby number: "))

    while len(lobbyID) != 7:
        lobbyID = str(input("Re-enter: "))

    totalBotNumber = int(input("Enter number of bots: "))
    numberOfDigits = len(str(totalBotNumber))

    botName = str(input("Enter bot name: "))

    while (len(botName) + numberOfDigits > 15):
        botName = str(input("Please use a shorter name: "))

    host = Host(lobbyID,botName)

    updatedBotNumber = totalBotNumber
    for i in range(totalBotNumber ):
        print(f"Adding bot {i}...")
        if i != 0:
            host.driver.execute_script("window.open()") # open new tab
            host.driver.switch_to.window(host.driver.window_handles[i]) 
        if i < 6:
            joinSuccessful = host.join_game(botNumber=i, delay=False)
        else:
            print("Applying delay...")
            joinSuccessful = host.join_game(botNumber=i, delay=True)

        if joinSuccessful: # check if bot was able to join game
            pass
        else:
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
    while host.driver.current_url != "https://kahoot.it/v2/ranking": 
        host.wait_for_url_change()
        print("Answering question")
        time.sleep(1)
        availableButtons = host.remove_options()
        i = 0
        for bot in host.bots:
            if bot.joinSuccessful == True:
                host.driver.switch_to.window(host.driver.window_handles[i])
                host.answer_question(availableButtons)
            else:
                # ignore this tab since the bot has failed to join
                pass 
            i += 1

        host.wait_for_url_change()
        host.wait_for_url_change()

    # shutdown 
    print("Game has ended")
    input("End program: ")
    print("Terminating bots... ")
    host.driver.quit()

    for bot in host.bots:
        del bot

    del host


class Bot(): # custom datatype for different traits such as their join status or if they're a leader
    # webdriver shit is still done by Host()
    def __init__(self, name, score, joinSuccessful):
        self.name = name
        self.score = score
        self.joinSuccessful = joinSuccessful 

class Host():  # control bot for all player bots under it
    def __init__(self, lobbyID, botName):
        self.lobbyID = lobbyID
        self.botName = botName 
        try:
            self.driver = webdriver.Firefox() # webdriver to automatically control web browser
        except AttributeError: # web driver is not in path
            raise AttributeError("Program dun goofed. Add webdriver to path dipshit")
        self.bots = [] # all bots currently in existence

    def join_game(self, botNumber, delay):
        # create a bot and send it to a kahoot lobby
        # create bot
        numberedBotName = self.botName + str(botNumber) # original bot name with its number attached to it
        bot = Bot(numberedBotName, 0, joinSuccessful=False)

        joinSuccessful = False
        self.driver.get("https://kahoot.it/")

        try:
            # delay workaround since kahoot blocks bots
            # the blocks seem to be timer based 
            # refreshing the page to create a brief pause seems to be the quickest way to bypass this
            workaroundDelay = 0.5
            if delay == True:
                self.driver.refresh()
                time.sleep(workaroundDelay)
            # while this workaround does prevent most bots from being blocked
            # rate of bot joining reduces slightly and on average 2 bots will fail to join since the join cooldown time appears to fluctuate randomly

            # enter lobby ID
            WebDriverWait(self.driver, 3).until(EC.element_to_be_clickable((By.ID, "game-input")))
            gamePinTextBox = self.driver.find_element_by_id("game-input")
            gamePinTextBox.send_keys(self.lobbyID + Keys.ENTER)

            # enter name
            WebDriverWait(self.driver, 3).until(EC.element_to_be_clickable((By.ID, "nickname")))
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
        buttonIDPresent = ["triangle-button", "diamond-button", "circle-button", "square-button"]
        tmp = ["triangle-button", "diamond-button", "circle-button", "square-button"]

        for id in buttonIDPresent:
            try:
                self.driver.find_element_by_id(id)
            except NoSuchElementException:
                tmp.remove(id)
        
        buttonIDPresent = tmp
        return buttonIDPresent

    def answer_question(self, availableAnswers):
        # gets a bot to select an answer from a kahoot question
        
        button = random.randint(0, len(availableAnswers) - 1)
        availableAnswers = list(availableAnswers)
        print(f"Answering")
        try:
            WebDriverWait(self.driver, 1.5).until(EC.element_to_be_clickable((By.ID, availableAnswers[button])))
            button = self.driver.find_element_by_id(availableAnswers[button])
            button.click() 
        except TimeoutException:
            print("Failed to answer")

    def wait_for_url_change(self):
        # pause until the page changes to a new url
        # i.e wait for the lobby screen to change to the block selection screen
        currentURL = self.driver.current_url
        while currentURL == self.driver.current_url:
            pass


if __name__ == "__main__":
    main()