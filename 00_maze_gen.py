import pygame
from sys import exit
from config import *

N_ROWS = 40
N_COLS = 40
WIDTH = CELL_WIDTH * N_COLS
HEIGHT = CELL_HEIGHT * N_ROWS

CELL_TYPES = ["wall", "path", "start", "goal"]


class Cell:
    def __init__(self, x, y, type):
        assert type in CELL_TYPES
        self.x = x
        self.y = y
        self.type = type

    def set_type(self, type):
        assert type in CELL_TYPES
        self.type = type

    def __repr__(self):
        return self.type[0]


# transform pixel coordinates into maze coordinates
def get_coordinates(x, y):
    x = int((x - OFFSET) / CELL_WIDTH)
    y = int((y - OFFSET) / CELL_HEIGHT)
    return x, y


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH + OFFSET * 2, HEIGHT + OFFSET * 2))
    pygame.display.set_caption("Maze Generator")
    clock = pygame.time.Clock()

    maze = []
    # create maze without any walls
    for y in range(N_ROWS):
        row = []
        for x in range(N_COLS):
            row.append(Cell(x, y, "path"))
        maze.append(row)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                x, y = get_coordinates(x, y)
                # block cell
                if event.button == 1:
                    maze[y][x].set_type("wall")
                # path cell
                elif event.button == 3:
                    maze[y][x].set_type("path")
            elif event.type == pygame.KEYDOWN:
                # save maze into a txt file
                if event.key == pygame.K_SPACE:
                    print(f"Saving maze into file: {FILE_NAME}")

                    with open(FILE_NAME, "w") as f:
                        for row in maze:
                            for cell in row:
                                f.write(str(cell))
                            f.write("\n")

                # create start cell
                elif event.key == pygame.K_s:
                    x, y = pygame.mouse.get_pos()
                    x, y = get_coordinates(x, y)
                    maze[y][x].set_type("start")
                # create start cell
                elif event.key == pygame.K_g:
                    x, y = pygame.mouse.get_pos()
                    x, y = get_coordinates(x, y)
                    maze[y][x].set_type("goal")
        screen.fill(BG_COLOR)

        # draw maze
        for row in maze:
            for cell in row:
                # cells
                start_x = cell.x * CELL_WIDTH + OFFSET
                start_y = cell.y * CELL_HEIGHT + OFFSET
                color = (255, 0, 0)
                if cell.type == "path":
                    color = PATH_COLOR
                elif cell.type == "wall":
                    color = WALL_COLOR
                elif cell.type == "goal":
                    color = GOAL_COLOR
                elif cell.type == "start":
                    color = START_COLOR
                pygame.draw.rect(
                    screen,
                    color,
                    (start_x, start_y, CELL_WIDTH, CELL_HEIGHT),
                )
                # borders
                # top lines
                pygame.draw.line(
                    screen,
                    BORDER_COLOR,
                    (start_x, start_y),
                    (start_x + CELL_WIDTH, start_y),
                    BORDER_WIDTH,
                )
                # right lines
                pygame.draw.line(
                    screen,
                    BORDER_COLOR,
                    (start_x + CELL_WIDTH, start_y),
                    (start_x + CELL_WIDTH, start_y + CELL_HEIGHT),
                    BORDER_WIDTH,
                )
                # bottom lines
                pygame.draw.line(
                    screen,
                    BORDER_COLOR,
                    (start_x, start_y + CELL_HEIGHT),
                    (start_x + CELL_WIDTH, start_y + CELL_HEIGHT),
                    BORDER_WIDTH,
                )
                # left lines
                pygame.draw.line(
                    screen,
                    BORDER_COLOR,
                    (start_x, start_y),
                    (start_x, start_y + CELL_HEIGHT),
                    BORDER_WIDTH,
                )

        pygame.display.update()
        clock.tick(FPS)


if __name__ == "__main__":
    main()
