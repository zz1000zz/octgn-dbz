####################################################
#  actions.py
# This script contains functions that are invoked
# directly by the player. For example, menu options
# double clicking cards,and hotkeys
####################################################

import re

def untapAll(group, x = 0, y = 0):
	mute()
	notify("{} untaps all his cards".format(me))
	for card in group: 
		if card.controller == me:
			card.orientation &= ~Rot90			
			
def clearAll(group, x = 0, y= 0):
    notify("{} clears all targets and combat.".format(me))
    for card in group:
		if card.controller == me:
			card.target(False)
			card.highlight = None

def roll20(group, x = 0, y = 0):
    mute()
    n = rnd(1, 20)
    notify("{} rolls {} on a 20-sided die.".format(me, n))

def flipCoin(group, x = 0, y = 0):
    mute()
    n = rnd(1, 2)
    if n == 1:
        notify("{} flips heads.".format(me))
    else:
        notify("{} flips tails.".format(me))

def powerUp(group, x = 0, y = 0):
        mute()
        personalitiesInTable = [c for c in table if c.controller == me]
        for card in personalitiesInTable:
                if re.search(r'Hero', card.type) or re.search(r'Villain', card.type) or re.search(r'Personality', card.type) or re.search(r'Ally', card.type):
                        try:
                                card.markers[CounterMarker] += int(card.PUR)
                                if card.markers[CounterMarker] > 10:
                                        card.markers[CounterMarker] = 10
                        except:
                                pass
        notify("{} powers up their personalities".format(me.name))

def tap(card, x = 0, y = 0):
    mute()
    card.orientation ^= Rot90
    if card.orientation & Rot90 == Rot90:
		notify('{} taps {}'.format(me, card))
    else:
        notify('{} untaps {}'.format(me, card))
		  
def flip(card, x = 0, y = 0):
    mute()
    if card.isFaceUp:
        notify("{} turns {} face down.".format(me, card))
        card.isFaceUp = False
    else:
        card.isFaceUp = True
        notify("{} turns {} face up.".format(me, card))

def faceUpAll():
    mute()
    for c in table:
        if c.controller == me:
            c.isFaceUp = True

def discard(card, x = 0, y = 0):
	card.moveTo(me.piles['Discard Pile'])
	notify("{} discards {}".format(me, card))

def banishTop(group, x = 0, y = 0):
	card = group.top()
	card.moveTo(me.piles['Removed from game'])
	notify("{} banishes {} from the top of their discard pile.".format(me, card))
	
def banishBottom(group, x = 0, y = 0):
	card = group.bottom()
	card.moveTo(me.piles['Removed from game'])
	notify("{} banishes {} from the bottom of their discard pile.".format(me, card))

def addCounter(card, x = 0, y = 0):
	mute()
	notify("{} adds 1 counter to {}.".format(me, card))
	card.markers[CounterMarker] += 1

def removeCounter(card, x = 0 , y = 0):
	mute()
	notify("{} removes 1 counter to {}.".format(me, card))
	card.markers[CounterMarker] -= 1
	  
def setCounter(card, x = 0, y = 0):
	mute()
	quantity = askInteger("How many counters", 0)
	notify("{} sets {} counters on {}.".format(me, quantity, card))
	card.markers[CounterMarker] = quantity

def takeDamage(card, x = 0, y = 0):
    mute()
    manageDamage(card)

def takeUnpreventableDamage(card, x = 0, y = 0):
    mute()
    manageDamage(card, True, False)

def takeBanishedDamage(card, x = 0, y = 0):
    mute()
    manageDamage(card, False, True)

def takeUnpreventableBanishedDamage(card, x = 0, y = 0):
    mute()
    manageDamage(card, True, True)
		
def play(card, x = 0, y = 0):
    mute()
    src = card.group
    if not me.isInverted:
        cardPlayed_x_offset = HostPlayerCardPlayed_x_Offset
        cardPlayed_y_offset = HostPlayerCardPlayed_y_Offset
    else:
        cardPlayed_x_offset = GuestPlayerCardPlayed_x_Offset
        cardPlayed_y_offset = GuestPlayerCardPlayed_y_Offset
    card.moveToTable(cardPlayed_x_offset, cardPlayed_y_offset)
    notify("{} plays {} from their {}.".format(me, card, src.name))
    # When playing allies, automatically start at 3 stages
    if "Ally" in card.type:
        card.markers[CounterMarker] = 3

def mulligan(group):
    mute()
    newCount = len(group) - 1
    if newCount < 0: return
    if not confirm("Mulligan down to %i ?" % newCount): return
    notify("{} mulligans down to {}".format(me, newCount))
    librarycount = len(me.piles["Life Deck"])
    for card in group:
        n = rnd(0, librarycount)
        card.moveTo(me.piles["Life Deck"], n)
    me.piles["Life Deck"].shuffle()
    for card in me.piles["Life Deck"].top(newCount):
        card.moveTo(me.hand)

