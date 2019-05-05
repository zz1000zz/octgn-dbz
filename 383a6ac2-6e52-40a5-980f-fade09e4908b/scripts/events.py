####################################################
#  events.py
# This script contains event handler functions for
# the events listed in the game definition.
####################################################

import re
import collections
import time

# boardInit
# Trigger: OnTableLoaded (whenever the game is loaded for the
# first time)
# Arguments: None
# Sets the default value (disabled) for automationEnabled
def boardInit():
    setGlobalVariable("automationEnabled", "False")
    whisper("Press Ctrl+A to enable Game Setup Automation for both players.")
    whisper("This automation will play your MP and Mastery (face down) to the table when your deck is loaded.")
    whisper("When both players have loaded a deck, cards will turn face up, decks will be shuffled, and the first player will be randomly decided.")
    whisper("Press Ctrl+Z to disable Game Setup Automation once enabled.")

# gameInit
# Trigger: OnGameStarted (whenever the game is loaded or reset)
# Arguments: None
# Sets the number of loaded decks to 0
def gameInit():
    setGlobalVariable("numLoadedDecks", "0")

# loadDeck
# Trigger: OnDeckLoaded
# Arguments:
#   args: {
#         player: (Player) player that loaded a deck
#         groups: (list<Group>) List of groups to which cards were added
#       }
# When a deck is loaded, search "Starting" for the player's Mastery and
# Level 1 MP, and move those two cards to the table face-down.
# If the other player has already loaded their deck, both players
# call "gameSetup" and then the first player is determined.
# This functionality can be opted out of by disabling Game Setup
# Automation.
def loadDeck(args):
    mute()
    if not eval(getGlobalVariable("automationEnabled")):
        return
    if not me.isInverted:
        mp_x_offset = HostPlayerMP_x_Offset
        mp_y_offset = HostPlayerMP_y_Offset
        mastery_x_offset = HostPlayerMastery_x_Offset
        mastery_y_offset = HostPlayerMastery_y_Offset
    else:
        mp_x_offset = GuestPlayerMP_x_Offset
        mp_y_offset = GuestPlayerMP_y_Offset
        mastery_x_offset = GuestPlayerMastery_x_Offset
        mastery_y_offset = GuestPlayerMastery_y_Offset

    if args.player == me:
        setGlobalVariable("numLoadedDecks", str( 1 + eval(getGlobalVariable("numLoadedDecks")) ) )
        args.player.setGlobalVariable("maxHandSize", 1)
        for card in args.player.piles["Starting"]:
            if card.Type == "Mastery":
                card.moveToTable(mastery_x_offset, mastery_y_offset, True)
            elif card.properties["Card Level"] == "1":
                card.moveToTable(mp_x_offset, mp_y_offset, True)
        if eval(getGlobalVariable("numLoadedDecks")) > 1:
            gameSetup()
            remoteCall(players[1], "gameSetup", [])
            update()
            determineFirstPlayer()

# handlePhase
# Trigger: OnPhasePassed
# Arguments:
#   args: {
#         name: str(<name of the previous phase>),
#         id: int(<index of the previous phase>),
#         force: bool(<skip player-defined stops>)
#       }
# Special Note: This is called when _exiting_ a phase,
# not when entering it.
# This handler is called by both players, so only the
# Active Player should perform any functions.
# Calls the appropriate "Manage*Phase" function.
def handlePhase(args):
    currentPhaseIndex = args.id + 1
    if(getActivePlayer() == me):
        if currentPhaseIndex == 1:
            manageDrawPhase()
        elif currentPhaseIndex == 2:
            managePlanningPhase()
        elif currentPhaseIndex == 3:
            managePowerUpPhase()
        #elif currentPhaseIndex == 4:
        #elif currentPhaseIndex == 5:
        #elif currentPhaseIndex == 6:
        elif currentPhaseIndex == 7:
            manageRejuvenatePhase()