from __future__ import annotations
import random
import numpy as np
import time
from collections import deque
from typing import List, Tuple
import sys

BIG_COST = 9999999999999
PHEROMONE_MAX = 0.99
PHEROMONE_MIN = 0.01

def read_input_file():
    # Read the number of customers
    n = int(input().strip())

    # Initialize lists for e, l, and d
    e, l, d = [], [], []

    # Read the e, l, d values for each customer
    for i in range(n):
        ei, li, di = map(int, input().split())
        e.append(ei)
        l.append(li)
        d.append(di)

    # Initialize a matrix for t (travel times between points)
    t = []

    # Read the travel time matrix t
    for i in range(n + 1):
        t_row = list(map(int, input().split()))
        t.append(t_row)

    # Return the parsed values
    return n, e, l, d, t

def read_input_from_file(filename='TSPTW_test_1.txt'):
    '''
    This function reads an input file for the TSPTW problem.
    If successful, this returns a tuple (N, e, l, d, t) where:
        + N is the number of points to visit
        + e and l contain the starts and ends of N time windows
        + d is the service times at N points
        + t is the travel time matrix, size (N+1) x (N+1)
    '''
    try:
        with open(filename, 'r') as file_handle:
            # Read all lines from the file and strip whitespace
            content = [line.strip() for line in file_handle.readlines() if line.strip()]

            # Ensure there is at least one line for the number of points
            if not content:
                raise ValueError("Input file is empty or not formatted correctly.")

            # Read the number of points (N)
            N = int(content[0])

            # Initialize lists for e, l, and d
            e, l, d = [], [], []

            # Parse the time window and service time data for N points
            for i in range(1, N + 1):
                ei, li, di = map(int, content[i].split())
                e.append(ei)
                l.append(li)
                d.append(di)

            # Parse the travel time matrix (N+1 x N+1)
            t = []
            for i in range(N + 1):
                t_row = list(map(int, content[N + 1 + i].split()))
                if len(t_row) != N + 1:
                    raise ValueError("Travel time matrix row size mismatch.")
                t.append(t_row)

            return N, e, l, d, t

    except FileNotFoundError:
        print(f"Error: The file '{filename}' was not found.")
        return None
    except ValueError as ve:
        print(f"Value Error: {ve}")
        return None
    except Exception as ex:
        print(f"An unknown error occurred: {ex}")
        return None

if len(sys.argv) > 1:
    n, e, l, d, t = read_input_from_file(sys.argv[1])
else:
    n, e, l, d, t = read_input_file()

# Precalculate the variables necessary for the calculation of the heuristic values
lambda_t, lambda_l, lambda_e = 0.75, 0.1, 0.15
min_e, max_e, min_l, max_l, min_t, max_t = min(e), max(e), min(l), max(l), min([min([item if item > 0 else BIG_COST for item in row]) for row in t]), max([max(row) for row in t])
lambda_heuristics = [[0 for i in range(n+1)] for j in range(n+1)]
for i in range(n+1):
    for j in range(n+1):
        lambda_heuristics[i][j] = ((max_e - e[j-1])/(max_e - min_e), (max_l - l[j-1])/(max_l - min_l), (max_t - t[i][j])/(max_t - min_t))
e_temp = [0] + e
l_temp = [BIG_COST] + l
proximity = np.array([[min(l_temp[j], l_temp[i] + t[i][j]) - max(e_temp[j], e_temp[i] + t[i][j]) for j in range(n+1)] for i in range(n+1)])
max_abs_proximity = max([max([abs(proximity[i][j]) for j in range(n+1) if j!=i]) for i in range(n+1)])
# Apply a scaling function to the proximity matrix
proximity = 1 /( 1 + np.exp(-proximity/(max_abs_proximity/10)))
# print(proximity)
temp_good_paths = []

pheromone = [[0.5 for i in range(n+1)] for j in range(n+1)]


