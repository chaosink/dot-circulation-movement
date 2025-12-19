import sys
import random
from config import N, SVG_SIZE, MARGIN

# Increase recursion depth just in case
sys.setrecursionlimit(2000)

class HamiltonianCycleWilson:
    def __init__(self, N=N):
        if N % 2 != 0:
            raise ValueError("N must be even for 2x2 block construction")
        self.N = N
        self.grid = [[0 for _ in range(N)] for _ in range(N)]
        self.is_ccw = False

        # Directions: 1: Left, 2: Up, 3: Right, 4: Down
        self.LEFT = 1
        self.UP = 2
        self.RIGHT = 3
        self.DOWN = 4

    def solve(self):
        # 1. Initialize with 2x2 loops in every block
        self.is_ccw = random.choice([False, True])

        for r in range(0, self.N, 2):
            for c in range(0, self.N, 2):
                if not self.is_ccw:
                    self.grid[r][c] = self.RIGHT
                    self.grid[r][c+1] = self.DOWN
                    self.grid[r+1][c+1] = self.LEFT
                    self.grid[r+1][c] = self.UP
                else:
                    self.grid[r][c] = self.DOWN
                    self.grid[r+1][c] = self.RIGHT
                    self.grid[r+1][c+1] = self.UP
                    self.grid[r][c+1] = self.LEFT

        # 2. Generate Uniform Spanning Tree (UST) on (N/2)x(N/2) coarse grid using Wilson's Algorithm
        R, C = self.N // 2, self.N // 2

        # 'visited' tracks nodes IN THE TREE
        in_tree = [[False for _ in range(C)] for _ in range(R)]

        # 'next_node' stores the path for loop-erased random walk
        # next_node[r][c] = (nr, nc)
        # This acts as a temporary parent pointer during the walk

        # Step 2a: Arbitrarily pick a root and add to tree
        root_r, root_c = random.randint(0, R-1), random.randint(0, C-1)
        in_tree[root_r][root_c] = True

        # Total nodes to add
        remaining_nodes = R * C - 1

        while remaining_nodes > 0:
            # Step 2b: Pick a random starting node NOT in tree
            while True:
                curr_r, curr_c = random.randint(0, R-1), random.randint(0, C-1)
                if not in_tree[curr_r][curr_c]:
                    break

            # Step 2c: Perform Loop-Erased Random Walk until hitting the tree
            start_r, start_c = curr_r, curr_c
            walk_path = {} # Map (r,c) -> (next_r, next_c)

            u_r, u_c = start_r, start_c
            while not in_tree[u_r][u_c]:
                # Pick random neighbor
                moves = [(-1, 0), (1, 0), (0, -1), (0, 1)]
                valid_moves = []
                for dr, dc in moves:
                    nr, nc = u_r + dr, u_c + dc
                    if 0 <= nr < R and 0 <= nc < C:
                        valid_moves.append((nr, nc))

                next_r, next_c = random.choice(valid_moves)
                walk_path[(u_r, u_c)] = (next_r, next_c)
                u_r, u_c = next_r, next_c

            # Step 2d: Retrace path, add to tree, and merge blocks
            # The path in 'walk_path' is now loop-erased automatically
            # because re-visiting a node overwrites its entry in the dictionary.
            # We just follow the pointers from start_r, start_c.

            u_r, u_c = start_r, start_c
            while not in_tree[u_r][u_c]:
                in_tree[u_r][u_c] = True
                remaining_nodes -= 1

                next_r, next_c = walk_path[(u_r, u_c)]

                # MERGE the blocks between (u_r, u_c) and (next_r, next_c)
                self.merge_blocks(u_r, u_c, next_r, next_c)

                u_r, u_c = next_r, next_c

        return True

    def merge_blocks(self, r1, c1, r2, c2):
        # Coordinates in fine grid (top-left of each 2x2 block)
        fr1, fc1 = r1 * 2, c1 * 2
        fr2, fc2 = r2 * 2, c2 * 2

        if r2 == r1 and c2 == c1 + 1: # Right neighbor
            if not self.is_ccw:
                # CW
                # A_tr -> B_tl
                self.grid[fr1][fc1+1] = self.RIGHT
                # B_bl -> A_br
                self.grid[fr2+1][fc2] = self.LEFT
            else:
                # CCW
                # A_br (1,1) -> A_tr (0,1) [Up]
                # B_tl (0,0) -> B_bl (1,0) [Down]
                # Swap to:
                # A_br -> B_bl [Right]
                # B_tl -> A_tr [Left]
                self.grid[fr1+1][fc1+1] = self.RIGHT
                self.grid[fr2][fc2] = self.LEFT

        elif r2 == r1 and c2 == c1 - 1: # Left neighbor
            self.merge_blocks(r2, c2, r1, c1)

        elif c2 == c1 and r2 == r1 + 1: # Bottom neighbor
            if not self.is_ccw:
                # CW
                # A_br -> B_tr
                self.grid[fr1+1][fc1+1] = self.DOWN
                # B_tl -> A_bl
                self.grid[fr2][fc2] = self.UP
            else:
                # CCW
                # A_bl -> A_br (Right)
                # B_tr -> B_tl (Left)
                # Swap to:
                # A_bl -> B_tl (Down)
                # B_tr -> A_br (Up)
                self.grid[fr1+1][fc1] = self.DOWN
                self.grid[fr2][fc2+1] = self.UP

        elif c2 == c1 and r2 == r1 - 1: # Top neighbor
            self.merge_blocks(r2, c2, r1, c1)

    def print_grid(self):
        for y in range(self.N):
            row_str = []
            for x in range(self.N):
                row_str.append(str(self.grid[y][x]))
            print(",".join(row_str) + ",")
        print("\n----------\n")

    def generate_html(self, filename="HamiltonianCycleWilson.html"):
        available_size = SVG_SIZE - 2 * MARGIN
        cell_size = available_size / self.N

        width = SVG_SIZE
        height = SVG_SIZE

        svg_content = [f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">']

        # Draw Path
        for y in range(self.N):
            for x in range(self.N):
                direction = self.grid[y][x]
                if direction == 0: continue

                x1 = MARGIN + x * cell_size + cell_size / 2
                y1 = MARGIN + y * cell_size + cell_size / 2

                dx, dy = 0, 0
                if direction == self.LEFT: dx = -1
                elif direction == self.UP: dy = -1
                elif direction == self.RIGHT: dx = 1
                elif direction == self.DOWN: dy = 1

                x2 = x1 + dx * cell_size
                y2 = y1 + dy * cell_size

                stroke_width = max(1, cell_size * 0.1)
                svg_content.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#007bff" stroke-width="{stroke_width}" />')
                radius = max(1, cell_size * 0.1)
                svg_content.append(f'<circle cx="{x1}" cy="{y1}" r="{radius}" fill="#007bff" />')

        svg_content.append('</svg>')

        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Hamiltonian Cycle Wilson {self.N}x{self.N}</title>
    <style>
        body {{ font-family: sans-serif; text-align: center; padding: 0; margin: 0; }}
        h1 {{ margin: 10px; }}
        svg {{ border: 1px solid #ccc; background: #f9f9f9; }}
    </style>
</head>
<body>
    <h1>Hamiltonian Cycle Wilson ({self.N}x{self.N})</h1>
    {"".join(svg_content)}
</body>
</html>
"""
        with open(filename, "w", encoding="utf-8") as f:
            f.write(html_content)
        print(f"HTML visualization saved to {filename}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        try:
            N = int(sys.argv[1])
        except:
            pass

    solver = HamiltonianCycleWilson(N)
    if solver.solve():
        solver.print_grid()
        solver.generate_html("HamiltonianCycleWilson.html")
    else:
        print("No solution found.")
