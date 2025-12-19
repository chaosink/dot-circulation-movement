import sys
import random
from config import N, SVG_SIZE, MARGIN

# Increase recursion depth just in case
sys.setrecursionlimit(2000)

class HamiltonianCycleConstructive:
    def __init__(self, N=N):
        if N % 2 != 0:
            raise ValueError("N must be even for 2x2 block construction")
        self.N = N
        self.grid = [[0 for _ in range(N)] for _ in range(N)]
        self.is_ccw = False # Store the orientation choice

        # Directions: 1: Left, 2: Up, 3: Right, 4: Down (Matching genmap.cpp)
        self.LEFT = 1
        self.UP = 2
        self.RIGHT = 3
        self.DOWN = 4

    def solve(self):
        # 1. Initialize with 2x2 loops in every block
        # Randomly choose between Clockwise (CW) and Counter-Clockwise (CCW) for the whole grid
        self.is_ccw = random.choice([False, True])

        for r in range(0, self.N, 2):
            for c in range(0, self.N, 2):
                if not self.is_ccw:
                    # CW
                    self.grid[r][c] = self.RIGHT
                    self.grid[r][c+1] = self.DOWN
                    self.grid[r+1][c+1] = self.LEFT
                    self.grid[r+1][c] = self.UP
                else:
                    # CCW
                    self.grid[r][c] = self.DOWN
                    self.grid[r+1][c] = self.RIGHT
                    self.grid[r+1][c+1] = self.UP
                    self.grid[r][c+1] = self.LEFT

        # 2. Generate Spanning Tree on (N/2)x(N/2) coarse grid
        # We use the edges of the spanning tree to merge the 2x2 loops.
        R, C = self.N // 2, self.N // 2
        visited = [[False for _ in range(C)] for _ in range(R)]

        # Iterative DFS for Spanning Tree generation
        stack = [(0, 0)]
        visited[0][0] = True

        while stack:
            curr_r, curr_c = stack[-1]

            # Find unvisited neighbors
            # (dr, dc) for coarse grid
            moves = [(-1, 0), (1, 0), (0, -1), (0, 1)]
            random.shuffle(moves)

            found_next = False
            for dr, dc in moves:
                nr, nc = curr_r + dr, curr_c + dc
                if 0 <= nr < R and 0 <= nc < C and not visited[nr][nc]:
                    # Found a valid neighbor to connect to
                    visited[nr][nc] = True
                    stack.append((nr, nc))

                    # 3. Perform the merge/swap between (curr_r, curr_c) and (nr, nc)
                    self.merge_blocks(curr_r, curr_c, nr, nc)
                    found_next = True
                    break

            if not found_next:
                stack.pop()

        return True

    def merge_blocks(self, r1, c1, r2, c2):
        # Coordinates in fine grid (top-left of each 2x2 block)
        fr1, fc1 = r1 * 2, c1 * 2
        fr2, fc2 = r2 * 2, c2 * 2

        # Determine relative position
        if r2 == r1 and c2 == c1 + 1: # Right neighbor
            if not self.is_ccw:
                # CW logic (original)
                # A_tr: grid[fr1][fc1+1] was DOWN, becomes RIGHT
                self.grid[fr1][fc1+1] = self.RIGHT
                # B_bl: grid[fr2+1][fc2] was UP, becomes LEFT
                self.grid[fr2+1][fc2] = self.LEFT
            else:
                # CCW logic
                # A's right edge is A_tr->A_br (Up? No).
                # CCW: (0,0)->(1,0) Down, (1,0)->(1,1) Right, (1,1)->(0,1) Up, (0,1)->(0,0) Left
                # A_tr (0,1) -> (0,0) Left
                # A_br (1,1) -> (0,1) Up
                # B_tl (0,0) -> (1,0) Down
                # B_bl (1,0) -> (1,1) Right

                # We need to swap edges on the boundary.
                # A's right edge is A_br -> A_tr (Up) ? No.
                # A_br (1,1) -> A_tr (0,1) [Up]
                # B_tl (0,0) -> B_bl (1,0) [Down]

                # Swap to:
                # A_br -> B_bl [Right]
                # B_tl -> A_tr [Left]

                # A_br: grid[fr1+1][fc1+1] was UP, becomes RIGHT
                self.grid[fr1+1][fc1+1] = self.RIGHT
                # B_tl: grid[fr2][fc2] was DOWN, becomes LEFT
                self.grid[fr2][fc2] = self.LEFT

        elif r2 == r1 and c2 == c1 - 1: # Left neighbor
            self.merge_blocks(r2, c2, r1, c1)

        elif c2 == c1 and r2 == r1 + 1: # Bottom neighbor
            if not self.is_ccw:
                # CW logic (original)
                # A_br: grid[fr1+1][fc1+1] was LEFT, becomes DOWN
                self.grid[fr1+1][fc1+1] = self.DOWN
                # B_tl: grid[fr2][fc2] was RIGHT, becomes UP
                self.grid[fr2][fc2] = self.UP
            else:
                # CCW logic
                # A's bottom edge is A_bl->A_br (Right)
                # B's top edge is B_tr->B_tl (Left)
                # Swap to:
                # A_bl -> B_tl (Down)
                # B_tr -> A_br (Up)

                # A_bl: grid[fr1+1][fc1] was RIGHT, becomes DOWN
                self.grid[fr1+1][fc1] = self.DOWN
                # B_tr: grid[fr2][fc2+1] was LEFT, becomes UP
                self.grid[fr2][fc2+1] = self.UP

        elif c2 == c1 and r2 == r1 - 1: # Top neighbor
            self.merge_blocks(r2, c2, r1, c1)

    def print_grid(self):
        # Print numeric grid compatible with C++ genmap style
        for y in range(self.N):
            row_str = []
            for x in range(self.N):
                row_str.append(str(self.grid[y][x]))
            print(",".join(row_str) + ",")
        print("\n----------\n")

    def generate_html(self, filename="HamiltonianCycleSpanningTree.html"):
        # Calculate cell size dynamically to fit SVG_SIZE
        available_size = SVG_SIZE - 2 * MARGIN
        cell_size = available_size / self.N

        width = SVG_SIZE
        height = SVG_SIZE

        svg_content = [f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">']
        svg_content.append('<defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L0,6 L9,3 z" fill="#333" /></marker></defs>')

        # Draw Grid (Optional, faint)
        for i in range(self.N + 1):
            pos = MARGIN + i * cell_size
            # Vertical
            svg_content.append(f'<line x1="{pos}" y1="{MARGIN}" x2="{pos}" y2="{height-MARGIN}" stroke="#eee" stroke-width="1" />')
            # Horizontal
            svg_content.append(f'<line x1="{MARGIN}" y1="{pos}" x2="{width-MARGIN}" y2="{pos}" stroke="#eee" stroke-width="1" />')

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

                # Draw path segment (adjust stroke width based on cell size)
                stroke_width = max(1, cell_size * 0.1)
                svg_content.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#007bff" stroke-width="{stroke_width}" />')

                # Draw small dot
                radius = max(1, cell_size * 0.1)
                svg_content.append(f'<circle cx="{x1}" cy="{y1}" r="{radius}" fill="#007bff" />')

        svg_content.append('</svg>')

        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Hamiltonian Cycle Spanning Tree {self.N}x{self.N}</title>
    <style>
        body {{ font-family: sans-serif; text-align: center; padding: 0; margin: 0; }}
        h1 {{ margin: 10px; }}
        svg {{ border: 1px solid #ccc; background: #f9f9f9; }}
    </style>
</head>
<body>
    <h1>Hamiltonian Cycle Spanning Tree ({self.N}x{self.N})</h1>
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

    solver = HamiltonianCycleConstructive(N)
    # print(f"Generating Hamiltonian Cycle for {N}x{N} grid (Constructive Method)...", file=sys.stderr)
    if solver.solve():
        # print("Solution found:", file=sys.stderr)
        solver.print_grid()
        solver.generate_html("HamiltonianCycleSpanningTree.html")
    else:
        print("No solution found.")
