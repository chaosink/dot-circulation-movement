import sys
import random
from config import N, SVG_SIZE, MARGIN

# Increase recursion depth just in case
sys.setrecursionlimit(2000)

class HamiltonianCycleDomino:
    def __init__(self, N=N):
        if N % 2 != 0:
            raise ValueError("N must be even for Domino Tiling")
        self.N = N
        self.grid = [[0 for _ in range(N)] for _ in range(N)]

        # Directions
        self.LEFT = 1
        self.UP = 2
        self.RIGHT = 3
        self.DOWN = 4

    def solve(self):
        # 1. Generate a random tiling T1 (Horizontal initialization)
        self.grid = [[0 for _ in range(self.N)] for _ in range(self.N)]
        for r in range(self.N):
            for c in range(0, self.N, 2):
                self.grid[r][c] = self.RIGHT
                self.grid[r][c+1] = self.LEFT

        # Shuffle T1
        iterations = self.N * self.N * 5
        for _ in range(iterations):
            r = random.randint(0, self.N - 2)
            c = random.randint(0, self.N - 2)
            self.shuffle_window(self.grid, r, c)

        # T1 Adjacency
        t1_adj = self.grid_to_adj(self.grid)

        # 2. Generate a random tiling T2 (Vertical initialization)
        t2_grid = [[0 for _ in range(self.N)] for _ in range(self.N)]
        for c in range(self.N):
            for r in range(0, self.N, 2):
                t2_grid[r][c] = self.DOWN
                t2_grid[r+1][c] = self.UP

        # Shuffle T2
        for _ in range(iterations):
            r = random.randint(0, self.N - 2)
            c = random.randint(0, self.N - 2)
            self.shuffle_window(t2_grid, r, c)

        t2_adj = self.grid_to_adj(t2_grid)

        # 3. Build Overlay Graph
        graph = {}
        for r in range(self.N):
            for c in range(self.N):
                u = (r,c)
                v1 = t1_adj[u]
                v2 = t2_adj[u]
                graph[u] = [v1, v2]

        # 4. Union-Find Initialization
        parent = {}
        for r in range(self.N):
            for c in range(self.N):
                parent[(r,c)] = (r,c)

        def find(i):
            if parent[i] == i:
                return i
            parent[i] = find(parent[i])
            return parent[i]

        def union(i, j):
            root_i = find(i)
            root_j = find(j)
            if root_i != root_j:
                parent[root_i] = root_j
                return True
            return False

        # 5. Identify Initial Cycles
        visited = set()
        num_cycles = 0

        # Use a list to iterate deterministically or just loops
        for r in range(self.N):
            for c in range(self.N):
                start_node = (r,c)
                if start_node not in visited:
                    num_cycles += 1
                    curr = start_node
                    while curr not in visited:
                        visited.add(curr)
                        union(start_node, curr)

                        # Move to next
                        neighbors = graph[curr]
                        # We need to traverse edges. Since 'visited' tracks nodes,
                        # we just need to find the neighbor we haven't just come from.
                        # But here we are just establishing connectivity.
                        # Traversing by simple graph search (BFS/DFS) is enough to union them.
                        for nb in neighbors:
                             if nb not in visited:
                                 # This logic is slightly flawed for cycle traversal if we want to follow lines,
                                 # but for Connected Components (Union-Find), we just need to visit everything reachable.
                                 pass

                        # Wait, simple DFS/BFS to find component is better.
                        break # Let the DFS below handle it

        # Reset and do proper component finding
        parent = {}
        for r in range(self.N):
            for c in range(self.N):
                parent[(r,c)] = (r,c)

        visited = set()
        num_cycles = 0
        for r in range(self.N):
            for c in range(self.N):
                node = (r,c)
                if node not in visited:
                    num_cycles += 1
                    # BFS to find all nodes in this cycle/component
                    q = [node]
                    visited.add(node)
                    while q:
                        curr = q.pop(0)
                        union(node, curr)
                        for nb in graph[curr]:
                            if nb not in visited:
                                visited.add(nb)
                                q.append(nb)

        # 6. Merge Cycles
        # Repeat until 1 cycle remains
        print(f"Initial cycles: {num_cycles}")

        while num_cycles > 1:
            candidates = []

            # Scan all 2x2 windows for valid merge moves
            # A move is valid if:
            # 1. It forms a 2x2 loop of edges (parallel edges)
            # 2. The edges connect two DIFFERENT components

            for r in range(self.N - 1):
                for c in range(self.N - 1):
                    u = (r, c) # Top-Left
                    v1 = (r, c+1) # Top-Right
                    v2 = (r+1, c) # Bottom-Left
                    v3 = (r+1, c+1) # Bottom-Right

                    root_u = find(u)

                    # Check Horizontal Parallel Edges
                    # (u-v1) and (v2-v3)
                    # Note: We must check if these edges actually exist in the current graph
                    if v1 in graph[u] and v3 in graph[v2]:
                        root_v2 = find(v2)
                        if root_u != root_v2:
                            candidates.append(((r,c), 'H'))

                    # Check Vertical Parallel Edges
                    # (u-v2) and (v1-v3)
                    if v2 in graph[u] and v3 in graph[v1]:
                        root_v1 = find(v1)
                        if root_u != root_v1:
                            candidates.append(((r,c), 'V'))

            if not candidates:
                print("No valid merges found (Deadlock). Restarting...")
                return self.solve()

            # Randomly pick a merge
            (r, c), type = random.choice(candidates)

            u = (r, c)
            v1 = (r, c+1)
            v2 = (r+1, c)
            v3 = (r+1, c+1)

            if type == 'H':
                # Swap Horizontal edges to Vertical
                # Remove (u, v1) and (v2, v3)
                self.remove_edge(graph, u, v1)
                self.remove_edge(graph, v2, v3)
                # Add (u, v2) and (v1, v3)
                self.add_edge(graph, u, v2)
                self.add_edge(graph, v1, v3)
                # Union sets
                union(u, v2)
            else:
                # Swap Vertical edges to Horizontal
                # Remove (u, v2) and (v1, v3)
                self.remove_edge(graph, u, v2)
                self.remove_edge(graph, v1, v3)
                # Add (u, v1) and (v2, v3)
                self.add_edge(graph, u, v1)
                self.add_edge(graph, v2, v3)
                # Union sets
                union(u, v1)

            num_cycles -= 1
            if num_cycles % 10 == 0:
                print(f"Cycles remaining: {num_cycles}")

        # 7. Convert Graph to Grid Directions
        self.graph_to_grid(graph)
        return True

    def shuffle_window(self, grid, r, c):
        # 2x2 rotation logic
        if (grid[r][c] == self.RIGHT and grid[r][c+1] == self.LEFT and
            grid[r+1][c] == self.RIGHT and grid[r+1][c+1] == self.LEFT):
            grid[r][c] = self.DOWN; grid[r+1][c] = self.UP
            grid[r][c+1] = self.DOWN; grid[r+1][c+1] = self.UP
        elif (grid[r][c] == self.DOWN and grid[r+1][c] == self.UP and
              grid[r][c+1] == self.DOWN and grid[r+1][c+1] == self.UP):
            grid[r][c] = self.RIGHT; grid[r][c+1] = self.LEFT
            grid[r+1][c] = self.RIGHT; grid[r+1][c+1] = self.LEFT

    def grid_to_adj(self, grid):
        adj = {}
        for r in range(self.N):
            for c in range(self.N):
                d = grid[r][c]
                nr, nc = r, c
                if d == self.LEFT: nc -= 1
                elif d == self.RIGHT: nc += 1
                elif d == self.UP: nr -= 1
                elif d == self.DOWN: nr += 1
                adj[(r,c)] = (nr, nc)
        return adj

    def remove_edge(self, graph, u, v):
        if v in graph[u]: graph[u].remove(v)
        if u in graph[v]: graph[v].remove(u)

    def add_edge(self, graph, u, v):
        graph[u].append(v)
        graph[v].append(u)

    def graph_to_grid(self, graph):
        # Pick start node
        start = (0,0)
        visited = set()
        curr = start
        prev = graph[start][0] # Arbitrary prev

        # Traverse Hamiltonian Cycle
        # Note: 'graph' is adjacency list. Each node has degree 2.
        # We need to trace the path and assign directions.

        # Find the neighbor that is NOT prev to determine direction
        # Special case for start: just pick one neighbor as 'next', the other becomes 'prev' effectively

        # Actually, let's just trace.
        path = []
        curr = start
        # Find valid initial next
        nbs = graph[curr]
        next_node = nbs[0]

        # Traverse
        while len(path) < self.N * self.N:
            path.append(curr)
            visited.add(curr)

            # Determine direction to next_node
            r, c = curr
            nr, nc = next_node

            if nr == r and nc == c - 1: self.grid[r][c] = self.LEFT
            elif nr == r and nc == c + 1: self.grid[r][c] = self.RIGHT
            elif nr == r - 1 and nc == c: self.grid[r][c] = self.UP
            elif nr == r + 1 and nc == c: self.grid[r][c] = self.DOWN

            # Move
            prev = curr
            curr = next_node

            # Find new next
            nbs = graph[curr]
            if nbs[0] == prev:
                next_node = nbs[1]
            else:
                next_node = nbs[0]

    def print_grid(self):
        for y in range(self.N):
            row_str = []
            for x in range(self.N):
                row_str.append(str(self.grid[y][x]))
            print(",".join(row_str) + ",")
        print("\n----------\n")

    def generate_html(self, filename="HamiltonianCycleDomino.html"):
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
    <title>Hamiltonian Cycle Domino {self.N}x{self.N}</title>
    <style>
        body {{ font-family: sans-serif; text-align: center; padding: 0; margin: 0; }}
        h1 {{ margin: 10px; }}
        svg {{ border: 1px solid #ccc; background: #f9f9f9; }}
    </style>
</head>
<body>
    <h1>Hamiltonian Cycle Domino ({self.N}x{self.N})</h1>
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

    solver = HamiltonianCycleDomino(N)
    if solver.solve():
        solver.print_grid()
        solver.generate_html("HamiltonianCycleDomino.html")
    else:
        print("No solution found.")
