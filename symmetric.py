# -*- coding: utf-8 -*-
"""
Created on Thu Apr 12 16:03:29 2018

@author: zsnyd
"""

from treys import Card


char_to_int = {
    's': 1,  # spades
    'h': 2,  # hearts
    'd': 4,  # diamonds
    'c': 8,  # clubs
}


int_to_char = {
    1: 's',  # spades
    2: 'h',  # hearts
    4: 'd',  # diamonds
    8: 'c',  # clubs
}



##get_suit_int()
#'s': 1 --- spades
#'h': 2 --- hearts
#'d': 4 --- diamonds
#'c': 8 --- clubs
#Input is list of two cards, represent cards in player's hand
#returns swaps needed in list 
#For example:
#['hs'] == hearts to spades
#['cs'] == clubs to spades


def find_swap(hand):
    
    s1 = Card.get_suit_int(hand[0])
    s2 = Card.get_suit_int(hand[1])
    
    if(s1 == s2):
        if(s1 == 1):
            return 0 #both are spades, do nothing
        else:
            return [int_to_char[s1] + 's'] #swap with spades
            
    elif(s1 == 1 or s2 == 1):
        
        if(s1 == 1):
            if(s2 != 2):
                return [int_to_char[s2] + 'h']
            else:
                return 0
        else:
            #some suit with spade
            if(s1 != 2):
                return [int_to_char[s1] + 'h', 'hs']
            else:
                #heart and spade
                return ['hs']
                
                
    elif(s1 == 2 or s2 == 2): #no spades, hearts and something else
        if(s1 == 2):
            return[int_to_char[s2] + 's', 'sh']
        
        else:
            return[int_to_char[s1] + 's']

    else:
        return[int_to_char[s1] + 's', int_to_char[s2] + 'h']


#print(find_swap(h))

    
#hands --- list containing cards to change
#swaps --- list containing swaps to make
#returns a card in integer form
def make_swaps(cards, swaps):
    
    if(swaps != 0):
            
        bool_list = [False]*len(cards)
        
        for i in range(len(cards)):
            for j in range(len(swaps)):
                
                #attempt to make swap
                returned_card = do_swap(cards[i], swaps[j])
                
                #if swap occurs then change value of bool list
                if(cards[i] != returned_card):
                    bool_list[i] = True
                    
                cards[i] = returned_card
        
        
        for i in range(len(swaps)):
            swaps[i] = swaps[i][::-1]
        
        
        #do opposite swap
        for i in range(len(cards)):
            for j in range(len(swaps)):
                if(bool_list[i] == False):
                    cards[i] = do_swap(cards[i], swaps[j])
                
    
        return cards
    
    else:
        
        return 0
    
   
    
#input is single card and single swap
#helper function for make_swaps
def do_swap(card, swap):
    
    char_one = swap[0]
    char_two = swap[1]
    
    if(Card.get_suit_int(card) == char_to_int[char_one]):
        return Card.new(str(Card.get_rank_int(card) + 2) + char_two)
    else:
        return card
    
    
    
#EXAMPLES
hand = []
hand.append(Card.new("7h"))
hand.append(Card.new("8d"))


Card.print_pretty_cards(hand)

s = find_swap(hand)
new_hand = make_swaps(hand, s)

if(new_hand != 0):
    Card.print_pretty_cards(new_hand)




