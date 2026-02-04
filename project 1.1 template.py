from typing import List, Tuple, Set
from collections import deque
import heapq
import json

def dfs_search(dct) -> List[Tuple[int, int]]:
    """
    Input:
        dct: dictionary with keys
        - "description": str
        - "rows": int
        - "cols": int
        - "obstacles": List[Tuple[int, int]]
        - "start": Tuple[int, int]
        - "goals": List[Tuple[int, int]]
    """
    # YOUR CODE HERE. Do not change the name of the function.
    start = tuple(dct["start"])
    goals = set(tuple(goal) for goal in dct["goals"])
    obstacles = set(tuple(obstacle) for obstacle in dct["obstacles"])
    rows = dct["rows"]
    cols = dct["cols"]
    class Node:
        def __init__(self, status: tuple, previousNode: 'Node' = None):
            self.status = status
            self.previousNode = previousNode
        # def findPath(self):
        #     if (self.previousNode == None):
        #         print(self.status)
        #         return
        #     self.previousNode.findPath()
        #     print(self.status)

    startNode = Node(start)
    # print(startNode.status, startNode.previousNode)
    frontier = deque([startNode])
    reached = {startNode.status}
    path = []
    # case that has no legal path:
    if (start in obstacles):
        return path
    while (len(frontier) != 0):
        # print("looping")
        currentNode = frontier.pop()
        row = currentNode.status[0]
        col = currentNode.status[1]
        #check whether it's one of the goal states, if yes, generate the path
        if (currentNode.status in goals):
            # currentNode.findPath()
            tempNode = currentNode
            while (tempNode != None):
                path.append(tempNode.status)
                tempNode = tempNode.previousNode
            path.reverse()
            break
        # if not goal: check all possible actions (up/down/left/right)
        if (row-1 >= 0 and (row-1, col) not in obstacles): # up
            if ((row-1,col) not in reached):
                # newNode = Node((row-1, col), currentNode)
                # print(newNode.status)
                frontier.append(Node((row-1, col), currentNode))
                reached.add((row-1,col))
        if (row+1 < rows and (row+1, col) not in obstacles): #down
            if ((row+1,col) not in reached):
                frontier.append(Node((row+1, col), currentNode))
                reached.add((row+1,col))
        if (col-1 >= 0 and (row, col-1) not in obstacles): # left
            if ((row,col-1) not in reached):
                frontier.append(Node((row, col-1), currentNode))
                reached.add((row,col-1))
        if (col+1 < cols and (row, col+1) not in obstacles): # right
            if ((row,col+1) not in reached):
                frontier.append(Node((row, col+1), currentNode))
                reached.add((row,col+1))
    return path
    # pass


def bfs_search(dct) -> List[Tuple[int, int]]:
    """
    Input:
        dct: dictionary with keys
        - "description": str
        - "rows": int
        - "cols": int
        - "obstacles": List[Tuple[int, int]]
        - "start": Tuple[int, int]
        - "goals": List[Tuple[int, int]]
    """
    # YOUR CODE HERE. Do not change the name of the function.
    start = tuple(dct["start"])
    goals = set(tuple(goal) for goal in dct["goals"])
    obstacles = set(tuple(obstacle) for obstacle in dct["obstacles"])
    rows = dct["rows"]
    cols = dct["cols"]
    class Node:
        def __init__(self, status: tuple, previousNode: 'Node' = None):
            self.status = status
            self.previousNode = previousNode

    startNode = Node(start)
    frontier = deque([startNode])
    reached = {startNode.status}
    path = []
    if (start in obstacles):
        return path
    while (len(frontier) != 0):
        currentNode = frontier.popleft()
        row = currentNode.status[0]
        col = currentNode.status[1]
        #check whether it's one of the goal states, if yes, generate the path
        if (currentNode.status in goals):
            tempNode = currentNode
            while (tempNode != None):
                path.append(tempNode.status)
                tempNode = tempNode.previousNode
            path.reverse()
            break
        # if not goal: check all possible actions (up/down/left/right)
        for rowDistance, colDistance in [(-1,0), (1,0), (0,-1), (0,1)]:
            newRow = row + rowDistance
            newCol = col + colDistance
            if (0 <= newRow < rows and 0 <= newCol < cols and (newRow, newCol) not in obstacles and (newRow, newCol) not in reached):
                frontier.append(Node((newRow, newCol), currentNode))
                reached.add((newRow, newCol))
    return path
    # pass


def ucs_search(dct) -> List[Tuple[int, int]]:
    """
    Input:
        dct: dictionary with keys
        - "description": str
        - "rows": int
        - "cols": int
        - "obstacles": List[Tuple[int, int]]
        - "start": Tuple[int, int]
        - "goals": List[Tuple[int, int]]
    """
    # YOUR CODE HERE. Do not change the name of the function.
    start = tuple(dct["start"])
    goals = set(tuple(goal) for goal in dct["goals"])
    obstacles = set(tuple(obstacle) for obstacle in dct["obstacles"])
    rows = dct["rows"]
    cols = dct["cols"]
    class Node:
        def __init__(self, status: tuple, previousNode: 'Node' = None, cost: int = 0):
            self.status = status
            self.previousNode = previousNode
            self.cost = cost

        def __lt__(self, anotherNode):
            return self.cost < anotherNode.cost
            
    startNode = Node(start)
    frontier = []
    heapq.heappush(frontier, startNode)
    reached = {startNode.status: startNode.cost} # reached is a dictionary with node position as key and path cost as value
    path = []
    if (start in obstacles):
        return path
    while (len(frontier) != 0):
        currentNode = heapq.heappop(frontier)
        row = currentNode.status[0]
        col = currentNode.status[1]
        currentCost = currentNode.cost
        #check whether it's one of the goal states, if yes, generate the path
        if (currentNode.status in goals):
            tempNode = currentNode
            while (tempNode != None):
                path.append(tempNode.status)
                tempNode = tempNode.previousNode
            path.reverse()
            break
        # if not goal: check all possible actions (up/down/left/right)
        for rowDistance, colDistance in [(-1,0), (1,0), (0,-1), (0,1)]:
            newRow = row + rowDistance
            newCol = col + colDistance
            if (0 <= newRow < rows and 0 <= newCol < cols and (newRow, newCol) not in obstacles):
                if ((newRow, newCol) not in reached or reached[(newRow, newCol)] > currentCost+1):
                    heapq.heappush(frontier, Node((newRow, newCol), currentNode, currentCost+1))
                    reached[(newRow, newCol)] = currentCost + 1
    return path
    # pass

if __name__ == '__main__':
    file_path = 'project 1.1 test cases/correctness_public_ab_small_1_99.json'
    with open(file_path, 'r') as f:
        dct = json.load(f)
    path = ucs_search(dct)
    print("Path found:", path)
        
    