def Calculate(path:List[int]):
    cur_pos = 0
    total_time = 0
    travel_time = 0
    for i in range (0, n):
        total_time += t[cur_pos][path[i]]
        travel_time += t[cur_pos][path[i]]
        if total_time <= l[path[i]-1]:
            total_time = max(total_time, e[path[i]-1])
            total_time += d[path[i]-1]
            cur_pos = path[i]
        else:
            return BIG_COST
    return travel_time

def lex_compare(path1:List[int], path2:List[int]) -> bool:
    if path2 == None:
        return True
    total_time1, total_time2 = 0, 0
    travel_time1, travel_time2 = 0, 0
    violations_count1, violations_count2 = 0, 0
    cur_pos = 0
    for i in range (0, n):
        total_time1 += t[cur_pos][path1[i]]
        travel_time1 += t[cur_pos][path1[i]]

        total_time1 = max(total_time1, e[path1[i]-1])
        total_time1 += d[path1[i]-1]
        if total_time1 > l[path1[i] - 1]:
            violations_count1 += 1
        cur_pos = path1[i]
    cur_pos = 0
    for i in range (0, n):
        total_time2 += t[cur_pos][path2[i]]
        travel_time2 += t[cur_pos][path2[i]]

        total_time2 = max(total_time2, e[path2[i]-1])
        total_time2 += d[path2[i]-1]
        if total_time2 > l[path2[i]-1]:
            violations_count2 += 1
        cur_pos = path2[i]
    return violations_count1 < violations_count2 or (violations_count1 == violations_count2 and travel_time1 < travel_time2)

def LocalSearch(start_path:List[int], enhancement:bool=False, allowed_time:int=None, accepted_delay:int=None):
    tabu = deque()
    tabu.append((1, start_path))
    run_time = 2
    time_since_best = time.time()
    start_time = time_since_best
    depth = 6 if n <= 30 else (2 if n <= 300 else 1)
    vertex_check = n // 2 if n < 100 else (n // 6 if n <= 300 else n // 5)
    optimal_path = start_path
    cur_MIN = Calculate(start_path)

    while len(tabu) > 0:
        element = tabu.popleft()  # This pops the first inserted item
        if element[0] <= depth:
            cur_best_element = []
            found_better = False
            for i in range (0, n - 1):
                for j in range (i + 1, min(i + vertex_check, n)):
                    try_path = element[1][:]
                    try_path = try_path[:i] + try_path[i + 1:j] + try_path[i:i+1] + try_path[j:]
                    # travel_time = Calculate(try_path)
                    # if travel_time < cur_MIN:
                    if lex_compare(try_path, optimal_path):
                        found_better = True
                        cur_best_element = []
                        cur_best_element.append((0, try_path[:]))
                        optimal_path = try_path[:]
                        if enhancement:
                            temp_good_paths.append(try_path)
                        # cur_MIN = travel_time
                        cur_MIN = Calculate(try_path)
                        # print(cur_MIN)
                        time_since_best = time.time()
                    elif Calculate(try_path) == cur_MIN:
                        cur_best_element.append((0, try_path))
                    else: cur_best_element.append((element[0] + 1, try_path))
                    time_passed = time.time() - time_since_best
                    if time_passed > accepted_delay or (allowed_time != None and time.time() - start_time > allowed_time):
                        break
            if found_better == True and len(cur_best_element) > 0:
                tabu.clear()
            for i in cur_best_element:
                tabu.append(i)
            if len(tabu) > 1000000:
                # print('pop')
                for _ in range(500000):
                    tabu.popleft()
            # print(cur_MIN)
        time_passed = time.time() - time_since_best
        if time_passed > accepted_delay or (allowed_time != None and time.time() - start_time > allowed_time):
            break
    return optimal_path

