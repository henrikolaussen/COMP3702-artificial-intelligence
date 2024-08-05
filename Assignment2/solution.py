import sys
import time

from game_env import GameEnv
from game_state import GameState
from itertools import product
from typing import Dict

import transition_restricted as ts
"""
solution.py

This file is a template you should use to implement your solution.

You should implement each of the method stubs below. You may add additional methods and/or classes to this file if you 
wish. You may also create additional source files and import to this file if you wish.

COMP3702 Assignment 2 "Dragon Game" Support Code

Last updated by njc 30/08/23
"""


class Solver:

    def __init__(self, game_env: GameEnv, epsilon: float = 0.0001, gamma: float = 0.999, epsilon_pi: float = 0.001):
        self.game_env = game_env
        self.converged = False
        self.epsilon = epsilon 
        self.epsilon_pi = epsilon_pi
        self.gamma = gamma
        self.exit_terminal_state = GameState(self.game_env.exit_row, self.game_env.exit_col, tuple([1] * self.game_env.n_gems))
        

    @staticmethod
    def testcases_to_attempt():
        """
        Return a list of testcase numbers you want your solution to be evaluated for.
        """
        # TODO: modify below if desired (e.g. disable larger testcases if you're having problems with RAM usage, etc)
        return [1, 2, 3, 4, 5]

    # === Value Iteration ==============================================================================================

    def vi_initialise(self):
        """
        Initialise any variables required before the start of Value Iteration.
        """
        #
        # TODO: Implement any initialisation for Value Iteration (e.g. building a list of states) here. You should not
        #  perform value iteration in this method.
        #
        # In order to ensure compatibility with tester, you should avoid adding additional arguments to this function.
        #

        self.states = list(GameState(row, col, tuple(g)) for row in range(self.game_env.n_rows) 
                        for col in range(self.game_env.n_cols)
                        for g in product([1,0], repeat=self.game_env.n_gems)
                        if self.game_env.grid_data[row][col] not in self.game_env.COLLISION_TILES)
        
        self.cache = dict()
        self.valid_actions = dict()
        for s in self.states:
            self.valid_actions[s] = []
            for a in self.game_env.ACTIONS:
                valid = self.game_env.perform_action(s, a)[0]
                if valid: 
                    self.valid_actions[s].append(a)
                if (s,a) not in self.cache.keys():
                    self.cache[(s,a)] = ts.get_transition_outcomes_restricted(self.game_env, s, a) #lists of possible next state, reward, prob
        
        self.values = {s: 0 for s in self.states}
        self.policy = {s: 'wl' for s in self.states}
    

    def vi_is_converged(self):
        """
        Check if Value Iteration has reached convergence.
        :return: True if converged, False otherwise
        """
        #
        # TODO: Implement code to check if Value Iteration has reached convergence here.
        #
        # In order to ensure compatibility with tester, you should avoid adding additional arguments to this function.
        #
        return self.converged
    
    def vi_iteration(self): 
        delta = 0
        for s in self.states:
            best_q = - float('inf')
            best_a = None
            if self.game_env.grid_data[s.row][s.col] == self.game_env.LAVA_TILE or s == self.exit_terminal_state:
                continue
            for a in self.valid_actions[s]:
                q = 0
                for ns, rw, p in self.cache[(s,a)]:
                    q += p * (rw + (self.gamma * self.values[ns]))
                if q > best_q:
                    best_q = q
                    best_a = a
            diff = abs(self.values[s]-best_q)
            if diff > delta:
                delta = diff
            self.policy[s] = best_a
            self.values[s] = best_q
        if delta < self.epsilon:
            self.converged = True                 

    def vi_plan_offline(self):
        """
        Plan using Value Iteration.
        """
        # !!! In order to ensure compatibility with tester, you should not modify this method !!!
        self.vi_initialise()
        while True:
            self.vi_iteration()

            # NOTE: vi_iteration is always called before vi_is_converged
            if self.vi_is_converged():
                break

    def vi_get_state_value(self, state: GameState):
        """
        Retrieve V(s) for the given state.
        :param state: the current state
        :return: V(s)
        """
        #
        # TODO: Implement code to return the value V(s) for the given state (based on your stored VI values) here. If a
        #  value for V(s) has not yet been computed, this function should return 0.
        #
        # In order to ensure compatibility with tester, you should avoid adding additional arguments to this function.
        #
        return self.values[state]

    def vi_select_action(self, state: GameState):
        """
        Retrieve the optimal action for the given state (based on values computed by Value Iteration).
        :param state: the current state
        :return: optimal action for the given state (element of ROBOT_ACTIONS)
        """
        #
        # TODO: Implement code to return the optimal action for the given state (based on your stored VI values) here.
        #
        # In order to ensure compatibility with tester, you should avoid adding additional arguments to this function.
        #
        return self.policy[state]

    # === Policy Iteration =============================================================================================

    def pi_initialise(self):
        """
        Initialise any variables required before the start of Policy Iteration.
        """
        #
        # TODO: Implement any initialisation for Policy Iteration (e.g. building a list of states) here. You should not
        #  perform policy iteration in this method. You should assume an initial policy of always move FORWARDS.
        #
        # In order to ensure compatibility with tester, you should avoid adding additional arguments to this function.
        #
              #

        self.states = list(GameState(row, col, tuple(g)) for row in range(self.game_env.n_rows) 
                        for col in range(self.game_env.n_cols)
                        for g in product([1,0], repeat=self.game_env.n_gems)
                        if self.game_env.grid_data[row][col] not in self.game_env.COLLISION_TILES)
        
        self.cache = dict()
        self.valid_actions = dict()
        for s in self.states:
            self.valid_actions[s] = []
            for a in self.game_env.ACTIONS:
                valid = self.game_env.perform_action(s, a)[0]
                if valid: 
                    self.valid_actions[s].append(a)
                if (s,a) not in self.cache.keys():
                    self.cache[(s,a)] = ts.get_transition_outcomes_restricted(self.game_env, s, a) #lists of possible next state, reward, prob
        
        self.values = {s: 0 for s in self.states}
        self.policy = {s: 'wl' for s in self.states}

    def pi_is_converged(self):
        """
        Check if Policy Iteration has reached convergence.
        :return: True if converged, False otherwise
        """
        #
        # TODO: Implement code to check if Policy Iteration has reached convergence here.
        #
        # In order to ensure compatibility with tester, you should avoid adding additional arguments to this function.
        #
        return self.converged

    def pi_iteration(self):
        """
        Perform a single iteration of Policy Iteration (i.e. perform one step of policy evaluation and one step of
        policy improvement).
        """
        #
        # TODO: Implement code to perform a single iteration of Policy Iteration (evaluation + improvement) here.
        #
        # In order to ensure compatibility with tester, you should avoid adding additional arguments to this function.
        #
        self.pi_eval()
        return self.pi_improv()

    def pi_plan_offline(self):
        """
        Plan using Policy Iteration.
        """
        # !!! In order to ensure compatibility with tester, you should not modify this method !!!
        self.pi_initialise()
        while True:
            self.pi_iteration()

            # NOTE: pi_iteration is always called before pi_is_converged
            if self.pi_is_converged():
                break
        

    def pi_select_action(self, state: GameState):
        """
        Retrieve the optimal action for the given state (based on values computed by Value Iteration).
        :param state: the current state
        :return: optimal action for the given state (element of ROBOT_ACTIONS)
        """
        #
        # TODO: Implement code to return the optimal action for the given state (based on your stored PI policy) here.
        #
        # In order to ensure compatibility with tester, you should avoid adding additional arguments to this function.
        #
        return self.policy[state]

    # === Helper Methods ===============================================================================================
    #
    #
    # TODO: Add any additional methods here
    #
    #  
    def pi_eval(self):  
        val_conv = False
        while not val_conv: 
            delta = 0
            for s in self.states:
                a_val = 0 
                a = self.policy[s]
                if self.game_env.grid_data[s.row][s.col] == self.game_env.LAVA_TILE or s == self.exit_terminal_state:
                    continue
                for ns, rw, p in self.cache[(s,a)]:
                    a_val += p * (rw + self.gamma * self.values[ns])
                diff = abs(self.values[s]-a_val)
                if diff > delta:
                    delta = diff
                self.values[s] = a_val
            if delta < self.epsilon_pi:
                val_conv = True

    def pi_improv(self): 
        old_policy = self.policy.copy()
        for s in self.states:
            if self.game_env.grid_data[s.row][s.col] == self.game_env.LAVA_TILE or s == self.exit_terminal_state:
                    continue
            best_q = -float('inf')
            best_a = None
            for a in self.valid_actions[s]:
                q = 0 
                for ns,rw,p in self.cache[(s,a)]:
                    q += p * (rw + self.gamma * self.values[ns])
                if q > best_q:
                    best_a = a
                    best_q = q
            self.policy[s] = best_a
            
        if self.policy == old_policy:
            self.converged = True
        return self.converged

