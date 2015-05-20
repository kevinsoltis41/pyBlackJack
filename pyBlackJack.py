
import random
import os
import sys
import pygame
from pygame.locals import *
pygame.font.init()
pygame.mixer.init()

screen = pygame.display.set_mode((1200, 700))
clock = pygame.time.Clock()

#####       Function that will load image based on name and our Image folder.
def loadImage(name):
    fullname = os.path.join('images', name)
    image = pygame.image.load(fullname)
    image = image.convert()
    
    return image, image.get_rect()
        
#####       Display Text
def display(font, sentence):
    displayFont = pygame.font.Font.render(font, sentence, 1, (255,255,255), (0,0,0)) 
    return displayFont

def mainGame():

    #####       When User's busts...
    def gameOver():
        while True:
            for event in pygame.event.get():
                if (event.type == QUIT):
                    sys.exit()
                if (event.type == KEYDOWN and event.key == K_ESCAPE):
                    sys.exit()

            # Fill the screen with black
            screen.fill((0,0,0))
            
            # Render "Game Over" sentence on the screen
            oFont = pygame.font.Font(None, 50)
            displayFont = pygame.font.Font.render(oFont, "Game over! You have ran out of cash!", 1, (255,255,255), (0,0,0)) 
            screen.blit(displayFont, (125, 220))
            
            # Update the display
            pygame.display.flip()

    #####       Using Randoms shuffle default array shuffle function.
    def shuffle(deck):
        # TODO: KS: Abstracted out shuffle if we would like to use our own shuffle function later?
        random.shuffle(deck)
        
        return deck
                      
    #####       Create and return deck [s2, s3, etc]                       
    def createDeck():
        deck = []
        values = ['2','3','4','5','6','7','8','9','10','j','q','k','a']
        suiteList = ['s','h','c','d']        
        
        for v in values:
            for s in suiteList:
                deck.append(s + v)

        return deck

    #####       Deal Deck and return the deck, player's hand, dealer's hand
    def deckDeal(deck):
        
        deck = shuffle(deck)
        
        dealerHand, playerHand = [], []

        cardsToDeal = 2

        while (cardsToDeal > 0):
            playerHand.append(deck[0])
            del deck[0]
            dealerHand.append(deck[0])
            del deck[0]

            cardsToDeal -= 1
            
        return deck, playerHand, dealerHand

    #####       Add a card from deck to hand passed as @param
    def hit(deck, hand):
        ##### could use the lists pop() if we didn't want to 'deal from the end'
        #####  KS: also could extend list and add new method that would deal from front.
        hand.append(deck[0])
        del deck[0]

        return deck, hand

    #####       get Total Value of hand passed as @param. handling Dealer card facing down with isDealerCardDown @param
    def displayValue(hand, isDealerCardDown):
        if(len(hand) > 0):
            totalValue = 0

            if (isDealerCardDown): # If Dealers card is faced down just get value from card in pos[1]
                return hand[0][1:]
            else:
                totalValue = 0

            for card in hand:
                value = card[1:]

                # Jacks, kings and queens are all worth 10, and ace is worth 11    
                if (value == 'j' or value == 'q' or value == 'k'): 
                    value = 10
                elif (value == 'a'): 
                    value = 11
                else: 
                    value = int(value)

                totalValue += value                

            if (totalValue > 21):
                for card in hand:
                    if (card[1] == 'a'): # Handing busting with Ace here
                        totalValue -= 10 
                    if (totalValue <= 21):
                        break
                    else:
                        continue

            return totalValue

    #####       Return Hand Value
    def getHandValue(hand):
        totalValue = 0

        for card in hand:
            value = card[1:]

            # Jacks, kings and queens are all worth 10, and ace is worth 11    
            if (value == 'j' or value == 'q' or value == 'k'): 
                value = 10
            elif (value == 'a'): 
                value = 11
            else: 
                value = int(value)

            totalValue += value            

        if totalValue > 21: # If > 21, handle if hand contains an 'a'
            for card in hand:
                if (card[1] == 'a'): 
                    totalValue -= 10
                if (totalValue <= 21):
                    break
                else:
                    continue

        return totalValue
        
    #####       Called when Dealer || Player has blackjack; should determine outcome.
    def blackJack(deck, playerHand, dealerHand, funds, bet, cards, cardSprite):
        textFont = pygame.font.Font(None, 28)

        playerValue = getHandValue(playerHand)
        dealerValue = getHandValue(dealerHand)
        
        if (playerValue == 21 and dealerValue == 21):
            # The opposing player ties the original blackjack getter because he also has blackjack
            # No money will be lost, and a new hand will be dealt
            displayFont = display(textFont, "Blackjack! The dealer also has blackjack, so it's a push!")
            deck, playerHand, dealerHand, funds, roundEnd = endRound(deck, playerHand, dealerHand, funds, 0, bet, cards, cardSprite)
                
        elif (playerValue == 21 and dealerValue != 21):
            # Dealer loses
            displayFont = display(textFont, "Blackjack! You won $%.2f." %(bet*1.5))
            deck, playerHand, dealerHand, funds, roundEnd = endRound(deck, playerHand, dealerHand, funds, bet, 0, cards, cardSprite)
            
        elif (dealerValue == 21 and playerValue != 21):
            # Player loses, money is lost, and new hand will be dealt
            deck, playerHand, dealerHand, funds, roundEnd = endRound(deck, playerHand, dealerHand, funds, 0, bet, cards, cardSprite)
            displayFont = display(textFont, "Dealer has blackjack! You lose $%.2f." %(bet))
            
        return displayFont, playerHand, dealerHand, funds, roundEnd

    #####       Handle bust.
    def bust(deck, playerHand, dealerHand, funds, moneyGained, moneyLost, cards, cardSprite):
        font = pygame.font.Font(None, 28)
        displayFont = display(font, "You bust! You lost $%.2f." %(moneyLost))
        
        deck, playerHand, dealerHand, funds, roundEnd = endRound(deck, playerHand, dealerHand, funds, moneyGained, moneyLost, cards, cardSprite)
        
        return deck, playerHand, dealerHand, funds, roundEnd, displayFont

    #####       After Round is over; need to clean up hands, check funds, etc
    def endRound(deck, playerHand, dealerHand, funds, moneyGained, moneyLost, cards, cardSprite):
        # If user has BlackJack; payout *1.5
        if (len(playerHand) == 2 and "a" in playerHand[0] or "a" in playerHand[1]):
            moneyGained += (moneyGained/2.0)
         
        cards.empty()
        dCardPos = (560, 100)

                   
        for x in dealerHand:
            card = cardSprite(x, dCardPos)
            dCardPos = (dCardPos[0] + 80, dCardPos [1])
            cards.add(card)

        del playerHand[:]
        del dealerHand[:]

        funds += moneyGained
        funds -= moneyLost

        textFont = pygame.font.Font(None, 28)

        if (funds <= 0):
            gameOver()  
        
        roundEnd = True

        return deck, playerHand, dealerHand, funds, roundEnd 
        
    #####       Called after first deal to check for BlackJack, & when player stands.
    def compareHands(deck, playerHand, dealerHand, funds, bet, cards, cardSprite):
        textFont = pygame.font.Font(None, 28)
        moneyGained = 0
        moneyLost = 0

        dealerValue = getHandValue(dealerHand)
        playerValue = getHandValue(playerHand)
            
        # Dealer hits until he has 17 or over        
        while 1:
            if (dealerValue < 17):
                deck, dealerHand = hit(deck, dealerHand)
                dealerValue = getHandValue(dealerHand)
            else:                   
                break
            
        if (playerValue > dealerValue and playerValue <= 21): # player beats the dealer and has NOT busted.
            moneyGained = bet
            deck, playerHand, dealerHand, funds, roundEnd = endRound(deck, playerHand, dealerHand, funds, bet, 0, cards, cardSprite)
            displayFont = display(textFont, "You won $%.2f." %(bet))
        elif (playerValue == dealerValue and playerValue <= 21): # Tied and player has NOT busted.
            deck, playerHand, dealerHand, funds, roundEnd = endRound(deck, playerHand, dealerHand, funds, 0, 0, cards, cardSprite)
            displayFont = display(textFont, "It's a push!")
        elif (dealerValue > 21 and playerValue <= 21): # Dealer has busted and the player has not.
            deck, playerHand, dealerHand, funds, roundEnd = endRound(deck, playerHand, dealerHand, funds, bet, 0, cards, cardSprite)
            displayFont = display(textFont, "Dealer busts! You won $%.2f." %(bet))
        else:
            deck, playerHand, dealerHand, funds, roundEnd = endRound(deck, playerHand, dealerHand, funds, 0, bet, cards, cardSprite)
            displayFont = display(textFont, "Dealer wins! You lost $%.2f." %(bet))
            
        return deck, roundEnd, funds, displayFont

    #####       Card Sprite Class
    class cardSprite(pygame.sprite.Sprite):
        def __init__(self, card, position): #ctr for Card Sprite.
            pygame.sprite.Sprite.__init__(self)
            cardImage = card + ".png"
            self.image, self.rect = loadImage(cardImage)
            self.position = position

        def update(self):
            self.rect.center = self.position
            
    #####       Hit Button Sprite Class
    class hitButton(pygame.sprite.Sprite): 
        def __init__(self):
            pygame.sprite.Sprite.__init__(self)
            self.image, self.rect = loadImage("blankGreen.png")
            self.position = (100, 350)
            
        def update(self, mX, mY, deck, playerHand, cards, pCardPos, roundEnd, cardSprite, click):
            if (roundEnd == False):  #Toggle visibility of button based on if roundIsOver
                self.image, self.rect = loadImage("hit.png") 
            else: 
                self.image, self.rect = loadImage("blankGreen.png")                 
            
            self.position = (100, 350)
            self.rect.center = self.position
            
            if (self.rect.collidepoint(mX, mY) == 1 and click == 1):
                if (roundEnd == False): 
                    deck, playerHand = hit(deck, playerHand)

                    currentCard = len(playerHand) - 1
                    card = cardSprite(playerHand[currentCard], pCardPos)
                    cards.add(card)
                    pCardPos = (pCardPos[0] + 80, pCardPos[1])
                
                    click = 0
                
            return deck, playerHand, pCardPos, click
            
    class standButton(pygame.sprite.Sprite): 
        def __init__(self):
            pygame.sprite.Sprite.__init__(self)
            self.image, self.rect = loadImage("blankGreen.png")
            self.position = (100, 500)
            
        def update(self, mX, mY, deck, playerHand, dealerHand, cards, pCardPos, roundEnd, cardSprite, funds, bet, displayFont):
            if (roundEnd == False): 
                self.image, self.rect = loadImage("stand.png")
            else: 
                self.image, self.rect = loadImage("blankGreen.png")
            
            self.position = (100, 500)
            self.rect.center = self.position
            
            if (self.rect.collidepoint(mX, mY) == 1):
                if (roundEnd == False): 
                    deck, roundEnd, funds, displayFont = compareHands(deck, playerHand, dealerHand, funds, bet, cards, cardSprite)
                
            return deck, roundEnd, funds, playerHand, pCardPos, displayFont 
            
    class doubleButton(pygame.sprite.Sprite): 
        def __init__(self):
            pygame.sprite.Sprite.__init__(self)
            self.image, self.rect = loadImage("blankGreen.png")
            self.position = (100, 425)
            
        def update(self, mX, mY,   deck, playerHand, dealerHand, playerCards, cards, pCardPos, roundEnd, cardSprite, funds, bet, displayFont):
            if (roundEnd == False and funds >= bet * 2 and len(playerHand) == 2): # Double is only available before Player has hit ie. len(hand) == 2
                self.image, self.rect = loadImage("double.png")
            else: 
                self.image, self.rect = loadImage("blankGreen.png")
                
            self.position = (100, 425)
            self.rect.center = self.position
                
            if (self.rect.collidepoint(mX, mY) == 1):
                if (roundEnd == False and funds >= bet * 2 and len(playerHand) == 2): 
                    bet = bet * 2
                    deck, playerHand = hit(deck, playerHand)

                    currentCard = len(playerHand) - 1
                    card = cardSprite(playerHand[currentCard], pCardPos)
                    playerCards.add(card)
                    pCardPos = (pCardPos[0] - 80, pCardPos[1])
        
                    deck, roundEnd, funds, displayFont = compareHands(deck, playerHand, dealerHand, funds, bet, cards, cardSprite)
                    
                    bet = bet / 2

            return deck, roundEnd, funds, playerHand, pCardPos, displayFont, bet

    class dealButton(pygame.sprite.Sprite): 
        def __init__(self):
            pygame.sprite.Sprite.__init__(self)
            self.image, self.rect = loadImage("deal.png")
            self.position = (175, 600)

        def update(self, mX, mY, deck, roundEnd, cardSprite, cards, playerHand, dealerHand, dCardPos, pCardPos, displayFont, playerCards, click):
            textFont = pygame.font.Font(None, 28)
            
            if (roundEnd == True): 
                self.image, self.rect = loadImage("deal.png")
            else: 
                self.image, self.rect = loadImage("blankGreen.png")
            
            self.position = (175, 600)
            self.rect.center = self.position            
                
            if (self.rect.collidepoint(mX, mY) == 1):
                if (roundEnd == True and click == True):
                    displayFont = display(textFont, "")
                    
                    dealerCards.empty()
                    playerCards.empty()

                    deck = createDeck()
                    
                    deck, playerHand, dealerHand = deckDeal(deck)

                    dCardPos = (560, 100)
                    pCardPos = (560, 450)

                    # Create player's card sprites
                    for x in playerHand:
                        card = cardSprite(x, pCardPos)
                        pCardPos = (pCardPos[0] + 80, pCardPos [1])
                        playerCards.add(card)
                    
                    # Create dealer's card sprites  
                    card = cardSprite(dealerHand [0], dCardPos)
                    dCardPos = (dCardPos[0] + 80, dCardPos[1])
                    dealerCards.add(card)

                    faceDownCard = cardSprite("back", dCardPos) #Hide Dealer's second card
                    dealerCards.add(faceDownCard)
                    roundEnd = False
                    click = False
                    
            return deck, playerHand, dealerHand, dCardPos, pCardPos, roundEnd, displayFont, click
            
    class betButtonUp(pygame.sprite.Sprite): 
        def __init__(self):
            pygame.sprite.Sprite.__init__(self)
            self.image, self.rect = loadImage("plus.png")
            self.position = (100, 600)
            
        def update(self, mX, mY, bet, funds, click, roundEnd):
            if (roundEnd == 1): 
                self.image, self.rect = loadImage("plus.png")
            else: 
                self.image, self.rect = loadImage("blankGreen.png")
            
            self.position = (100, 600)
            self.rect.center = self.position
            
            if (self.rect.collidepoint(mX, mY) == True and click == True and roundEnd == True):
                if (bet < funds):
                    bet += 5.0

                click = 0
            
            return bet, click
            
    class betButtonDown(pygame.sprite.Sprite): 
        def __init__(self):
            pygame.sprite.Sprite.__init__(self)
            self.image, self.rect = loadImage("minus.png")
            self.position = (50, 600)
            
        def update(self, mX, mY, bet, click, roundEnd):  
            # Get either minus png or black png
            if (roundEnd == True): 
                self.image, self.rect = loadImage("minus.png")
            else: 
                self.image, self.rect = loadImage("blankGreen.png")
        
            self.position = (50, 600)
            self.rect.center = self.position
            
            if (self.rect.collidepoint(mX, mY) == True and click == True and roundEnd == True):
                if bet > 5:
                    bet = bet - 5.0
                    
                    
                click = 0
            
            return bet, click

    # This font is used to display text on the right-hand side of the screen
    textFont = pygame.font.Font(None, 28)

    # This sets up the background image, and its container rect
    background, backgroundRect = loadImage("BlackJackTable.png")
    
    # Dealear & Player cards is the sprite group
    dealerCards = pygame.sprite.Group()
    playerCards = pygame.sprite.Group()

    # This creates instances of all the button sprites
    bbU = betButtonUp()
    bbD = betButtonDown()
    standButton = standButton()
    dealButton = dealButton()
    hitButton = hitButton()
    doubleButton = doubleButton()
    
    # This group containts the button sprites
    buttons = pygame.sprite.Group(bbU, bbD, hitButton, standButton, dealButton, doubleButton)
    
    deck = []

    # Defaults
    playerHand, dealerHand, dCardPos, pCardPos = [],[],(),()
    mX, mY = 0, 0
    click = 0
    funds = 100.00
    bet = 10.00
    roundEnd = True
    firstTime = True

    while True:
        screen.blit(background, backgroundRect)
        
        if (bet > funds):
            bet = funds
        
        if (roundEnd == True and firstTime == True):
            displayFont = display(textFont, "Please Select Bet Amount Bellow:")
            firstTime = 0

        #       Player funds / current balance / etc
        screen.blit(displayFont, (250,550))
        fundsFont = pygame.font.Font.render(textFont, "Funds: $%.2f" %(funds), 1, (255,255,255), (0,0,0))
        screen.blit(fundsFont, (250,570))
        betFont = pygame.font.Font.render(textFont, "Bet: $%.2f" %(bet), 1, (255,255,255), (0,0,0))
        screen.blit(betFont, (250,590))
        
        for event in pygame.event.get():
            if (event.type == QUIT):
                sys.exit()
            elif (event.type == MOUSEBUTTONDOWN):
                if event.button == 1:
                    mX, mY = pygame.mouse.get_pos()
                    click = 1
            elif (event.type == MOUSEBUTTONUP):
                mX, mY = 0, 0
                click = 0
            
        if (roundEnd == False):
            playerValue = getHandValue(playerHand)
            dealerValue = getHandValue(dealerHand)

            displayPlayerValue = displayValue(playerHand, False)
            displayDealerValue = displayValue(dealerHand, True)
            

            fundsFont = pygame.font.Font.render(textFont, "Player Hand Value: " + str(displayPlayerValue), 1, (255,255,255), (0,0,0))
            screen.blit(fundsFont, (250,450))

            fundsFont = pygame.font.Font.render(textFont, "Dealer Hand Value: " + str(displayDealerValue) + "(?)", 1, (255,255,255), (0,0,0))
            screen.blit(fundsFont, (250,100))
    
            if (playerValue == 21 and len(playerHand) == 2):
                displayFont, playerHand, dealerHand, funds, roundEnd = blackJack(deck, playerHand, dealerHand, funds,  bet, dealerCards, cardSprite)
                
            if (dealerValue == 21 and len(dealerHand) == 2):
                displayFont, playerHand, dealerHand, funds, roundEnd = blackJack(deck, playerHand, dealerHand, funds,  bet, dealerCards, cardSprite)

            if (playerValue > 21):
                deck, playerHand, dealerHand, funds, roundEnd, displayFont = bust(deck, playerHand, dealerHand, funds, 0, bet, dealerCards, cardSprite)
         
        
        # update buttons
        deck, playerHand, dealerHand, dCardPos, pCardPos, roundEnd, displayFont, click = dealButton.update(mX, mY, deck, roundEnd, cardSprite, dealerCards, playerHand, dealerHand, dCardPos, pCardPos, displayFont, playerCards, click)   
        deck, playerHand, pCardPos, click = hitButton.update(mX, mY, deck, playerHand, playerCards, pCardPos, roundEnd, cardSprite, click)
        deck, roundEnd, funds, playerHand, pCardPos,  displayFont  = standButton.update(mX, mY, deck, playerHand, dealerHand, dealerCards, pCardPos, roundEnd, cardSprite, funds, bet, displayFont)
        deck, roundEnd, funds, playerHand, pCardPos, displayFont, bet  = doubleButton.update(mX, mY, deck, playerHand, dealerHand, playerCards, dealerCards, pCardPos, roundEnd, cardSprite, funds, bet, displayFont)
        bet, click = bbU.update(mX, mY, bet, funds, click, roundEnd)
        bet, click = bbD.update(mX, mY, bet, click, roundEnd)
        
        # draw buttons on the screen
        buttons.draw(screen)
         
        # update and draw cards
        playerCards.update()
        playerCards.draw(screen)
        dealerCards.update()
        dealerCards.draw(screen)

        # Updates the contents of the display
        pygame.display.flip()

if __name__ == "__main__":
    mainGame()