class Node:
    def __init__(self, value, parent):
        self.Children: List[Node] = [] # list of child nodes of the current nodes
        self.extensions:set = None # Set of nodes that can be extend from this node
        if value == 0: # Initialize the extensions set for the root node of the tree
            self.extensions = set(range(1, n + 1))
        self.value:int = value # The value ranging from 0 (only the first node of the tree) to n
        self.parent:Node = parent # The parent Node

        self.h_value:float = None
        self.rank_sum:int = 0
        self.times_passed:int = 0
        self.violations_count:int = 0
        self.travel_time:int = 0
    def AddChild(self, child_value:int, child_h_value:float, child_rank_sum:int, child_times_passed:int, child_violations_count:int, travel_time:int):
        child = Node(child_value, self)
        child.extensions = (self.extensions - set([child_value]))
        child.h_value = child_h_value
        child.rank_sum = child_rank_sum
        child.times_passed = child_times_passed
        child.violations_count = child_violations_count
        child.travel_time = travel_time
        self.Children.append(child)

    def CalculateRankSum(self):
        if len(self.Children) == 0:
            return
        self.Children.sort(key=lambda item:item.h_value)
        # ranks = sorted([child for child in self.Children], key=lambda item:item.h_value)
        for i in range(len(self.Children)-1, -1, -1):
            self.Children[i].rank_sum = self.rank_sum + (len(self.Children) - i)
    def __str__(self):
        if self.parent == None:
            return f'value({self.value}):parent(None):h_value({self.h_value}):rank_sum({self.rank_sum}):times_passed({self.times_passed}):violations_count({self.violations_count}):travel_time({self.travel_time})'
        return f'value({self.value}):parent({self.parent.value}):h_value({self.h_value}):rank_sum({self.rank_sum}):times_passed({self.times_passed}):violations_count({self.violations_count}):travel_time({self.travel_time})'
    def __lt__(self, other:Node) -> bool:
        return (other==None) or (self.violations_count < other.violations_count) or (self.violations_count == other.violations_count and self.travel_time < other.travel_time)
    def __gt__(self, other:Node) -> bool:
        return other < self

def calculate_heuristic(parent:Node, new_value:int):
    if parent == None: # When the first Node of the Tree is created, there is no further information
        return 0
    # We can also generate random values for the three lambdas during each calculation, but I did experiment and found that the tuple (0.15, 0.1, 0.75) initialized globally works best
    eta = lambda_e * lambda_heuristics[parent.value][new_value][0] + lambda_l * lambda_heuristics[parent.value][new_value][1] + lambda_t * lambda_heuristics[parent.value][new_value][2] + 0.00001
    pheromone_value = pheromone[parent.value][new_value]
    times_passed = max((parent.times_passed + t[parent.value][new_value]), e[new_value - 1]) # The total time passed before getting to the point new_value
    v = 0 # Check if putting the new node in the path creates a new violation
    # print(times_passed)
    if times_passed > l[new_value - 1]:
        v = 1
    return (eta * pheromone_value , 0, times_passed, parent.violations_count + v, parent.travel_time + t[parent.value][new_value])

def path_from_leave(leave:Node):
    pointer = leave
    temp_path = [pointer.value]
    while pointer.parent != None:
        temp_path.append(pointer.parent.value)
        pointer = pointer.parent
    return temp_path[::-1][1:]

