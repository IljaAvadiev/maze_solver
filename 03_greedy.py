# somewhat inspired by https://cdn.cs50.net/ai/2020/spring/lectures/0/src0/maze.py
from pickle import NONE
import pygame
from sys import exit
from config import *

# class for a visual representation of the maze
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


# load prepared map
with open(FILE_NAME, "r") as f:
    map_config = f.read().splitlines()

N_ROWS = len(map_config)
N_COLS = len(map_config[0])
WIDTH = CELL_WIDTH * N_COLS
HEIGHT = CELL_HEIGHT * N_ROWS
START_STATE = None
GOAL_STATE = None

maze = []
walls = []
# load maze from a txt file
for y, row in enumerate(map_config):
    cells = []
    for x, char in enumerate(row):
        t = None
        if char == "w":
            t = "wall"
            walls.append((x, y))
        elif char == "p":
            t = "path"
        elif char == "s":
            t = "start"
            START_STATE = (x, y)
        elif char == "g":
            t = "goal"
            GOAL_STATE = (x, y)

        cell = Cell(x, y, t)
        cells.append(cell)
    maze.append(cells)


class Vertex:
    def __init__(self, state, parent, action, cost, h):
        self.state = state
        self.parent = parent
        self.action = action
        self.cost = cost
        self.h = h

    def __lt__(self, other):
        return self.h < other.h

    def __gt__(self, other):
        return self.h > other.h

    def __eq__(self, other):
        if isinstance(other, Vertex):
            return self.state == other.state
        elif isinstance(other, tuple):
            return self.state == other
        return False


# this is a FIFO frontier using a queue data structure
class Frontier:
    def __init__(self):
        self.frontier = []

    def add(self, vertex):
        self.frontier.append(vertex)

    def __len__(self):
        return len(self.frontier)

    def __contains__(self, vertex):
        return vertex in self.frontier

    def pop(self):
        min_h_vertex = min(self.frontier)
        self.frontier.remove(min_h_vertex)
        return min_h_vertex


# calculate a list of neighbours for a single state
neighbours = lambda state: [
    ((dx, dy), (state[0] + dx, state[1] + dy))
    for dx, dy in (
        (-1, 0),
        (0, 1),
        (0, -1),
        (1, 0),
    )
    if state[0] + dx >= 0
    and state[0] + dx < N_COLS
    and state[1] + dy >= 0
    and state[1] + dy < N_ROWS
    and (state[0] + dx, state[1] + dy) not in walls
]


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH + OFFSET * 2, HEIGHT + OFFSET * 2))
    pygame.display.set_caption("Maze Generator")
    clock = pygame.time.Clock()

    goal_reached = False

    # initialize frontier with the start state
    frontier = Frontier()
    start_vertex = Vertex(state=START_STATE, parent=None, action=None, cost=0, h=0)
    frontier.add(start_vertex)
    explored_states = []

    # for video recording purposes
    frame_num = 0

    # contains the actions from the path that the algorithm finds
    actions = []

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

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
                elif cell.type == "visited":
                    color = VISITED_COLOR
                elif cell.type == "solution":
                    color = SOLUTION_COLOR
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
        # draw found path
        if actions:
            prev_state = START_STATE
            for action in reversed(actions):
                if action is not None:
                    x, y = prev_state
                    dx, dy = action

                    start_x = x * CELL_WIDTH + OFFSET + CELL_WIDTH / 2
                    start_y = y * CELL_HEIGHT + OFFSET + CELL_HEIGHT / 2
                    end_x = (x + dx) * CELL_WIDTH + OFFSET + CELL_WIDTH / 2
                    end_y = (y + dy) * CELL_HEIGHT + OFFSET + CELL_HEIGHT / 2
                    pygame.draw.line(
                        screen,
                        "black",
                        (start_x, start_y),
                        (end_x, end_y),
                        4,
                    )
                    prev_state = (x + dx, y + dy)

        # use the greed best first search algorithm
        if len(frontier) > 0 and not goal_reached:
            vertex = frontier.pop()

            if vertex.state == GOAL_STATE:
                goal_reached = True
                # mark the solution path with pygame
                while vertex.parent is not None:
                    actions.append(vertex.action)
                    vertex = vertex.parent

                    if vertex.state != GOAL_STATE and vertex.state != START_STATE:
                        x, y = vertex.state
                        maze[y][x].set_type("solution")
            else:
                # mark a cell as explored
                explored_states.append(vertex.state)
                if vertex.state != GOAL_STATE and vertex.state != START_STATE:
                    x, y = vertex.state
                    maze[y][x].set_type("visited")

                # add neighbours to frontier
                for action, state in neighbours(vertex.state):
                    if state not in frontier and state not in explored_states:
                        # Manhattan distance as heuristic
                        h = abs(state[0] - GOAL_STATE[0]) + abs(
                            state[1] - GOAL_STATE[1]
                        )
                        child = Vertex(
                            state=state,
                            parent=vertex,
                            action=action,
                            cost=vertex.cost + 1,
                            h=h,
                        )
                        frontier.add(child)

        pygame.display.update()
        clock.tick(FPS)
        # save images for animation purposes
        if RECORD:
            pygame.image.save(screen, f"frames/frame_{frame_num:04}.jpeg")
            frame_num += 1


if __name__ == "__main__":
    main()
