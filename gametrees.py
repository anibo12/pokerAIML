from itertools import combinations
from itertools import permutations
from itertools import product
from collections import Counter
from copy import deepcopy
from functools import partial
from treys import Card,Deck,Evaluator
import sys
sys.setrecursionlimit(1000000)

Fold=0
All_in=1
Call=2
Check=3
Halfpot=4
Fullpot=5

full_deck=[]
for rank in Card.STR_RANKS:
    for suit, val in Card.CHAR_SUIT_TO_INT_SUIT.items():
        full_deck.append(Card.new(rank + suit))

class Gametree(object):
    def __init__(self):
        self.root=Node(parent=None,hands="",board="",stack=200,pot=0,current_bet=0,self_bet=0)
        self.count=3

    def build(self):
        for i in range(2):
            self.root.children.append(BeginNode(self.root,hands="",board="",stack=200,pot=0,current_bet=0,self_bet=0,position=i))
        for node in self.root.children:
            self.build_subtree(node)

    def build_subtree(self,target_node):
        self.count+=1
        print(self.count,":",type(target_node))
        if type(target_node)==TerminalNode:
            pass
        else:
            target_node.get_children()
            for node in target_node.children:
                node.get_children()
                self.build_subtree(node)

class Node(object):
    def __init__(self,parent,hands,board,stack,pot,current_bet,self_bet):
        self.parent=parent
        self.hands=hands
        self.board=board
        self.stack=stack
        self.pot=pot
        self.current_bet=current_bet
        self.self_bet=self_bet
        self.children=[]

    def __str__(self):
        return("hands:")

#get the options of actions
    def get_actions(self):
        raise NotImplementedError("get_actions should be rewriten")

    def get_children(self):
        raise NotImplementedError("get_children should be rewriten")

class  BeginNode(Node):
    def __init__(self,parent,hands,board,stack,pot,current_bet,self_bet,position):
        Node.__init__(self,parent,hands,board,stack,pot,current_bet,self_bet)
        self.position=position
        if position==0:
            self.stack-=1
            self.self_bet=1
        else:
            self.stack-=2
            self.self_bet=2
        self.pot+=3
        self.current_bet=2

    def get_children(self):
        self.children=[]
        temp_deck=[]
        for rank in Card.STR_RANKS:
            for suit in ("s","h"):
                temp_deck.append(Card.new(rank + suit))

        hands_combination=[]
        for i in range(13):
            for j in range(i+1,len(temp_deck)):
                hands_combination.append([temp_deck[i],temp_deck[j]])

        for temp_hands in hands_combination:
            self.children.append(CardNode(self,hands=temp_hands,board=self.board,stack=self.stack,pot=self.pot,current_bet=self.current_bet,self_bet=self.self_bet,position=self.position))

    def get_actions(self):
        return None

class CardNode(Node):
    def __init__(self,parent,hands,board,stack,pot,current_bet,self_bet,position):
        Node.__init__(self,parent,hands,board,stack,pot,current_bet,self_bet)
        self.position=position

    def get_actions(self):
        actions=[All_in]
        if self.current_bet>self.self_bet:
            actions.append(Fold)
        if self.self_bet<self.current_bet and self.stack>=self.current_bet-self.self_bet:
            actions.append(Call)
        if self.current_bet==self.self_bet:
            actions.append(Check)
        if self.stack>0.5*self.pot:
            actions.append(Halfpot)
        if self.stack>self.pot:
            actions.append(Fullpot)
        return actions

    def get_children(self):
        self.children=[]
        actions=self.get_actions()
        for action in actions:
            #fold causes the game to end
            if action==Fold:
                self.children.append(TerminalNode(self,hands=self.hands,board=self.board,stack=self.stack,pot=self.pot,current_bet=self.current_bet,self_bet=self.self_bet,position=self.position,reason="Fold"))
            #all in action node
            elif action==All_in:
                self.children.append(ActionNode(self,hands=self.hands,board=self.board,stack=0,pot=self.pot+self.stack,current_bet=self.self_bet+self.stack,self_bet=self.self_bet+self.stack,position=self.position))
            #call action node( end the game or flip another card)
            elif action==Call:
                if len(self.board)==5:
                    self.children.append(TerminalNode(self, hands=self.hands, board=self.board, stack=self.stack-(self.current_bet-self.self_bet), pot=self.pot + (self.current_bet-self.self_bet),
                               current_bet=self.current_bet, self_bet=self.current_bet,
                               position=self.position,reason="Call"))
                else:
                    self.children.append(ActionNode(self, hands=self.hands, board=self.board, stack=self.stack-(self.current_bet-self.self_bet), pot=self.pot + (self.current_bet-self.self_bet),
                               current_bet=self.current_bet, self_bet=self.current_bet,
                               position=self.position,flip=True))
            #check action node(end the game or flip a card or wait for other's action)
            elif action==Check:
                if self.position==0 and len(self.board)==5:
                    self.children.append(
                    TerminalNode(self, hands=self.hands, board=self.board, stack=self.stack, pot=self.pot,
                                 current_bet=self.current_bet, self_bet=self.self_bet, position=self.position,reason="Check-show down"))
                elif self.position==0:
                    self.children.append(
                    ActionNode(self, hands=self.hands, board=self.board, stack=self.stack, pot=self.pot,
                                 current_bet=self.current_bet, self_bet=self.self_bet, position=self.position,flip=True))
                else:
                    self.children.append(
                    ActionNode(self, hands=self.hands, board=self.board, stack=self.stack, pot=self.pot,
                                 current_bet=self.current_bet, self_bet=self.self_bet, position=self.position))
            #bet half pot action node
            elif action==Halfpot:
                betsize=int(0.5*self.pot)
                self.children.append(
                    ActionNode(self, hands=self.hands, board=self.board, stack=self.stack-betsize, pot=self.pot+betsize,
                                 current_bet=self.self_bet+betsize, self_bet=self.self_bet+betsize, position=self.position))
            #bet full pot action node
            elif action==Fullpot:
                betsize=self.pot
                self.children.append(ActionNode(self, hands=self.hands, board=self.board, stack=self.stack-betsize, pot=self.pot+betsize,
                                 current_bet=self.self_bet+betsize, self_bet=self.self_bet+betsize, position=self.position))

