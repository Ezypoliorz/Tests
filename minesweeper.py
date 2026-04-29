# A simple Minesweeper game using Arcade
# I also made a script that solves the grid - see minesweeper_solver.py

import arcade
import random

# Defines the basic configuration
SCREEN_SIZE = 700
SCREEN_TITLE = "Minesweeper"

ROWS = 20
COLUMNS = 20

BORDER = 30 # Minimum border around the grid, in px
AVAILABLE_SPACE = SCREEN_SIZE - BORDER # Available space for the grid

CELL_SIZE = int(AVAILABLE_SPACE / max(COLUMNS, ROWS)) # Size of a single tile, in px

GRID_OFFSET_X = (SCREEN_SIZE - (COLUMNS * CELL_SIZE)) / 2 # Actual offset of the grid so it is centered
GRID_OFFSET_Y = (SCREEN_SIZE - (ROWS * CELL_SIZE)) / 2

DENSITY = 12 # Density of mines
MINES = int(DENSITY * ROWS * COLUMNS / 100) # Number of mines to generate

class Cell() : # Class for every tile of the grid
    def __init__(self, row, column) :
        self.row = row
        self.column = column
        self.posX = int(GRID_OFFSET_X + (column * CELL_SIZE) + CELL_SIZE / 2) # Position of the center of the cell
        self.posY = int(GRID_OFFSET_Y + (row * CELL_SIZE) + CELL_SIZE / 2)
        self.mine = False
        self.value = 0
        self.hidden = True
        self.flag = False

    def getSurroundingCells(self, grid) : # Returns a list of the surrounding cells
        surroundingCells = []
        surroundingRelativeCoordinates = [  (1, -1), (1, 0), (1, 1),
                                            (0, -1),         (0, 1), 
                                            (-1, -1), (-1, 0), (-1, 1)]
        
        for cell in surroundingRelativeCoordinates :
            cellRow = self.row + cell[0]
            cellColumn = self.column + cell[1]
            if 0 <= cellRow < ROWS and 0 <= cellColumn < COLUMNS :
                surroundingCells.append(grid[cellRow][cellColumn])
        
        return surroundingCells
    
    def calculateValue(self, grid) : # Calculates the value of the cell based on the number of mines around it
        if self.mine == False :
            for cell in self.getSurroundingCells(grid=grid) :
                if cell.mine == True :
                    self.value += 1

    def draw(self, hover : bool, textures) :
        # Chooses the appropriate texture to apply
        if hover == True :
            texture = 'cellTextureHover'
        elif self.hidden == True :
            if self.flag == True :
                texture = 'cellTextureFlag'
            else :
                texture = 'cellTextureHidden'
        elif self.mine == True :
            texture = 'cellTextureMine'
        else :
            texture = f'cellTexture{self.value}'

        # Defines the Arcade sprite corresponding to the cell
        sprite = arcade.Sprite(
            path_or_texture=textures[texture], # Applies the texture to the sprite
            scale=1/400 * CELL_SIZE, # The textures are 400x400px
            center_x=self.posX, center_y=self.posY)

        arcade.draw_sprite(sprite)

def placeMines(grid, firstClick : tuple) :
    # Creates a list of available coordinates to place mines on
    coordinates = []
    for row in grid :
        for cell in row :
            coordinates.append((cell.row, cell.column))
    
    # Defines "safe cells" on and around the firt cell clicked
    safeCoordinates = []
    surroundingCells = grid[firstClick[0]][firstClick[1]].getSurroundingCells(grid=grid)
    for cell in surroundingCells :
        safeCoordinates.append((cell.row, cell.column))
    safeCoordinates.append(firstClick)
    
    availableCoordinates = [coordinate for coordinate in coordinates if coordinate not in safeCoordinates]

    # Randomly generates mine placements
    mineLocations = random.sample(availableCoordinates, MINES) # Using random.sample guarantees that there are no duplicates

    for mineLocation in mineLocations :
        grid[mineLocation[0]][mineLocation[1]].mine = True
        grid[mineLocation[0]][mineLocation[1]].value = None
    
    for row in grid :
        for cell in row :
            cell.calculateValue(grid)


def generateGrid() :
    grid = []
    for row in range(ROWS) :
        grid.append([])
        for column in range(COLUMNS) :
            grid[row]. append(Cell(row=row, column=column))
    return grid

