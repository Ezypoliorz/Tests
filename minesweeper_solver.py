# A script that solves a Minesweeper grid
# Uses the small game from minesweeper.py, refer to this script for further details on the game itself
# This solver's algorithm is, I believe, very inefficient as for each chunk, the amount of computation grows exponentially with the number of cells in the chunk

import random
import arcade
import minesweeper

class LogicSolver :
    def __init__(self, grid) :
        self.grid = grid
        self.maxGroupSize = 20 # Limits the cell chuncks to 20 cells

    def getBorderCells(self) : # Finds the hidden cells next to revealed cells (the "borders")
        borderCells = set() # Using a set guarantees that there are no duplicates, if a hidden cell is next to multiple values
        for row in self.grid :
            for cell in row :
                if not cell.hidden and cell.value > 0 :
                    # If one of the surrounding cells is hidden and isn't flagged, it is added to borderCells
                    for neighbor in cell.getSurroundingCells(grid = self.grid) :
                        if neighbor.hidden and not neighbor.flag :
                            borderCells.add(neighbor)
        return list(borderCells)

    def getGroups(self, borderCells) : # Divides the "border" cells into chuncks, to optimize computation
        groups = []
        unvisited = set(borderCells)

        while unvisited :
            # Creates a new empty group
            currentGroup = set()

            # Picks a random cell to start the search from
            stack = [unvisited.pop()]

            while stack :
                cell = stack.pop()
                currentGroup.add(cell) # Adds the cell to the group

                # Looks at all the revealed numbers next to that cell
                for numCell in self.getRelevantNumberedCells([cell]) :
                    # For each number, looks ath the cells around it : if two hidden cells are next to a common number, they belong to the same group
                    for neighbor in numCell.getSurroundingCells(grid = self.grid) :
                        # If one of the surrounding cells has not been visited, removes it from unvisited and adds it to the stack
                        if neighbor in unvisited :
                            unvisited.remove(neighbor)
                            stack.append(neighbor)

            # When the stack is empty, the group is finished and isolated from the others
            groups.append(list(currentGroup))

        return groups

    def getRelevantNumberedCells(self, cells) : # For a given hidden cell, outputs the values surrounding it, to find the constraints applying to the group
        relevant = set()
        for cell in cells :
            for neighbor in cell.getSurroundingCells(grid = self.grid) :
                # If the neighbor cell is revealed and contains a value, adds it to the list of constraints for teh group
                if not neighbor.hidden and neighbor.value is not None :
                    relevant.add(neighbor)
        return list(relevant)

    def findTrivialMoves(self) : # Gets the obvious configurations out of the way quickly
        moves = []
        for row in self.grid :
            for cell in row :
                if not cell.hidden and cell.value > 0 :
                    surrounding = cell.getSurroundingCells(grid = self.grid)
                    hiddenNeighbors = [n for n in surrounding if n.hidden and not n.flag]
                    flagsAround = sum(1 for n in surrounding if n.flag)
                    
                    if cell.value - flagsAround == len(hiddenNeighbors) and len(hiddenNeighbors) > 0 : # The number of surrounding hidden cells is equal the the number of mines
                        # Flags the surrounding hidden cells
                        for n in hiddenNeighbors :
                            moves.append((n, "FLAG"))
                    
                    elif cell.value == flagsAround and len(hiddenNeighbors) > 0 : # All the surrounding mines have been flagged
                        # Reveals all the other hidden surrounding cells
                        for n in hiddenNeighbors :
                            moves.append((n, "REVEAL"))

        return moves
    
    def isConfigurationValid(self, currentConfig, cells, relevantNums) : # Figures out if a hypothetical mines configuration is possible
        # Temporarily associates a state (0 = safe / 1 = mine) to each cell of the group
        assignment = {cells[i] : currentConfig[i] for i in range(len(currentConfig))}

        # For each mine, checks is the number of mines (flagged and simulated) surrounding a cell is equal to its value
        for numCell in relevantNums :
            surrounding = numCell.getSurroundingCells(grid = self.grid)
            minesFound = 0
            hiddenPotential = 0
            for n in surrounding :
                if not n.hidden :
                    if n.mine : minesFound += 1
                elif n.flag : minesFound += 1
                elif n in assignment :
                    if assignment[n] == 1 : minesFound += 1
                else :
                    hiddenPotential += 1
            if minesFound > numCell.value or (minesFound + hiddenPotential) < numCell.value :
                return False
        return True

    def backtrack(self, index, cells, relevantNums, currentConfig, validConfigs) : # Generates every possible valid configuration for a group of cells
        # If the current hypothetical configuration contradicts the values, stops searching in that direction
        if not self.isConfigurationValid(currentConfig, cells, relevantNums) :
            return
        
        # If the index is equal to the total number of tiles, a possible hypothesis has been made for each one
        if index == len(cells) :
            validConfigs.append(list(currentConfig))
            return
        
        # Otherwise, makes a hypothesis
        for val in [0, 1] : # Tests if it can be a safe cell (0) and can be a mine (1)
            # Adds the current supposition to the hypothetical configuration
            currentConfig.append(val)

            # Calls itself to make the following hypothesis or add the configuration if it is valid
            self.backtrack(index + 1, cells, relevantNums, currentConfig, validConfigs)

            # Removes the current hypothesis for this cell to test for a mine
            currentConfig.pop()

    def findSafeMoves(self) : # Coordinates all the other methods to output all the safe moves
        # If trivial moves were found, outputs those
        trivialMoves = self.findTrivialMoves()
        if trivialMoves :
            return trivialMoves

        borderCells = self.getBorderCells()
        if not borderCells : return []

        groups = self.getGroups(borderCells)
        allSafeMoves = []

        for group in groups :
            if len(group) > self.maxGroupSize :
                continue

            relevantNums = self.getRelevantNumberedCells(group)
            validConfigs = []
            self.backtrack(0, group, relevantNums, [], validConfigs)

            if validConfigs :
                for i in range(len(group)) :
                    if all(config[i] == 0 for config in validConfigs) : # If a cell is safe in all configurations, it has to be safe
                        allSafeMoves.append((group[i], "REVEAL"))
                    elif all(config[i] == 1 for config in validConfigs) : # If a cell is a mine in all configuration, it has to be a mine
                        allSafeMoves.append((group[i], "FLAG"))
        
        return allSafeMoves

    def solveStep(self, window) : # Executes the found moves on the Arcade window
        moves = self.findSafeMoves()
        
        if moves :
            # Avoids clicking twice on the same cell
            processed = set()

            for cell, action in moves :
                if cell not in processed :
                    btn = arcade.MOUSE_BUTTON_LEFT if action == "REVEAL" else arcade.MOUSE_BUTTON_RIGHT
                    window.handleCellClick(cell.row, cell.column, btn)
                    processed.add(cell)
            return True # Signals that an action had been executed
        else :
            # Verifies if there are remaining hidden cells that aren't flagged yet
            hiddenRemaining = [c for r in self.grid for c in r if c.hidden and not c.flag]
            if hiddenRemaining :
                print("The solver is stuck, no logical solution has been found.")
                return False # Signals that the solver is stuck
            return True # The grid has been solved

if __name__ == "__main__" :
    
    # Delay between each step of the solver. Cannot be set to 0 for some reason
    DELAY = 0.25

    # Initializes the Arcade window and solver
    window = minesweeper.GameWindow()
    solver = LogicSolver(grid = window.grid)

    # Makes a first click randomly on the grid
    startRow = random.randint(0, minesweeper.ROWS - 1)
    startCol = random.randint(0, minesweeper.COLUMNS - 1)
    window.handleCellClick(startRow, startCol, arcade.MOUSE_BUTTON_LEFT)

    def update(deltaTime) :
        if not window.gameOver :
            # Calls the solver
            canContinue = solver.solveStep(window)

            # If the solver returns False, then it is stuck
            if not canContinue :
                print("Stopping the solver")
                
                # Stops calling the next step
                arcade.unschedule(update)

                arcade.schedule(lambda delta_time : arcade.exit(), 10) # 10-seconds delay before the window closes
                
    arcade.schedule(update, DELAY)
    arcade.run()