class Tree:
    def __init__(self, k_bw:int, muy:float, N_s:int, q0:float=0.5):
        self.root = Node(0, None)
        self.leaves = [self.root] # This list will store the leave nodes of the tree after every step
        self.heuristics: List[Tuple[Node, int, Tuple[float, int, int, int, int]]] = [] # (Node, new, h) This list stores the calculated heuristics after each expansion step
        self.k_bw = k_bw
        self.muy = muy
        self.N_s = N_s
        self.q0 = q0
        self.strict = True # This guarantee any path generated doesn't violate time constraints. If every path found after expansion violates time window constraints, then this will automatically be set to False

    def reset_leaves(self): # Reset the children and extensions of leaves to save memory, else the program will crash with n >= 100
        for leave in self.leaves:
            leave.Children = []
            leave.extensions = {}

    def expand(self):
        self.heuristics = []
        for leave_node in self.leaves:
            for new in leave_node.extensions:
                self.heuristics.append((leave_node, new, calculate_heuristic(leave_node, new)))
        if self.strict:
            # print(f'current len is: {len(self.heuristics)}')
            self.heuristics = [item for item in self.heuristics if item[2][3] == 0]
            # print(len(self.heuristics))
            if len(self.heuristics) == 0:
                self.strict = False
                self.expand()
                return
        self.heuristics.sort(key=lambda item:item[2][0]) # Sort by the product of the pheromone*eta function
        new_leaves = []
        q = random.random()
        if q < self.q0:
            # print("Expanding deterministically")
            # Select the best k_bw new possible nodes to expand
            self.heuristics = self.heuristics[-min(int(self.muy * len(self.leaves))+1, len(self.heuristics)):]

        else:
            # print("Expanding using weights for random choices")
            # Select from heuristics list extensions with corresponding weights, no replacement
            S = sum([item[2][0] for item in self.heuristics])
            chosen = np.random.choice(len(self.heuristics), p=[item[2][0]/S for item in self.heuristics], size=min(int(self.muy * len(self.leaves))+1, len(self.heuristics)), replace=False)
            temp = []
            for choice in chosen:
                temp.append(self.heuristics[choice])
            self.heuristics = temp

        for extension in self.heuristics:
            extension[0].AddChild(extension[1], extension[2][0], extension[2][1], extension[2][2], extension[2][3], extension[2][4]) # Add a child to the best leave nodes
            new_leaves.append(extension[0].Children[-1]) # Add the previously added child to the list of new leaves
        for leave in self.leaves:
            leave.CalculateRankSum()
        self.reset_leaves()
        self.leaves = new_leaves
        # Modify the leaves array
    def shrink(self):
        self.leaves.sort(key=lambda item:(item.violations_count, item.rank_sum, item.travel_time))
        self.leaves = self.leaves[:self.k_bw]
    def __str__(self):
        return ''

class BeamSolver:
    def __init__(self, k_bw:int, muy:float, N_s:int, q0:float=0.5):
        self.k_bw = k_bw
        self.muy = muy
        self.N_s = N_s
        self.q0 = q0
        self.found_paths = []
    def solve(self):
        self.solver_tree = Tree(self.k_bw, self.muy, self.N_s, self.q0)
        for _ in range(1, n+1):
            self.solver_tree.expand()
            self.solver_tree.shrink()
        # print(self.solver_tree)
        # print('The final leaves of the trees are:')
        # for leave in self.solver_tree.leaves:
        #     print(leave)
        self.solver_tree.leaves.sort()
        for leave in self.solver_tree.leaves:
            self.found_paths.append(path_from_leave(leave))

def ApplyPheromoneUpdate(good_paths:List[List], weights:List[float]=None, ro:float=0.1):
    if weights == None:
        weights = [1/len(good_paths) for _ in range(len(good_paths))]
    assert len(good_paths) == len(weights)
    for i in range(n+1):
        for j in range(n+1):
            pheromone[i][j] = max(PHEROMONE_MIN,  (1-ro)*pheromone[i][j])
    for i in range(len(good_paths)):
        pheromone[0][good_paths[i][0]] = min(pheromone[0][good_paths[i][0]] + ro*weights[i], PHEROMONE_MAX)
        for j in range(0, n - 1):
            pheromone[good_paths[i][j]][good_paths[i][j+1]] = min(pheromone[good_paths[i][j]][good_paths[i][j+1]] + ro*weights[i], PHEROMONE_MAX)

