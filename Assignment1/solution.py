from game_env import GameEnv
from game_state import GameState
import heapq
import time
import math


"""
solution.py

This file is a template you should use to implement your solution.

You should implement each of the method stubs below. You may add additional methods and/or classes to this file if you 
wish. You may also create additional source files and import to this file if you wish.

COMP3702 Assignment 1 "Dragon Game" Support Code

Last updated by njc 07/08/23
"""
class Node: # can get the state of the current node
    #node in the container (frontier/fringe)
    #stores: 
    #current state
    #the actions
    #the costs 


    def __init__(self, state, parent, action_from_parent, cost: int, game_env, heuristic_cost: int = 0): 
        self.state = state #game_state object

        self.parent = parent #node class
        self.action_from_parent = action_from_parent

        self.game_env = game_env
        
        self.cost = cost  #cost up til current step 
        self.cost_with_heuristic = cost + heuristic_cost

    def __lt__(self, other_node): #less than operator-> to prioritse nodes 
        return self.cost_with_heuristic < other_node.cost_with_heuristic


    def get_successors(self, game_env): #get fringe of current state
        """
        returns a list of successor nodes with new cost 
        """
        successors = []
        for action in game_env.ACTIONS:
            success, new_state = self.game_env.perform_action(self.state, action)
            if success == True:
                 action_cost = game_env.ACTION_COST[action]
                 new_node = Node(new_state, self, action, self.cost + action_cost, game_env) #self is parent node.
                 successors.append(new_node)
        return successors
    
    def get_successors_A_star(self, game_env, solver): #get fringe of current state
        """
        returns a list of successor nodes with new cost 
        """
        successors = []
        for action in game_env.ACTIONS:
            success, new_state = self.game_env.perform_action(self.state, action)
            
            if success == True:
                 heuristic_cost = solver.compute_heuristic(new_state)

                 action_cost = game_env.ACTION_COST[action]
                 new_node = Node(new_state, self, action, self.cost + action_cost, game_env, heuristic_cost) #self is parent node.
                 successors.append(new_node)
        return successors