def randomDiscard(group):
	mute()
	card = group.random()
	if card == None: return
	notify("{} randomly discards {}.".format(me,card.name))
	card.moveTo(me.piles['Discard Pile'])

def draw(group, x = 0, y = 0):
	if len(group) == 0: return
	mute()
	group[0].moveTo(me.hand)
	notify("{} draws a card.".format(me))

def drawMany(group, count = None):
	if len(group) == 0: return
	mute()
	if count == None: count = askInteger("Draw how many cards?", 0)
	for card in group.top(count): card.moveTo(me.hand)
	notify("{} draws {} cards.".format(me, count))

def rejuvenateOne(*args):
        card = me.piles["Discard Pile"].top()
        rejuvenate(card)

def rejuvenateMany(*args):
    count = askInteger("Rejuvenate how many cards?", 0)
    if count > 0:
        cards = [card for card in me.piles["Discard Pile"].top(count)]
        rejuvenate(cards)

def drawThree():
    mute()
    for card in me.piles["Life Deck"].top(3): card.moveTo(me.hand)
    notify("{} draws 3 cards.".format(me))

def drawBottom(group, x = 0, y = 0):
	if len(group) == 0: return
	mute()
	group.bottom().moveTo(me.hand)
	notify("{} draws a card from the bottom.".format(me))

def shuffle(group):
	group.shuffle()
  
#---------------------------------------------------------------------------
# Phases
#---------------------------------------------------------------------------

# nextPhase
# Invoked by the Active Player by pressing Ctrl+Enter
# Increments the phase counter using setPhase
# Exceptions:
#  - If the current phase is the final phase of the turn,
#    pass the turn to the opponent
#  - TODO: If the current phase is the discard step and
#    players have too many cards in hand, do not allow
#    progression to the next phase
def nextPhase(group = table, x = 0, y = 0): 
   mute()
   phase = currentPhase()
   #if phase[1] == 6 and not enforceHandLimits():
       #return
   if phase[1] == 7: 
      nextTurn(findOpponent())
      return  
   else:
    setPhase(phase[1]+1)

def showCurrentPhase(phaseNR = None): # Just say a nice notification about which phase you're on.
   if phaseNR: notify(phases[phaseNR])
   else: notify(phases[num(me.getGlobalVariable('phase'))])

def endMyTurn(opponent = None):
   if not opponent: opponent = findOpponent()
   me.setGlobalVariable('phase','0') # In case we're on the last phase (Force), we end our turn.
   notify("=== {} has ended their turn ===.".format(me))
   opponent.setActivePlayer() 

#---------------------------------------------------------------------------
# Automation Management Functions
#---------------------------------------------------------------------------

def enableSetupAutomation(group = table, x = 0, y = 0):
    setGlobalVariable("automationEnabled", "True")
    notify("Game Setup Automation enabled for both players.")

def disableSetupAutomation(group = table, x = 0, y = 0):
    setGlobalVariable("automationEnabled", "False")
    notify("Game Setup Automation disabled for both players.")

#---------------------------------------------------------------------------
# Meta Functions
#---------------------------------------------------------------------------
def findOpponent(position = '0', multiText = "Choose which opponent you're targeting with this effect."):
   opponentList = fetchAllOpponents()
   if len(opponentList) == 1: opponentPL = opponentList[0]
   else:
      if position == 'Ask':
         choice = SingleChoice(multiText, [pl.name for pl in opponentList])
         opponentPL = opponentList[choice]         
      else: opponentPL = opponentList[num(position)]
   return opponentPL

def fetchAllOpponents(targetPL = me):
   opponentList = []
   if len(getPlayers()) > 1:
      for player in getPlayers():
         if player != targetPL: opponentList.append(player) # Opponent needs to be not us, and of a different type. 
   else: opponentList = [me] # For debug purposes
   return opponentList   

def playerside():
   if me.hasInvertedTable(): side = -1
   else: side = 1   
   return side
   
 
#------------------------------------------------------------------------------
# Button and Announcement functions
#------------------------------------------------------------------------------

def BUTTON_OK(group = None,x=0,y=0):
   notify("--- {} has no further reactions.".format(me))

def BUTTON_Wait(group = None,x=0,y=0):  
   notify("--- Wait! {} wants to react.".format(me))

def BUTTON_Actions(group = None,x=0,y=0):  
   notify("--- {} is waiting for opposing actions.".format(me))

def declarePass(group, x=0, y=0):
   notify("--- {} Passes".format(me))    

def useCard(card,x=0,y=0):
   if card.Type == 'Button': # The Special button cards.
      if card.name == 'Wait!': BUTTON_Wait()
      elif card.name == 'Actions?': BUTTON_Actions()
      else: BUTTON_OK()
      return
   else: tap(card,x,y)