class ActionNode(Node):
    def __init__(self,parent,hands,board,stack,pot,current_bet,self_bet,position,flip=False):
        Node.__init__(self,parent,hands,board,stack,pot,current_bet,self_bet)
        self.position=position
        self.flip=flip

    def get_actions(self):
        actions=[All_in]
        if self.current_bet>self.self_bet:
            actions.append(Fold)
        if self.self_bet<self.current_bet and self.stack>=self.current_bet-self.self_bet:
            actions.append(Call)
        if self.current_bet==self.self_bet:
            actions.append(Check)
        if self.stack>0.5*self.pot:
            actions.append(Halfpot)
        if self.stack>self.pot:
            actions.append(Fullpot)
        return actions

    def get_children(self):
        self.children=[]
        temp_deck=full_deck[:]
        if self.flip:
            for card in self.hands:
                temp_deck.remove(card)
            if self.board!="":
                for card in self.board:
                    temp_deck.remove(card)

            if len(self.board)>=3:
                for card in temp_deck:
                    temp_board=list(self.board)
                    temp_board.append(card)
                    self.children.append(CardNode(self,hands=self.hands,board=temp_board,stack=self.stack,pot=self.pot,current_bet=0,self_bet=0,position=self.position))
            else:
                board_combinations=list(combinations(temp_deck,3))
                for comb in board_combinations:
                    self.children.append(
                        CardNode(self, hands=self.hands, board=comb, stack=self.stack, pot=self.pot,
                                 current_bet=0, self_bet=0, position=self.position))
        else:
            actions=self.get_actions()
            for action in actions:
                if action == Fold:
                    self.children.append(
                        TerminalNode(self, hands=self.hands, board=self.board, stack=self.stack, pot=self.pot,
                                     current_bet=self.current_bet, self_bet=self.self_bet, position=self.position,
                                     reason="Fold"))
                elif action == All_in:
                    self.children.append(TerminalNode(self, hands=self.hands, board=self.board, stack=0, pot=self.pot + self.stack,
                                       current_bet=self.self_bet + self.stack, self_bet=self.self_bet + self.stack,
                                       position=self.position,reason="All in"))
                elif action == Call:
                    if len(self.board) == 5:
                        self.children.append(TerminalNode(self, hands=self.hands, board=self.board,
                                                          stack=self.stack - (self.current_bet - self.self_bet),
                                                          pot=self.pot + (self.current_bet - self.self_bet),
                                                          current_bet=self.current_bet, self_bet=self.current_bet,
                                                          position=self.position, reason="Call"))
                    elif self.stack - (self.current_bet - self.self_bet)==0:
                        self.children.append(TerminalNode(self, hands=self.hands, board=self.board,
                                                          stack=self.stack - (self.current_bet - self.self_bet),
                                                          pot=0,
                                                          current_bet=self.current_bet, self_bet=self.current_bet,
                                                          position=self.position, reason="All in"))
                    else:
                        self.children.append(ActionNode(self, hands=self.hands, board=self.board,
                                                        stack=self.stack - (self.current_bet - self.self_bet),
                                                        pot=self.pot + (self.current_bet - self.self_bet),
                                                        current_bet=self.current_bet, self_bet=self.current_bet,
                                                        position=self.position, flip=True))
                elif action == Check:
                    if self.position == 0 and len(self.board) == 5:
                        self.children.append(
                            TerminalNode(self, hands=self.hands, board=self.board, stack=self.stack, pot=self.pot,
                                         current_bet=self.current_bet, self_bet=self.self_bet, position=self.position,
                                         reason="Check-show down"))
                    elif self.position == 0:
                        self.children.append(
                            ActionNode(self, hands=self.hands, board=self.board, stack=self.stack, pot=self.pot,
                                       current_bet=self.current_bet, self_bet=self.self_bet, position=self.position,
                                       flip=True))
                    else:
                        self.children.append(
                            ActionNode(self, hands=self.hands, board=self.board, stack=self.stack, pot=self.pot,
                                       current_bet=self.current_bet, self_bet=self.self_bet, position=self.position))

                elif action == Halfpot:
                    betsize = int(0.5 * self.pot)
                    self.children.append(
                        ActionNode(self, hands=self.hands, board=self.board, stack=self.stack - betsize,
                                   pot=self.pot + betsize,
                                   current_bet=self.self_bet + betsize, self_bet=self.self_bet + betsize,
                                   position=self.position))
                elif action == Fullpot:
                    betsize = self.pot
                    self.children.append(
                        ActionNode(self, hands=self.hands, board=self.board, stack=self.stack - betsize,
                                   pot=self.pot + betsize,
                                   current_bet=self.self_bet + betsize, self_bet=self.self_bet + betsize,
                                   position=self.position))

class TerminalNode(Node):
    def __init__(self,parent,hands,board,stack,pot,current_bet,self_bet,position,reason,flip=False):
        Node.__init__(self,parent,hands,board,stack,pot,current_bet,self_bet)
        self.position=position
        self.reason=reason

    def get_actions(self):
        return None

    def get_children(self):
        pass

tree=Gametree()
tree.build()