class Solver:

    def __init__(self, game_env):
        self.game_env = game_env
        self.priority_queue = None #self.preprocess_heuristic() #list with index of nodes in gem_position
        self.preprocess = False
    
        #
        #
        # TODO: Define any class instance variables you require here (avoid performing any computationally expensive
        #  heuristic preprocessing operations here - use the preprocess_heuristic method below for this purpose).
        #
        #
    

    # === Uniform Cost Search ==========================================================================================
    def search_ucs(self):
        """
        Find a path which solves the environment using Uniform Cost Search (UCS).
        :return: path (list of actions, where each action is an element of GameEnv.ACTIONS)
        """
        init_state = self.game_env.get_init_state()
        start_node = Node(init_state, None, None, 0, self.game_env)

        visited = {} #keys are states, values are the costs of getting there from initial node (dictionary)
    
        heap = [start_node] 
        heapq.heapify(heap) #heap will sort our priority queue correctly. 

        while len(heap) > 0: 
            curr_node = heapq.heappop(heap)
    
            if self.game_env.is_solved(curr_node.state) == True:
               
                actions = []
                while curr_node.action_from_parent is not None:
                    actions.append(curr_node.action_from_parent)
                    curr_node = curr_node.parent
                print(len(heap))
                return actions[::-1]
            
            successors = curr_node.get_successors(self.game_env)
 
            for next_node in successors: 
            
                if next_node.state not in visited.keys() or visited[next_node.state] > next_node.cost: 
                    visited[next_node.state] = next_node.cost
                    heapq.heappush(heap, next_node)


    # === A* Search ====================================================================================================
    def preprocess_heuristic(self): #find closest nodes wrt to the chosen heuristic. 
        """
        Perform pre-processing (e.g. pre-computing repeatedly used values) necessary for your heuristic,
        """

        #
        #
        # TODO: (Optional) Implement code for any preprocessing required by your heuristic here (if your heuristic
        #  requires preprocessing).
        #
        # If you choose to implement code here, you should call this method from your search_a_star method (e.g. once at
        # the beginning of your search).
        #
        #


        init_col = self.game_env.get_init_state().col
        init_row = self.game_env.get_init_state().row
       
        dist = [(math.sqrt((init_col-self.game_env.gem_positions[i][1])**2 + (init_row-self.game_env.gem_positions[i][0])**2), i) for i in range(len(self.game_env.gem_positions))]
        heapq.heapify(dist)

        gem_index0 = heapq.heappop(dist)[1] #(distance, gem_index)
        gem_pri = [gem_index0]

        while len(gem_pri) !=  self.game_env.n_gems: 
            closest_gem_index = heapq.heappop(dist)[1]
            curr_gem = self.game_env.gem_positions[closest_gem_index]
            
            if closest_gem_index not in gem_pri: 
                col_temp = curr_gem[1]
                row_temp =  curr_gem[0]

                gem_pri.append(closest_gem_index)
        
                #create new dist-heap in order to extract the minimal distance
                dist = [(math.sqrt((col_temp-self.game_env.gem_positions[i][1])**2 + (row_temp-self.game_env.gem_positions[i][0])**2), i) for i in range(len(self.game_env.gem_positions))]
                heapq.heapify(dist)
        
        self.priority_queue = gem_pri 
    
    
    def get_closest_gem(self, state):
        i = 0
        closest_index = self.priority_queue[i]  
            
        while state.gem_status[closest_index] == 1:
            i += 1
            if i == self.game_env.n_gems or closest_index == None: #if all gems are picked up
                return (self.game_env.exit_row, self.game_env.exit_col)
            closest_index = self.priority_queue[i]

        return self.game_env.gem_positions[closest_index]

    def compute_heuristic(self, state): #closest gem: index of closest gem in gem_positions 
        """
        Compute a heuristic value h(n) for the given state.
        :param state: given state (GameState object)
        :return a real number h(n)
        """

        #
        #
        # TODO: Implement your heuristic function for A* search here. Note that your heuristic can be tested on
        #  gradescope even if you have not yet implemented search_a_star.
        #
        # You should call this method from your search_a_star method (e.g. every time you need to compute a heuristic
        # value for a state).
        #
        curr_col = state.col
        curr_row = state.row
        
        closest_gem = self.get_closest_gem(state)
        
        return math.sqrt((curr_col-closest_gem[1])**2 + (curr_row-closest_gem[0])**2)*0.2
    

    def search_a_star(self):
        """
        Find a path which solves the environment using A* Search.
        :return: path (list of actions, where each action is an element of GameEnv.ACTIONS)
        """
        if self.preprocess == False: 
            self.priority_que = self.preprocess_heuristic()
            self.preprocess == True

        start_state = self.game_env.get_init_state()
        start_node = Node(start_state, None, None, 0, self.game_env)

        visited = {} #keys are states, values are the costs of getting there from initial node (dictionary)
    
        heap = [start_node] 
        heapq.heapify(heap) #heap will sort our priority queue correctly. 
        while len(heap) > 0: 
            
            curr_node = heapq.heappop(heap)
            if self.game_env.is_solved(curr_node.state) == True:
       
                actions = []
                while curr_node.action_from_parent is not None:
                    actions.append(curr_node.action_from_parent)
                    curr_node = curr_node.parent
                print(len(heap))
                return actions[::-1]
    
            successors = curr_node.get_successors_A_star(self.game_env, self)
 
            for next_node in successors: 
                if next_node.state not in visited.keys() or visited[next_node.state] > next_node.cost_with_heuristic: 
                    visited[next_node.state] = next_node.cost_with_heuristic
                    heapq.heappush(heap, next_node)

        


        
