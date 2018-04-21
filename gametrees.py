from itertools import combinations
from treys import Card
import sys
import os
import time
sys.setrecursionlimit(1000000)

Fold=0
All_in=1
Call=2
Check=3
Halfpot=4
Fullpot=5
Nothing=6
action_to_str=["Fold","All_in","Call","Check","Halfpot","Fullpot","Nothing"]

#Full_deck includes 52 cards
full_deck=[]
for rank in Card.STR_RANKS:
    for suit, val in Card.CHAR_SUIT_TO_INT_SUIT.items():
        full_deck.append(Card.new(rank + suit))

class Gametree(object):
    def __init__(self):
        self.root=Node(parent=None,hands="",board="",stack=200,pot=0,current_bet=0,self_bet=0)
        self.count=3

    def build(self):
        path = os.getcwd()
        path+="\\root"
        if os.path.exists(path)==False:
            os.mkdir(path)
        os.chdir(path)
        begin=time.time()
        for i in range(2):
            self.root.children.append(BeginNode(self.root,hands="",board="",stack=200,pot=0,current_bet=0,self_bet=0,position=i))
        for node in self.root.children:
            print(time.time()-begin)
            os.system("pause")
            self.build_subtree(node,path)

#use recursion to build trees
    def build_subtree(self,target_node,path):
        self.count+=1
        if type(target_node)==BeginNode:
            subpath=path+"\\Beginnode"+str(self.count)
        elif type(target_node)==CardNode:
            if target_node.board=="":
                subpath=path+"\\"+str([Card.int_to_pretty_str(card)for card in target_node.hands])
            elif len(target_node.board)==3:
                subpath = path + "\\" + str([Card.int_to_pretty_str(card) for card in target_node.board])
            else:
                subpath = path + "\\" + Card.int_to_pretty_str(target_node.board[-1])
        elif type(target_node)==ActionNode:
            subpath=path+"\\("+action_to_str[target_node.label]+","+action_to_str[target_node.previous_action]+")"
        else:
            subpath=path+"\\"+target_node.reason
        if os.path.exists(subpath) == False:
            os.mkdir(subpath)
        os.chdir(subpath)
        print(self.count, type(target_node))
        if type(target_node)==TerminalNode:
            with open("node info.txt", "w") as f:
                f.write(str(target_node))
        else:
            target_node.get_children()
            with open("node info.txt", "w") as f:
                f.write(str(target_node))
            if len(target_node.board)!="":Card.print_pretty_cards(target_node.board)
            for node in target_node.children:
                self.build_subtree(node,subpath)


"""parent:parent node
hands:hand cards
board:board cards
pot:pot size
current_bet:the present max betsize 
self_bet:the bet which has been done 
"""
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
        string="type:"+str(type(self))+"\n"
        string+="hands:"+(self.hands if self.hands==""else str([Card.int_to_str(card) for card in self.hands]))+"\n"
        string+="board:"+(self.board if self.board==""else str([Card.int_to_str(card)for card in self.board]))+"\n"
        string+="stack:"+str(self.stack)+"\n"
        string+="pot:"+str(self.pot)+"\n"
        string+="current_bet:"+str(self.current_bet)+"\n"
        string+="self_bet:"+str(self.self_bet)+"\n"
        string+="actions:"+("None"if self.get_actions()==None else str([action_to_str[action] for action in self.get_actions()]))+"\n"
        return string

#get the options of actions
    def get_actions(self):
        raise NotImplementedError("get_actions should be rewriten")

    def get_children(self):
        raise NotImplementedError("get_children should be rewriten")

