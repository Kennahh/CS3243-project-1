from typing import List, Tuple, Set
import heapq
from enum import Enum
import json

def search(dct) -> list[int]:
    # YOUR CODE HERE. Do not change the name of the function.
    """
    Finds the optimal path or decision in a dungeon scenario based on the given game state.

    Parameters:
    - dct (dict): A dictionary containing the following keys:
        - "cols" (int): The number of columns in the dungeon grid.
        - "rows" (int): The number of rows in the dungeon grid.
        - "obstacles" (List[Tuple[int, int]]): A list of (x, y) positions that represent impassable obstacles.
        - "creeps" (List[List[int]]): A list of cells with creeps, where each entry is [x, y, num_creeps].
                                      All other non-obstacle positions not listed here contain 0 creeps.
        - "start" (Tuple[int, int]): The starting (x, y) position in the dungeon.
        - "goals" (List[Tuple[int, int]]): A list of (x, y) positions representing rune goal locations.
        - "num_flash_left" (int): The number of times the FLASH ability can be used.
        - "num_nuke_left" (int): The number of times the NUKE ability can be used.

    Returns:
    - List[int]: A list of integers representing the actions or steps taken as output from the search logic.
    """
    class Action(Enum):
        UP = 0
        DOWN = 1
        LEFT = 2
        RIGHT = 3
        FLASH = 4
        NUKE = 5

    rows = dct["rows"]
    cols = dct["cols"]
    obstacles = set(tuple(obstacle) for obstacle in dct["obstacles"])
    creeps = [{(creep[0], creep[1]): creep[2] for creep in dct["creeps"]}]
    start = tuple(dct["start"])
    goals = set(tuple(goal) for goal in dct["goals"])
    num_flash_left = dct["num_flash_left"]
    num_nuke_left = dct["num_nuke_left"]

    class Node:
        def __init__(self, status: tuple, previousNode: 'Node' = None, action: int = None, pathCost: int = 0, num_flash_used: int = 0, num_nuke_used: int = 0, creepsVersionNumber: int = 0):
            self.status = status
            self.previousNode = previousNode
            self.action = action
            self.pathCost = pathCost
            self.num_flash_used = num_flash_used
            self.num_nuke_used = num_nuke_used
            self.creepsVersionNumber = creepsVersionNumber
            # heuristic: minimum manhattan distance to any goal * 2 (relaxation: no creeps, no obstacles, each step costs 2)
            self.heuristic = min([abs(status[0]-goal[0]) + abs(status[1]-goal[1]) for goal in goals]) * 2

        def __lt__(self, anotherNode: 'Node'):
            return (self.pathCost + self.heuristic) < (anotherNode.pathCost + anotherNode.heuristic)
        
        def getState(self):
            return (self.status, self.num_flash_used, self.num_nuke_used, self.creepsVersionNumber)
        
    startNode = Node(start)
    frontier = []
    heapq.heappush(frontier, startNode)
    path = []
    reached = {startNode.getState(): startNode.pathCost}
    while (len(frontier) != 0):
        currentNode = heapq.heappop(frontier)
        row = currentNode.status[0]
        col = currentNode.status[1]
        currentCost = currentNode.pathCost

        #check whether it's one of the goal states, if yes, generate the path
        if (currentNode.status in goals):
            tempNode = currentNode
            while (tempNode.action != None):
                path.append(tempNode.action)
                tempNode = tempNode.previousNode
            path.reverse()
            break

        # if not goal: check possible regular actions first (up/down/left/right)
        for rowDistance, colDistance, action in [(-1,0, Action.UP.value), (1,0, Action.DOWN.value), (0,-1, Action.LEFT.value), (0,1, Action.RIGHT.value)]:
            newRow = row + rowDistance
            newCol = col + colDistance
            if (0 <= newRow < rows and 0 <= newCol < cols and (newRow, newCol) not in obstacles):
                cost = currentCost + 4
                if (newRow, newCol) in creeps[currentNode.creepsVersionNumber]:
                    cost += creeps[currentNode.creepsVersionNumber][(newRow, newCol)]
                newNode = Node((newRow, newCol), currentNode, action, cost, currentNode.num_flash_used, currentNode.num_nuke_used, currentNode.creepsVersionNumber)
                if (newNode.getState() not in reached or reached[newNode.getState()] > cost):
                    heapq.heappush(frontier, newNode)
                    reached[newNode.getState()] = cost
    
        # check whether can use skills (flash/nuke)
        if (currentNode.num_flash_used < num_flash_left):
            flashNode = Node((row, col), currentNode, Action.FLASH.value, currentCost+10, currentNode.num_flash_used+1, currentNode.num_nuke_used, currentNode.creepsVersionNumber)
            if (flashNode.getState() not in reached or reached[flashNode.getState()] > (currentCost+10)):
                    heapq.heappush(frontier, flashNode)
                    reached[flashNode.getState()] = currentCost+10
            # flash up
            if (row > 0):
                newRow = row - 1
                cost = currentCost + 10
                while (newRow >= 0):
                    if ((newRow, col) in obstacles):
                        break
                    cost = cost + 2 
                    if (newRow, col) in creeps[currentNode.creepsVersionNumber]:
                        cost += creeps[currentNode.creepsVersionNumber][(newRow, col)]
                    newRow -= 1
                newRow += 1
                newNode = Node((newRow, col), flashNode, Action.UP.value, cost, currentNode.num_flash_used+1, currentNode.num_nuke_used, currentNode.creepsVersionNumber)
                if (newNode.getState() not in reached or reached[newNode.getState()] > cost):
                    heapq.heappush(frontier, newNode)
                    reached[newNode.getState()] = cost
            # flash down
            if (row < rows-1):
                newRow = row + 1
                cost = currentCost + 10
                while (newRow < rows):
                    if ((newRow, col) in obstacles):
                        break
                    cost = cost + 2 
                    if (newRow, col) in creeps[currentNode.creepsVersionNumber]:
                        cost += creeps[currentNode.creepsVersionNumber][(newRow, col)]
                    newRow += 1
                newRow -= 1
                newNode = Node((newRow, col), flashNode, Action.DOWN.value, cost, currentNode.num_flash_used+1, currentNode.num_nuke_used, currentNode.creepsVersionNumber)
                if (newNode.getState() not in reached or reached[newNode.getState()] > cost):
                    heapq.heappush(frontier, newNode)
                    reached[newNode.getState()] = cost
            # flash left
            if (col > 0):
                newCol = col - 1
                cost = currentCost + 10
                while (newCol >= 0):
                    if ((row, newCol) in obstacles):
                        break
                    cost = cost + 2 
                    if (row, newCol) in creeps[currentNode.creepsVersionNumber]:
                        cost += creeps[currentNode.creepsVersionNumber][(row, newCol)]
                    newCol -= 1
                newCol += 1
                newNode = Node((row, newCol), flashNode, Action.LEFT.value, cost, currentNode.num_flash_used+1, currentNode.num_nuke_used, currentNode.creepsVersionNumber)
                if (newNode.getState() not in reached or reached[newNode.getState()] > cost):
                    heapq.heappush(frontier, newNode)
                    reached[newNode.getState()] = cost
            # flash right
            if (col < cols-1):
                newCol = col + 1
                cost = currentCost + 10
                while (newCol < cols):
                    if ((row, newCol) in obstacles):
                        break
                    cost = cost + 2 
                    if (row, newCol) in creeps[currentNode.creepsVersionNumber]:
                        cost += creeps[currentNode.creepsVersionNumber][(row, newCol)]
                    newCol += 1
                newCol -= 1
                newNode = Node((row, newCol), flashNode, Action.RIGHT.value, cost, currentNode.num_flash_used+1, currentNode.num_nuke_used, currentNode.creepsVersionNumber)
                if (newNode.getState() not in reached or reached[newNode.getState()] > cost):
                    heapq.heappush(frontier, newNode)
                    reached[newNode.getState()] = cost

        if (currentNode.num_nuke_used < num_nuke_left):
            currentCreeps = creeps[currentNode.creepsVersionNumber].copy() # copy of current version of creeps dictionary
            cost = currentCost + 50
            for creepPosition in currentCreeps:
                if ((abs(row-creepPosition[0]) + abs(col-creepPosition[1])) <= 10):
                    currentCreeps[creepPosition] = 0
            creeps.append(currentCreeps)
            # heapq.heappush(frontier, Node((row, col), currentNode.previousNode, Action.NUKE.value, cost, currentNode.num_flash_used, currentNode.num_nuke_used+1, currentCreeps))
            newNode = Node((row, col), currentNode, Action.NUKE.value, cost, currentNode.num_flash_used, currentNode.num_nuke_used+1, len(creeps)-1)
            if (newNode.getState() not in reached or reached[newNode.getState()] > cost):
                heapq.heappush(frontier, newNode)
                reached[newNode.getState()] = cost
            
    return path

    # pass

if __name__ == '__main__':
    file_path = 'project 1.2 test cases/correctness_public_b_small_8_19.json'
    with open(file_path, 'r') as f:
        dct = json.load(f)
    path = search(dct)
    print("Path found:", path)