import sys
import random
from config import N, SVG_SIZE, MARGIN

# Increase recursion depth just in case
sys.setrecursionlimit(2000)

class RecursiveHamiltonianCycle:
    def __init__(self, N=N):
        # Ensure N is a power of 2 for perfect recursive division
        if N & (N-1) != 0:
             raise ValueError("N must be a power of 2 (e.g., 2, 4, 8, 16, 32)")

        self.N = N
        self.grid = [[0 for _ in range(N)] for _ in range(N)]

        # Directions
        self.LEFT = 1
        self.UP = 2
        self.RIGHT = 3
        self.DOWN = 4

    def solve(self):
        # Start the recursive construction
        # We start with N*N 1x1 blocks and recursively merge them.
        # However, the base case for "connecting" is simpler if we start from
        # the smallest unit that forms a cycle, which is a 2x2 block.

        # Level 0: Initialize 2x2 blocks with simple cycles
        self.initialize_2x2_cycles()

        # Now we recursively merge blocks.
        # Current block size is 2 (in terms of cells).
        # We merge 2x2 meta-blocks into larger meta-blocks.
        # Level 1: Merge 2x2 blocks (size 2) into 4x4 blocks (size 4)
        # Level 2: Merge 4x4 blocks (size 4) into 8x8 blocks (size 8)
        # ...
        current_size = 2
        while current_size < self.N:
            self.merge_level(current_size)
            current_size *= 2

        return True

    def initialize_2x2_cycles(self):
        # Initialize every 2x2 block with a cycle
        # Randomly choose between Clockwise (CW) and Counter-Clockwise (CCW) for the whole grid
        is_ccw = random.choice([False, True])

        for r in range(0, self.N, 2):
            for c in range(0, self.N, 2):
                if not is_ccw:
                    self.grid[r][c] = self.RIGHT
                    self.grid[r][c+1] = self.DOWN
                    self.grid[r+1][c+1] = self.LEFT
                    self.grid[r+1][c] = self.UP
                else:
                    self.grid[r][c] = self.DOWN
                    self.grid[r+1][c] = self.RIGHT
                    self.grid[r+1][c+1] = self.UP
                    self.grid[r][c+1] = self.LEFT

    def merge_level(self, block_size):
        # We are merging blocks of size `block_size` into blocks of size `2 * block_size`.
        # The grid of meta-blocks is effectively (N / block_size) x (N / block_size).
        # We iterate over the new larger meta-blocks (2x2 of the current blocks).

        new_block_size = block_size * 2

        for r in range(0, self.N, new_block_size):
            for c in range(0, self.N, new_block_size):
                # Within this region (r, c) of size new_block_size x new_block_size,
                # we have 4 sub-blocks of size block_size:
                # Top-Left (TL), Top-Right (TR), Bottom-Left (BL), Bottom-Right (BR).
                # We need to connect them to form a single cycle covering the whole region.
                # Currently, each sub-block is an independent cycle.

                # A simple fixed strategy to merge 4 cycles into 1:
                # "C" shape merge or "O" shape merge?
                # Let's use a "U" shape merge sequence: TL -> BL -> BR -> TR -> TL (or similar)
                # To do this, we need to merge:
                # 1. TL and BL (Vertical merge)
                # 2. BL and BR (Horizontal merge)
                # 3. BR and TR (Vertical merge)
                # (Connecting TR back to TL is implicit if we don't break that connection,
                #  but actually merging 3 times is sufficient to join 4 components into 1).

                # However, we want some randomness so it doesn't look too regular.
                # Randomly choose one of the spanning trees of the 2x2 meta-grid:
                # The 2x2 meta-grid has 4 nodes. A spanning tree has 3 edges.
                # There are a few patterns for spanning trees on 4 nodes (cycle is not allowed in tree).
                # Wait, we just need to merge them into ONE component.
                # 3 merges are necessary and sufficient.

                # Let's identify the 4 sub-blocks by their top-left coordinates:
                tl_r, tl_c = r, c
                tr_r, tr_c = r, c + block_size
                bl_r, bl_c = r + block_size, c
                br_r, br_c = r + block_size, c + block_size

                # We can randomize the merge pattern.
                # Possible spanning trees for 4 nodes in a square:
                # 1. U-shape: TL-BL-BR-TR (implies merges: TL-BL, BL-BR, BR-TR)
                # 2. C-shape: TR-TL-BL-BR (implies merges: TR-TL, TL-BL, BL-BR)
                # ... and so on.

                # Let's generalize:
                # List possible edges between the 4 sub-blocks:
                # (TL, TR), (TL, BL), (TR, BR), (BL, BR)
                # We need to choose 3 edges to form a tree.
                # (Total 4 edges in a square, choose 3 = remove 1 edge).

                edges = [
                    ('H', tl_r, tl_c, tr_r, tr_c), # Top Horizontal
                    ('V', tl_r, tl_c, bl_r, bl_c), # Left Vertical
                    ('V', tr_r, tr_c, br_r, br_c), # Right Vertical
                    ('H', bl_r, bl_c, br_r, br_c)  # Bottom Horizontal
                ]

                # Randomly choose 3 edges to merge
                # Removing one edge breaks the "cycle of blocks", leaving a tree (path) of blocks.
                random.shuffle(edges)
                edges_to_merge = edges[:3]

                for orientation, r1, c1, r2, c2 in edges_to_merge:
                    if orientation == 'H':
                        self.merge_horizontal(r1, c1, r2, c2, block_size)
                    else:
                        self.merge_vertical(r1, c1, r2, c2, block_size)

    def merge_horizontal(self, r1, c1, r2, c2, size):
        # Merge block at (r1, c1) with block at (r2, c2). (r2,c2) is to the right.
        # Boundary is at c1 + size.
        # We need to find two adjacent edges along the boundary to swap.
        # To preserve the Hamiltonian property, we must pick edges that are currently
        # part of the cycle.
        # For simple rectangular blocks formed by this recursive process,
        # the boundary usually consists of parallel lines.

        # Constructive invariant:
        # We can pick a random position along the shared boundary to perform the swap.
        # The shared boundary is vertical line at x = c1 + size.
        # Rows involved are r1 to r1 + size - 1.

        # We look for a row 'i' such that:
        # grid[i][x-1] == RIGHT (enters boundary) OR grid[i][x-1] == ...
        # Actually, simpler: Look for a row where:
        # Left Block (at x-1) has a path going DOWN or UP along the boundary?
        # NO. We need to find a place where the cycles are "tangent".

        # Let's look at the edges *crossing* the boundary? No, they don't cross yet.
        # They run parallel to the boundary.
        # On the Left Block's right edge (col x-1), path usually goes UP or DOWN.
        # On the Right Block's left edge (col x), path usually goes UP or DOWN.

        # We need to find a row 'i' where:
        # Left Block at (i, x-1) -> (i+1, x-1) (DOWN)
        # Right Block at (i+1, x) -> (i, x) (UP)
        # OR vice versa.

        # Then we can swap connections to:
        # (i, x-1) -> (i, x) (RIGHT)
        # (i+1, x) -> (i+1, x-1) (LEFT)

        x = c1 + size # The column index of the right block

        # Find valid merge spots
        candidates = []
        for i in range(r1, r1 + size - 1):
            # Check for antiparallel vertical edges
            # Case 1: Left goes DOWN, Right goes UP
            if (self.grid[i][x-1] == self.DOWN and
                self.grid[i+1][x] == self.UP): # Note: Checking grid values isn't enough, need to verify connectivity?
                # Actually, if grid[i][x-1] is DOWN, it means flow is (i, x-1) -> (i+1, x-1).
                # If grid[i+1][x] is UP, it means flow is (i+1, x) -> (i, x).
                # This is a valid swap spot.
                candidates.append((i, 1)) # Type 1

            # Case 2: Left goes UP, Right goes DOWN
            elif (self.grid[i+1][x-1] == self.UP and
                  self.grid[i][x] == self.DOWN):
                # Flow: (i+1, x-1) -> (i, x-1)
                # Flow: (i, x) -> (i+1, x)
                candidates.append((i, 2)) # Type 2

        if not candidates:
            # Fallback (should ideally not happen with this construction):
            # Try to force a merge on the very top or bottom if simple parallel edges exist?
            # In our 2x2 initialization and subsequent merges, we tend to preserve
            # long straight edges, but randomness might break this.
            return

        # Pick a random candidate
        i, type = random.choice(candidates)

        if type == 1:
            # Swap (L:Down, R:Up) -> (L:Right, R:Left)
            # Old: (i, x-1)->(i+1, x-1) and (i+1, x)->(i, x)
            # New: (i, x-1)->(i, x) and (i+1, x)->(i+1, x-1)
            self.grid[i][x-1] = self.RIGHT
            self.grid[i+1][x] = self.LEFT
        else:
            # Swap (L:Up, R:Down) -> (L:Right, R:Left)
            # Old: (i+1, x-1)->(i, x-1) and (i, x)->(i+1, x)
            # New: (i+1, x-1)->(i+1, x) and (i, x)->(i, x-1)
            self.grid[i+1][x-1] = self.RIGHT
            self.grid[i][x] = self.LEFT

    def merge_vertical(self, r1, c1, r2, c2, size):
        # Merge block at (r1, c1) with block at (r2, c2). (r2,c2) is below.
        # Boundary is at row y = r1 + size.

        y = r1 + size

        candidates = []
        for j in range(c1, c1 + size - 1):
            # Check for antiparallel horizontal edges
            # Case 1: Top goes RIGHT, Bottom goes LEFT
            if (self.grid[y-1][j] == self.RIGHT and
                self.grid[y][j+1] == self.LEFT):
                # Flow: (y-1, j) -> (y-1, j+1)
                # Flow: (y, j+1) -> (y, j)
                candidates.append((j, 1))

            # Case 2: Top goes LEFT, Bottom goes RIGHT
            elif (self.grid[y-1][j+1] == self.LEFT and
                  self.grid[y][j] == self.RIGHT):
                # Flow: (y-1, j+1) -> (y-1, j)
                # Flow: (y, j) -> (y, j+1)
                candidates.append((j, 2))

        if not candidates:
            return

        j, type = random.choice(candidates)

        if type == 1:
            # Swap (T:Right, B:Left) -> (T:Down, B:Up)
            # Old: (y-1, j)->(y-1, j+1) and (y, j+1)->(y, j)
            # New: (y-1, j)->(y, j) and (y, j+1)->(y-1, j+1)
            self.grid[y-1][j] = self.DOWN
            self.grid[y][j+1] = self.UP
        else:
            # Swap (T:Left, B:Right) -> (T:Down, B:Up)
            # Old: (y-1, j+1)->(y-1, j) and (y, j)->(y, j+1)
            # New: (y-1, j+1)->(y-1, j+1) [Wait, this is Up] -> No, (y-1, j+1) connects to (y, j+1) which is Down
            # Let's trace carefully:
            # We want to connect (y-1, j+1) to (y, j+1) [Down]
            # And (y, j) to (y-1, j) [Up]
            self.grid[y-1][j+1] = self.DOWN
            self.grid[y][j] = self.UP

    def print_grid(self):
        for y in range(self.N):
            row_str = []
            for x in range(self.N):
                row_str.append(str(self.grid[y][x]))
            print(",".join(row_str) + ",")
        print("\n----------\n")

    def generate_html(self, filename="HamiltonianCycleRecursive.html"):
        available_size = SVG_SIZE - 2 * MARGIN
        cell_size = available_size / self.N

        width = SVG_SIZE
        height = SVG_SIZE

        svg_content = [f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">']
        svg_content.append('<defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L0,6 L9,3 z" fill="#333" /></marker></defs>')

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
    <title>Hamiltonian Cycle Recursive {self.N}x{self.N}</title>
    <style>
        body {{ font-family: sans-serif; text-align: center; padding: 0; margin: 0; }}
        h1 {{ margin: 10px; }}
        svg {{ border: 1px solid #ccc; background: #f9f9f9; }}
    </style>
</head>
<body>
    <h1>Hamiltonian Cycle Recursive ({self.N}x{self.N})</h1>
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

    solver = RecursiveHamiltonianCycle(N)
    if solver.solve():
        solver.print_grid()
        solver.generate_html("HamiltonianCycleRecursive.html")
    else:
        print("No solution found.")