"""position:the index of the node's player
0:small blind/dealer   1:big blind
"""
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

    def __str__(self):
        string=Node.__str__(self)
        string+="position:"+str(self.position)
        return string

    def get_children(self):
        self.children=[]
        temp_deck=[]
        for suit in ("s","h"):
            for rank in Card.STR_RANKS:
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

    def __str__(self):
        string=Node.__str__(self)
        string+="position:"+str(self.position)
        return string

    def get_actions(self):
        actions=[All_in]
        if self.current_bet>self.self_bet:
            actions.append(Fold)
        if self.self_bet<self.current_bet and self.stack>self.current_bet-self.self_bet:
            actions.append(Call)
        if self.current_bet==self.self_bet:
            actions.append(Check)
        if self.stack>0.5*self.pot and int(0.5*self.pot)>self.current_bet-self.self_bet:
            actions.append(Halfpot)
        if self.stack>self.pot:
            actions.append(Fullpot)
        return actions

    def get_children(self):
        if (self.board==""and self.position==0)or self.position==1:
            self.children=[ActionNode(self,hands=self.hands,board=self.board,stack=self.stack,pot=self.pot,current_bet=self.current_bet,self_bet=self.self_bet,position=self.position)]
        else:
            temp_node = CardNode(self.parent, self.hands, self.board, 400 - self.stack - self.pot, self.pot,
                                 self.current_bet, (0 if self.self_bet != 2 else 1), (self.position + 1) % 2)
            actions=temp_node.get_actions()
            for action in actions:
                if action==Fold:
                    self.children.append(TerminalNode(self, hands=self.hands, board=self.board, stack=self.stack, pot=self.pot, current_bet=self.current_bet, self_bet=self.self_bet, position=self.position, reason="Opponent fold"))
                elif action==All_in:
                    #preflop
                    if self.board=="":
                        self.children.append(ActionNode(self, hands=self.hands, board=self.board, stack=self.stack, pot=202,
                                                        current_bet=200, self_bet=self.self_bet, position=self.position,previous_action=All_in))
                    #other situations
                    else:
                        self.children.append(ActionNode(self, hands=self.hands, board=self.board, stack=self.stack, pot=self.pot+self.stack,
                                                        current_bet=self.stack, self_bet=self.self_bet, position=self.position,previous_action=All_in))
                elif action==Check:
                    self.children.append(ActionNode(self, hands=self.hands, board=self.board, stack=self.stack, pot=self.pot,
                                                    current_bet=self.current_bet, self_bet=self.self_bet, position=self.position,previous_action=Check))
                #This only exists in preflop
                elif action==Call:
                    self.children.append(ActionNode(self, hands=self.hands, board=self.board, stack=self.stack, pot=self.pot+1,
                                                    current_bet=self.current_bet, self_bet=self.self_bet, position=self.position,previous_action=Call))
                elif action==Halfpot:
                    self.children.append(ActionNode(self, hands=self.hands, board=self.board, stack=self.stack, pot=self.pot+int(0.5*self.pot),
                                                    current_bet=int(0.5*self.pot), self_bet=self.self_bet, position=self.position,previous_action=Halfpot))
                elif action==Fullpot:
                    self.children.append(ActionNode(self, hands=self.hands, board=self.board, stack=self.stack, pot=2*self.pot,
                                                    current_bet=self.pot, self_bet=self.self_bet, position=self.position,previous_action=Fullpot))

