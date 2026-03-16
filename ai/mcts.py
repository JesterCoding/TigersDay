import numpy as np
import game.updater as Updater

class Node:
    def __init__(self, state, parent=None, move=None, prior=0.0):
        self.state = state
        self.parent = parent
        self.move = move
        self.children = {}
        
        self.visit_count = 0
        self.value_sum = 0.0
        self.prior = prior

    @property
    def eval(self):
        if self.visit_count == 0:
            return 0.0
        return self.value_sum / self.visit_count
    
    @property
    def is_expanded(self):
        return len(self.children) > 0
    
    # lazy evaluation, generate state before querying
    @property
    def is_luck(self):
        return self.state.is_luck
    
    # mask and normalize before this
    # call when is_luck False
    def expand_decision(self, action_priors):
        for move, prior in enumerate(action_priors):
            if prior > 0.0 and move not in self.children:
                self.children[move] = Node(None, self, move, prior)
                # lazy evaluation, leave game state unexplored

    # call when is_luck True
    def expand_luck(self):
        luck_outcomes = Updater.get_luck_outcomes(self.state)
        prior = 1.0 / len(luck_outcomes)

        for i, outcome in enumerate(luck_outcomes):
            if i not in self.children:
                self.children[i] = Node(outcome, self, i, prior)