def ConvergenceFactor() -> float:
    current_sum = 0
    for i in range(n+1):
        for j in range(n+1):
            current_sum += max(PHEROMONE_MAX- pheromone[i][j], pheromone[i][j] - PHEROMONE_MIN)
    current_sum /= (n+1)*(n+1)*(PHEROMONE_MAX - PHEROMONE_MIN)
    return 2 * (current_sum - 0.5)

class ACOSolver:
    def __init__(self, k_bw:int, muy:float, N_s:int, q0:float=0.5):
        self.N_s = N_s
        self.k_bw = k_bw
        self.muy = muy
        self.q0 = q0
        self.leave_P_bf = None
        self.leave_P_rb = None
        self.path_ib = None
        self.path_rb = None
        self.best_path = None
        self.last_cf = 0
        self.cf = 0 # convergence factor
        self.bs_update = False
        self.solution_time = 300 # The time that the algorithm is allowed to run, 300 seconds by default
        self.setParameters() # Set necessary parameters for the ACO algorithm
    def setParameters(self, ro=0.1, K_iter=0.2, K_restart=0.3, K_bf = 0.5):
        # print(K_iter, K_restart, K_bf)
        self.ro = ro
        self.K_iter = K_iter
        self.K_restart = K_restart
        self.K_bf = K_bf

    def setSolutionTime(self, solution_time:int):
        assert solution_time > 0 and solution_time <= 300
        self.solution_time = solution_time
    def solve(self):
        global temp_good_paths
        path_greedy_e = [x[0] for x in sorted([(i+1, e[i]) for i in range(n)], key=lambda item:item[1])]
        # print(Calculate(path_greedy_e))
        self.best_path = path_greedy_e
        self.time_best_path = 0
        start_loop = time.time()
        iteration = 0

        while time.time() - start_loop < self.solution_time:
            # print(f'Current iteration #{iteration}')
            if iteration % 5 == 1:
                self.best_path = LocalSearch(self.best_path, enhancement=True, allowed_time=self.solution_time - (time.time() - start_loop), accepted_delay=5)
            beamSolver = BeamSolver(self.k_bw, self.muy, self.N_s, self.q0)
            beamSolver.solve()
            leave_P_ib = beamSolver.solver_tree.leaves[0]
            self.path_ib = path_from_leave(leave_P_ib)
            # Local search here
            self.path_ib = LocalSearch(self.path_ib, enhancement=leave_P_ib.violations_count < 10, allowed_time=self.solution_time - (time.time() - start_loop), accepted_delay=1)
            # Update the restart-best path and best path using iteration-best path
            if lex_compare(self.path_ib, self.path_rb):
                self.path_rb = self.path_ib
            if lex_compare(self.path_ib, self.best_path):
                # print(self.path_ib, self.best_path)
                self.best_path = self.path_ib
                self.time_best_path = time.time() - start_loop

            self.last_cf = self.cf
            self.cf = ConvergenceFactor()
            if self.bs_update and abs(self.cf - self.last_cf) < 0.0001:
                # Reset the pheromone matrix
                for i in range(n+1):
                    for j in range(n+1):
                        pheromone[i][j] = 0.5
                self.path_rb = None
            else:
                if len(temp_good_paths) > 0:
                    # print(len(temp_good_paths))
                    ApplyPheromoneUpdate(temp_good_paths)
                    temp_good_paths = []
                if abs(self.cf - self.last_cf) < 0.0001: self.bs_update = True
                ApplyPheromoneUpdate([self.path_ib, self.path_rb, self.best_path], [self.K_iter, self.K_restart, self.K_bf])
            iteration += 1


ACO = ACOSolver(1000, 2, 0, 0.6)
ACO.setSolutionTime(30)
ACO.setParameters(K_iter=0.5, K_restart=0.2, K_bf=0.3, ro=0.3)
ACO.solve()

print(n)
print(*ACO.best_path)
# print(Calculate(ACO.best_path))
# print(ACO.time_best_path)
