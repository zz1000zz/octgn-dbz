####################################################
#  engine.py
# This script contains functions that manage the DBZ
# game engine.
####################################################


import re

# ===================
# Game Intialization
# ===================

# gameSetup 
# This function prepares the game for the first turn.
# It should be called on behalf of each player.
# Invokes 'faceUpAll' to turn MP/Mastery face up.
# Shuffles the player's Life Deck
# Searches the table for the player's MP and sets its
# power stage to 5 above 0.
def gameSetup():
    faceUpAll()
    me.piles["Life Deck"].shuffle()
    notify("{} shuffles their Life Deck.", me)
    for c in table:
        if c.controller == me and c.properties["Card Level"] is not "":
            c.markers[CounterMarker] = 5

# determineFirstPlayer
# This function should be called on behalf of one player.
# Randomly determine which player will have the option
# of going first, and present the choice to that player.
# TODO: Add "Before the first turn" effects (Currently
# just Saiyan Dynamic Mastery)
def determineFirstPlayer():
    n = rnd(0, 1)
    notify("OCTGN randomly determined {} will choose which player takes the first turn".format(players[n]))
    if players[n] == me:
        chooseFirstPlayer()
    else:
        remoteCall(findOpponent(), "chooseFirstPlayer", [])

# chooseFirstPlayer
# Only called by determineFirstPlayer
# Manages the choice for which player takes the first
# turn and sets the Active Player appropriately
def chooseFirstPlayer():
    choices = [me.name, findOpponent().name]
    choice = askChoice("Choose first player", choices)
    if choice == 2:
        setActivePlayer(findOpponent())
    else:
        setActivePlayer(me)

# ==========================
# End Game Initialization
# ==========================


# =================
# Phase Management
# =================

# manageDrawPhase
# Only called by the handlePhase event handler.
# Initializes any player variables for the current turn.
# Calls the "drawThree" action to Draw 3 cards.
# Automatically advances to the Planning Step.
# TODO:
#  - Update the OnTurnPassed event handler to automatically enter this phase
#  - Add any "Start of Turn" triggers
#  - Add any "when cards are drawn" trigger handlers
def manageDrawPhase():
    # TODO: Add Any Start of Turn triggers here
    me.setGlobalVariable("combatDeclared", "False")
    drawThree()
    nextPhase()

# managePlanningPhase
# Allow the Player to Play planning step cards. Make sure they know
# how to invoke the PowerUp function and how to end their planning step.
def managePlanningPhase():
    whisper("Play Setups, Drills, Allies, or Dragon Balls.")
    whisper("Press Ctrl+P to Power Up your personalities. This function does not currently manage active PUR modifiers.")
    whisper("Press Ctrl+Enter to end your Planning Step and Declare/Skip Combat (you will not be able to inspect piles while the dialog is open).")

# managePowerUpPhase
# Manage Combat Declaration and enter the appropriate phase if combat
# was declared or skipped.
# TODO: 
#   - Call the powerUp function automatically (when it can manage PUR modifiers)
#   - Rebrand the phase in the game definition from "Declare" to "Power Up"
def managePowerUpPhase():
    #powerUp(None)
    choices = ['Declare Combat', 'Skip Combat']
    choice = askChoice("Declare Phase", choices)
    if choice == 1:
        me.setGlobalVariable("combatDeclared", "True")
        setPhase(4) # Jump to entering combat phase
    else:
        setPhase(6) # Jump to Discard phase

# enforceHandLimits
# Checks each player's hand size against their maximum hand size
# Returns False if hand sizes would block moving out of the discard step.
# TODO: Account for cases where maxHandSize is greater than 1. Until then, always return True
def enforceHandLimits():
    # Until all ways a player's hand limit can be modified are accounted for, we must trust the players
    return True
    
    if len(me.hand) > me.getGlobalVariable("maxHandSize") or len(findOpponent().hand) > findOpponent().getGlobalVariable("maxHandSize"):
        return False
    return True

# manageRejuvenatePhase
# If combat was not declared this turn, present the option to
# rejuvenate 1.
# TODO:
#   - Add trigger window for "Start of Rejuvenation Step"
#   - Add triggers for "when cards are Rejuvenated"
#   - Automatically move to the next phase (turn)
def manageRejuvenatePhase():
    if not eval(me.getGlobalVariable("combatDeclared")):
        whisper("Combat was not declared this turn. You may Rejuvenate 1.")
        choices = ['Rejuvenate', 'Decline']
        choice = askChoice("Rejuvenate 1?", choices)
        if choice == 1:
            rejuvenateOne()
    # Can't automatically go to the next phase until effects like Popo are handled
    #nextPhase()

# ==========================
# End Phase Management
# ==========================



# rejuvenate
# Arguments:
#   count: (int) The number of cards to Rejuvenate
# Moves <count> cards from the top of a player's discard piles
# to the bottom of their Life Deck.
# TODO:
#   - Look at cards to be rejuvenated at trigger any "when rejuvenated" effects.
#   - Look for effects that prevent or modify rejuvenation and make sure they are applied.
def rejuvenate(cards = [], silent = False):
    mute()
    if not isinstance(cards, list):
        cards = [cards]
    if silent == False:
        formattedCards = [format(card) for card in cards]
        notify('{} rejuvenates {}.'.format(me, ', '.join(formattedCards)))
    for card in cards:
        card.moveToBottom(me.piles["Life Deck"])

def lookupAttackTable(group, x = 0, y = 0):
    mute()
    defenderPL = remoteCall(players[1], "lookupPowerLevel", [group, x, y])
    attackerPL = lookupPowerLevel(group, x, y)
    update()
    return calculateAT(me.getGlobalVariable("powerLevel"), players[1].getGlobalVariable("powerLevel"))

def calculateAT(attackerPL, defenderPL):
    mute()
    attackerBase = 1 + getBaseAT(int(attackerPL.replace(',','')))
    defenderBase = getBaseAT(int(defenderPL.replace(',','')))
    if defenderBase > attackerBase:
        return 0
    return attackerBase - defenderBase

def getBaseAT(p):
    mute()
    thresholds = [1000, 10000, 100000, 500000, 1500000]
    base = 0
    for threshold in thresholds:
        if p >= threshold:
            base += 1
    return base

def lookupPowerLevel(group, x = 0, y = 0):
    mute()
    personalitiesInTable = [c for c in table if c.controller == me]
    for card in personalitiesInTable:
        if re.search(r'Hero', card.type) or re.search(r'Villain', card.type) or re.search(r'Personality', card.type) or re.search(r'Ally', card.type):
            try:
                me.setGlobalVariable("powerLevel", card.properties["Power Rating"].split(";")[card.markers[CounterMarker]])
            except:
                pass