"""flip: determine whether to flip card(s)
previous_action: the action your opponent did(mostly, it won't be used. When ur opponent fold,create the terminal node)
if there is no previous action,  the default value is Nothing
"""
class ActionNode(Node):
    def __init__(self,parent,hands,board,stack,pot,current_bet,self_bet,position,previous_action=Nothing,flip=False,label=-1):
        Node.__init__(self,parent,hands,board,stack,pot,current_bet,self_bet)
        self.position=position
        self.flip=flip
        self.previous_action=previous_action
        self.label=label

    def __str__(self):
        string=Node.__str__(self)
        string+="position:"+str(self.position)+"\n"
        string += "flip:" + str(self.flip) + "\n"
        string += "previous action:" + action_to_str[self.previous_action] + "\n"
        string += "label:" + action_to_str[self.label] + "\n"
        try:
            string+=str([self.possibility[i] for i in range(len(self.possibility))])+"\n"
            string += str([self.regrets[i] for i in range(len(self.regrets))]) + "\n"
        except AttributeError:
            pass
        return string

    def get_actions(self):
        actions=[All_in]
        if self.current_bet>self.self_bet:
            actions.append(Fold)
        if self.self_bet<self.current_bet and self.stack>self.current_bet-self.self_bet:
            actions.append(Call)
        if self.current_bet==self.self_bet:
            actions.append(Check)
        if self.stack>0.5*self.pot and 0.5*self.pot>self.current_bet-self.self_bet:
            actions.append(Halfpot)
        if self.stack>self.pot:
            actions.append(Fullpot)
        return actions

    def get_children(self):
        self.children=[]
        if self.previous_action==Fold:
            self.children.append(TerminalNode(self, hands=self.hands, board=self.board, stack=self.stack,pot=self.pot,
                                              current_bet=self.current_bet, self_bet=self.self_bet, position=self.position, reason="Opponent fold"))
        else:
            #can flip another card
            if self.flip:
                temp_deck = full_deck[:]
                for card in self.hands:
                    temp_deck.remove(card)
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
            #can't flip another card
            else:
                self.actions = self.get_actions()
                self.possibility=[1/len(self.actions)for i in range(len(self.actions))]
                self.regrets=[0 for i in range(len(self.actions))]
                for action in self.actions:
                    # if fold, create a terminal node
                    if action == Fold:
                        self.children.append(
                            TerminalNode(self, self.hands, self.board, self.stack, self.pot, self.current_bet,
                                         self.self_bet, self.position, reason="Fold"))
                    # if all in , since there is no more actions that can be taken after that, create a terminal node
                    elif action == All_in:
                        self.children.append(TerminalNode(self, self.hands, self.board, 0, self.pot + self.stack,
                                                          self.self_bet + self.stack, self.self_bet + self.stack,
                                                          self.position, reason="All in"))
                    elif action == Call:
                        # if call and there are 5 borad cards, the game will end and a terminal node is created
                        if len(self.board) == 5:
                            self.children.append(TerminalNode(self, self.hands, self.board,
                                                              self.stack - (self.current_bet - self.self_bet),
                                                              self.pot + self.current_bet - self.self_bet,
                                                              self.current_bet, self.current_bet, self.position,
                                                              reason="Show down"))
                        elif self.self_bet==1:
                            temp_actionnode = ActionNode(self, self.hands, self.board, 198, self.pot+1,
                                                         self.current_bet, self.current_bet, (self.position + 1) % 2,
                                                         previous_action=Call)
                            temp_actions=temp_actionnode.get_actions()
                            for temp_action in temp_actions:
                                # if the opponent all in,create an actionnode
                                if temp_action == All_in:
                                    self.children.append(ActionNode(self, self.hands, self.board, 198,
                                                                    202, 200,
                                                                    self.self_bet+1, self.position,
                                                                    previous_action=All_in, label=Call))
                                # if the opponent check,create an actionnode which can create cardnode as children
                                elif temp_action == Check:
                                        self.children.append(
                                            ActionNode(self, self.hands, self.board, 198, 4,
                                                       2, 2, self.position,
                                                       previous_action=Check, flip=True, label=Call))
                                # if the opponent bet half of the pot,create an actionnode
                                elif temp_action == Halfpot:
                                    self.children.append(ActionNode(self, self.hands, self.board, 198,
                                                                    6, 4,
                                                                    2, self.position,
                                                                    previous_action=Halfpot, label=Call))
                                # if the opponent bet full pot,create an actionnode
                                elif temp_action == Fullpot:
                                    self.children.append(
                                        ActionNode(self, self.hands, self.board, 198,
                                                   8, 6,
                                                   2, self.position, previous_action=Fullpot, label=Check))
                                else:
                                    raise NotImplementedError("This call or fold is weird")
                        # if call and there are not 5 borad cards, the game will continue to flip another card and an action node which can have cardnodes as children is created
                        else:
                            self.children.append(ActionNode(self, self.hands, self.board,
                                                            self.stack - (self.current_bet - self.self_bet),
                                                            self.pot + self.current_bet - self.self_bet,
                                                            self.current_bet, self.current_bet, self.position,
                                                            previous_action=self.previous_action, flip=True,label=Call))
                    elif action == Check:
                        # if check ,there are 5 borad cards and no one acts later, the game will end and a terminal node is created
                        if self.position == 0 and len(self.board) == 5:
                            self.children.append(
                                TerminalNode(self, self.hands, self.board, self.stack, self.pot, self.current_bet,
                                             self.self_bet, self.position, reason="Show down"))
                        # if check ,there are not 5 borad cards and no one acts later, the game will continue to flip another card and an action node which can have cardnodes as children is created
                        elif self.position == 0 and len(self.board) > 0:
                            self.children.append(
                                ActionNode(self, self.hands, self.board, self.stack, self.pot, self.current_bet,
                                           self.self_bet, self.position, previous_action=Check, flip=True,label=Check))
                        elif self.position == 1 and len(self.board) == 0:
                            self.children.append(
                                ActionNode(self, self.hands, self.board, self.stack, self.pot, self.current_bet,
                                           self.self_bet, self.position, previous_action=Call, flip=True,label=Check))
                        # if check and someone will act later, create a series of action nodes to react to different situatins
                        else:
                            # simulate the other one's action node
                            temp_actionnode = ActionNode(self, self.hands, self.board, self.stack, self.pot,
                                                         self.current_bet, self.self_bet, (self.position + 1) % 2,
                                                         previous_action=Check)
                            temp_actions = temp_actionnode.get_actions()
                            for temp_action in temp_actions:
                                # if the opponent folds,create a terminalnode
                                if temp_action == Fold:
                                    self.children.append(
                                        TerminalNode(self, self.hands, self.board, self.stack, self.pot,
                                                     self.current_bet, self.self_bet, self.position,
                                                     reason="Opponent fold"))
                                # if the opponent all in,create an actionnode
                                elif temp_action == All_in:
                                    self.children.append(ActionNode(self, self.hands, self.board, self.stack,
                                                                    self.pot + (200 - self.stack), 200 - self.stack,
                                                                    self.self_bet, self.position,
                                                                    previous_action=All_in,label=Check))
                                # if the opponent check,create an actionnode which can create cardnode as children
                                elif temp_action == Check:
                                    if len(self.board) == 5:
                                        self.children.append(
                                            TerminalNode(self, self.hands, self.board, self.stack, self.pot,
                                                         self.current_bet, self.self_bet, self.position,
                                                         reason="Show down"))
                                    else:
                                        self.children.append(
                                            ActionNode(self, self.hands, self.board, self.stack, self.pot,
                                                       self.current_bet, self.self_bet, self.position,
                                                       previous_action=Check, flip=True,label=Check))
                                # if the opponent bet half of the pot,create an actionnode
                                elif temp_action == Halfpot:
                                    self.children.append(ActionNode(self, self.hands, self.board, self.stack,
                                                                    self.pot + int(0.5 * self.pot), int(0.5 * self.pot),
                                                                    self.self_bet, self.position,
                                                                    previous_action=Halfpot,label=Check))
                                # if the opponent bet full pot,create an actionnode
                                elif temp_action == Fullpot:
                                    self.children.append(
                                        ActionNode(self, self.hands, self.board, self.stack, self.pot * 2, self.pot,
                                                   self.self_bet, self.position, previous_action=Fullpot ,label=Check))
                                else:
                                    raise NotImplementedError("This call is weird")

                    # similar with action==check 's last situation
                    elif action == Halfpot:
                        # simulate the other one's action node
                        temp_actionnode = ActionNode(self, self.hands, self.board, 400 - self.pot - self.stack,
                                                     self.pot + int(0.5 * self.pot),
                                                     self.self_bet + int(0.5 * self.pot), self.current_bet,
                                                     (self.position + 1) % 2, previous_action=Halfpot)
                        temp_actions = temp_actionnode.get_actions()
                        for temp_action in temp_actions:
                            if temp_action == Fold:
                                self.children.append(
                                    TerminalNode(self, self.hands, self.board, self.stack - int(0.5 * self.pot),
                                                 self.pot + int(0.5 * self.pot),
                                                 self.self_bet + int(0.5 * self.pot),
                                                 self.self_bet + int(0.5 * self.pot), self.position,
                                                 reason="Opponent fold"))
                            elif temp_action == All_in:
                                self.children.append(
                                    ActionNode(self, self.hands, self.board, self.stack - int(0.5 * self.pot),
                                               self.pot + int(0.5 * self.pot) + 400 - self.pot - self.stack,
                                               self.current_bet + 400 - self.pot - self.stack,
                                               self.self_bet + int(0.5 * self.pot), self.position,
                                               previous_action=All_in, label=Halfpot))
                            elif temp_action == Call or (temp_action == Check and self.board == ""):
                                if len(self.board) != 5:
                                    self.children.append(
                                        ActionNode(self, self.hands, self.board, self.stack - int(0.5 * self.pot),
                                                   self.pot + 2 * int(0.5 * self.pot),
                                                   self.self_bet + int(0.5 * self.pot),
                                                   self.self_bet + int(0.5 * self.pot), self.position,
                                                   previous_action=Call, flip=True, label=Halfpot))
                                else:
                                    self.children.append(
                                        TerminalNode(self, self.hands, self.board, self.stack - int(0.5 * self.pot),
                                                     self.pot + 2 * int(0.5 * self.pot),
                                                     self.self_bet + int(0.5 * self.pot),
                                                     self.self_bet + int(0.5 * self.pot), self.position,
                                                     reason="Show down"))
                            elif temp_action == Halfpot:
                                self.children.append(
                                    ActionNode(self, self.hands, self.board, self.stack - int(0.5 * self.pot),
                                               self.pot + int(0.5 * self.pot) + int(
                                                   0.5 * (self.pot + int(0.5 * self.pot))),
                                               int(0.5 * (self.pot + int(0.5 * self.pot))) + self.current_bet,
                                               self.self_bet + int(0.5 * self.pot), self.position,
                                               previous_action=Halfpot, label=Halfpot))
                            elif temp_action == Fullpot:
                                self.children.append(
                                    ActionNode(self, self.hands, self.board, self.stack - int(0.5 * self.pot),
                                               2 * (self.pot + int(0.5 * self.pot)),
                                               self.pot + int(0.5 * self.pot) + self.current_bet,
                                               self.self_bet + int(0.5 * self.pot), self.position,
                                               previous_action=Fullpot, label=Halfpot))
                            else:
                                print(self)
                                print(temp_actionnode)
                                raise NotImplementedError("This check is weird")

                    elif action == Fullpot:
                        # simulate the other one's action node
                        temp_actionnode = ActionNode(self, self.hands, self.board, 400 - self.pot - self.stack,
                                                     2 * self.pot,
                                                     self.self_bet + self.pot, self.current_bet,
                                                     (self.position + 1) % 2, previous_action=Fullpot)
                        temp_actions = temp_actionnode.get_actions()
                        for temp_action in temp_actions:
                            if temp_action == Fold:
                                self.children.append(
                                    TerminalNode(self, self.hands, self.board, self.stack - self.pot, 2 * self.pot,
                                                 self.self_bet + self.pot, self.self_bet + self.pot, self.position,
                                                 reason="Opponent fold"))
                            elif temp_action == All_in:
                                self.children.append(
                                    ActionNode(self, self.hands, self.board, self.stack - self.pot,
                                               2 * self.pot + 400 - self.pot - self.stack,
                                               self.current_bet + 400 - self.pot - self.stack, self.self_bet + self.pot,
                                               self.position, previous_action=All_in, label=Fullpot))
                            elif temp_action == Call:
                                if len(self.board) == 5:
                                    self.children.append(
                                        TerminalNode(self, self.hands, self.board, self.stack - self.pot,
                                                     3 * self.pot + self.self_bet - self.current_bet,
                                                     self.self_bet + self.pot, self.self_bet + self.pot, self.position,
                                                     reason="Show down"))
                                else:
                                    self.children.append(ActionNode(self, self.hands, self.board, self.stack - self.pot,
                                                                    3 * self.pot + self.self_bet - self.current_bet,
                                                                    self.self_bet + self.pot, self.self_bet + self.pot,
                                                                    self.position, previous_action=Call, flip=True, label=Fullpot))
                            elif temp_action == Halfpot:
                                self.children.append(
                                    ActionNode(self, self.hands, self.board, self.stack - self.pot, 3 * self.pot,
                                               self.pot + self.current_bet, self.self_bet + self.pot, self.position,
                                               previous_action=Halfpot, label=Fullpot))
                            elif temp_action == Fullpot:
                                self.children.append(
                                    ActionNode(self, self.hands, self.board, self.stack - self.pot, 4 * self.pot,
                                               2 * self.pot + self.current_bet, self.self_bet + self.pot, self.position,
                                               previous_action=Fullpot, label=Fullpot))
                            else:
                                raise NotImplementedError("This check is weird")
                    else:
                        raise NotImplementedError("This action is weird")


"""reason: includes["All in","Show down","Fold","Opponent fold"]
"""
class TerminalNode(Node):
    def __init__(self,parent,hands,board,stack,pot,current_bet,self_bet,position,reason):
        Node.__init__(self,parent,hands,board,stack,pot,current_bet,self_bet)
        self.position=position
        self.reason=reason

    def __str__(self):
        string=Node.__str__(self)
        string+="position:"+str(self.position)+"\n"
        string+="reason:"+self.reason
        return string
    def get_actions(self):
        return None

    def get_children(self):
        pass

tree=Gametree()
tree.build()