class GameWindow(arcade.Window) : # Class for the Arcade window
    def __init__(self) :
        # Initializes the Arcade window
        super().__init__(SCREEN_SIZE, SCREEN_SIZE, SCREEN_TITLE)
        arcade.set_background_color(arcade.color.DARK_SLATE_GRAY)

        # Lowers the framerate to 30FPS (default is 60FPS)
        self.set_update_rate(1 / 30)

        self.clicks = 0
        self.gameOver = False # State of the game, a win also sets gameOver = True
        self.grid = generateGrid()

        # Pre-loads the textures
        self.textures = {
            'cellTextureHidden' : arcade.load_texture('Assets/Minesweeper/CellTextureHidden.png'),
            'cellTextureHover' : arcade.load_texture('Assets/Minesweeper/CellTextureHover.png'),
            'cellTextureFlag' : arcade.load_texture('Assets/Minesweeper/CellTextureFlag.png'),
            'cellTextureMine' : arcade.load_texture('Assets/Minesweeper/CellTextureMine.png'),
            'cellTexture0' : arcade.load_texture('Assets/Minesweeper/CellTexture0.png'),
            'cellTexture1' : arcade.load_texture('Assets/Minesweeper/CellTexture1.png'),
            'cellTexture2' : arcade.load_texture('Assets/Minesweeper/CellTexture2.png'),
            'cellTexture3' : arcade.load_texture('Assets/Minesweeper/CellTexture3.png'),
            'cellTexture4' : arcade.load_texture('Assets/Minesweeper/CellTexture4.png'),
            'cellTexture5' : arcade.load_texture('Assets/Minesweeper/CellTexture5.png'),
            'cellTexture6' : arcade.load_texture('Assets/Minesweeper/CellTexture5.png'),
            'cellTexture7' : arcade.load_texture('Assets/Minesweeper/CellTexture6.png'),
            'cellTexture8' : arcade.load_texture('Assets/Minesweeper/CellTexture7.png')
        }        
    
    def on_draw(self) : # When the window is updated
        self.clear() # Clears the display

        for row in self.grid :
            for cell in row :
                cell.draw(hover=False, textures=self.textures)

    def handleCellClick(self, clickedRow, clickedColumn, button) :
        if self.gameOver == True :
            return
        
        clickedCell = self.grid[clickedRow][clickedColumn]

        if button == arcade.MOUSE_BUTTON_LEFT :
            if clickedCell.hidden == True and clickedCell.flag == False :
                if clickedCell.mine == True :
                    print("You lost ! This was a mine !")
                    for row in self.grid :
                        for cell in row :
                            cell.hidden = False
                            cell.flag = False
                    arcade.set_background_color(arcade.color.FALU_RED)
                    arcade.schedule(lambda delta_time : arcade.exit(), 10) # 10-seconds delay before the window closes

                self.clicks += 1
                if self.clicks == 1 :
                    placeMines(grid=self.grid, firstClick=(clickedRow, clickedColumn))

                clickedCell.hidden = False

                # Reveals every cell with 0 mines around, and their surrounding cells
                revealedSafeCells = 1
                while revealedSafeCells > 0 :
                    revealedSafeCells = 0
                    for row in self.grid :
                        for cell in row :
                            if cell.hidden == False and cell.value == 0 :
                                for surroundingCell in cell.getSurroundingCells(self.grid) :
                                    if surroundingCell.hidden == True :
                                        surroundingCell.hidden = False
                                        revealedSafeCells += 1
        
        elif button == arcade.MOUSE_BUTTON_RIGHT :
            clickedCell.flag = True if clickedCell.flag == False else False
        
        # Checks if the grid is fully completed
        correct = True
        for row in self.grid :
            for cell in row :
                if cell.mine == True and cell.flag == False : # If a mine square isn't flagged
                    correct = False
                if cell.mine == False and cell.hidden == True : # If an empty cell isn't discovered
                    correct = False
        if correct == True :
            print("You won ! Congratulations !")
            self.gameOver = True
            for row in self.grid :
                for cell in row :
                    cell.hidden = False
                    cell.flag = False
            arcade.set_background_color(arcade.color.FERN_GREEN)
            arcade.schedule(lambda delta_time : arcade.exit(), 10) # 10-seconds delay before the window closes
    
    def on_mouse_press(self, x, y, button, modifiers) :
        clickedColumn = int((x - GRID_OFFSET_X)  / CELL_SIZE)
        clickedRow = int((y - GRID_OFFSET_Y)  / CELL_SIZE)

        if 0 <= clickedRow < ROWS and 0 <= clickedColumn < COLUMNS :
            self.handleCellClick(clickedRow=clickedRow, clickedColumn=clickedColumn, button=button)
            
if __name__ == "__main__":
    print("Game started !")
    window = GameWindow()
    arcade.run()