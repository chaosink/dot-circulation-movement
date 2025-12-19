import sys
import random
from config import N, SVG_SIZE, MARGIN

# Increase recursion depth just in case
sys.setrecursionlimit(2000)

class HamiltonianCycleBackbite:
    def __init__(self, N=N):
        if N % 2 != 0:
            raise ValueError("N must be even for Hamiltonian Cycle on grid")
        self.N = N
        self.grid = [[0 for _ in range(N)] for _ in range(N)]

        # Directions
        self.LEFT = 1
        self.UP = 2
        self.RIGHT = 3
        self.DOWN = 4

    def solve(self):
        # 1. Initialize with a simple snake path (Hamiltonian Cycle)
        # 0,0 -> 0,N-1
        # 1,N-1 -> 1,0
        # 2,0 -> 2,N-1 ...
        # This forms a path visiting all nodes. We need to close it to a cycle.
        # Actually, let's just use the simple constructive loop from Method A/B as the starting point.
        # It's a valid Hamiltonian Cycle.

        # Initialize with 2x2 Clockwise (CW) loops in every block (Method B Level 0)
        # And then merge them trivially to form a snake or just merge all horizontal/vertical.
        # Let's just construct a standard snake cycle manually.

        # Simple Snake Cycle Construction:
        # Rows 0 to N-2: Snake back and forth
        # Row N-1: Return straight from (N-1, N-1 or 0) to (N-1, 0) and close to (0,0)

        # Let's construct adjacency list format first for easier manipulation
        # adj[u] = {v1, v2}
        self.adj = {}

        # Create a simple "lawnmower" pattern
        # (0,0)->(0,1)->...->(0,N-1)
        # (1,N-1)->(1,N-2)->...->(1,0)
        # ...
        # This visits everyone.
        # Edges:
        for r in range(self.N):
            if r % 2 == 0:
                # Left to Right
                for c in range(self.N - 1):
                    self.add_edge((r, c), (r, c+1))
                # Connect to row below at end
                if r < self.N - 1:
                    self.add_edge((r, self.N-1), (r+1, self.N-1))
            else:
                # Right to Left
                for c in range(self.N - 1, 0, -1):
                    self.add_edge((r, c), (r, c-1))
                # Connect to row below at start
                if r < self.N - 1:
                    self.add_edge((r, 0), (r+1, 0))

        # Close the loop: (N-1, 0) back to (0, 0)
        self.add_edge((self.N-1, 0), (0, 0))

        # Now we have a valid Hamiltonian Cycle.
        # 2. Perform Backbite Moves (Markov Chain Monte Carlo)
        # Number of iterations determines how "random" the result is.
        # For N=16 (256 nodes), ~N^3 or N^4 iterations are good.
        iterations = self.N * self.N * self.N * 10 # 256*16*10 = 40960

        # To perform backbite, we need to treat the cycle as a path temporarily.
        # Or we can view a backbite move on a cycle as:
        # 1. Pick a random edge (u, v) to delete -> Path from u to v.
        # 2. Pick one endpoint, say u.
        # 3. Pick a random neighbor w of u that is NOT v and NOT connected to u in path.
        # 4. Add edge (u, w). Now u has degree 2 (v_old, w), w has degree 3 (w_prev, w_next, u).
        # 5. The graph is now a "q" shape or "lollipop".
        # 6. Remove the edge (w, w_next) or (w, w_prev) to restore degree 2 at w.
        #    Which one? The one that creates a new Path.
        #    If we add (u, w), we create a cycle u-...-w-u.
        #    To break the cycle and form a path, we must remove an edge adjacent to w in the cycle part.
        #    Wait, if we add (u, w), we form a cycle involving u and w.
        #    The original path was u-...-w-...-v.
        #    Adding (u, w) closes the loop u-...-w-u.
        #    The other part w-...-v is now a tail attached to the loop at w.
        #    We need to form a Hamiltonian Path again.
        #    The new path should be: u (start) ... w ... (end).
        #    Actually, standard backbite on a path u...v:
        #    Add (u, w). The new path endpoints become:
        #    One is v (unchanged).
        #    The other is... let's see.
        #    Path: u - x - ... - w - z - ... - v
        #    Add (u, w).
        #    Cycle is u-x-...-w-u.
        #    We must break the cycle. We break (w, z).
        #    New Path: z - ... - v (tail) is now connected to w? No.
        #    New Path: z - ... - v is separate? No.
        #    Visual:
        #    u -- x -- ... -- w -- z -- ... -- v
        #    |________________|
        #
        #    If we remove (w, z):
        #    Path becomes: x -- ... -- w -- u (loop back) AND z -- ... -- v (disconnected?)
        #    No, that splits the graph.
        #
        #    We must remove (w, x) or (w, z)?
        #    The standard move is:
        #    If path is u...v, and we connect u to w (where w is adjacent to u in grid),
        #    and w is the neighbor of k in the path (i.e., ...-k-w-...).
        #    The new path is k-...-u-w-...-v? No.
        #
        #    Let's trace carefully.
        #    Path P: u = p_0, p_1, ..., p_k = w, ..., p_n = v.
        #    Add edge (u, w).
        #    Cycle C: p_0, p_1, ..., p_k, p_0.
        #    Remove edge (w, p_{k-1}) OR (w, p_{k+1}).
        #    If we remove (w, p_{k+1}):
        #    New Path: p_{k+1}, ..., p_n (part 1)
        #    AND p_0, ..., p_k (part 2, which is u...w)
        #    We need to traverse: p_{k+1}...p_n is a segment. p_0...p_k is a segment.
        #    They are disconnected unless p_n connected to p_0? No.
        #
        #    Wait, Backbite is usually defined on a PATH.
        #    To use it for a CYCLE, we can:
        #    1. Break the cycle at a random edge -> Path.
        #    2. Perform ONE Backbite move -> New Path.
        #    3. Try to close the New Path to a Cycle.
        #       If (endpoints are adjacent), close it and we have a New Cycle.
        #       If not, repeat step 2 with the new path until we can close it.
        #
        #    This is the "Reptile" algorithm.

        # Implementation:
        # Start with Cycle.
        # 1. Break a random edge -> Path with endpoints L, R.
        # 2. Loop:
        #    a. Pick an endpoint, say L.
        #    b. Pick a neighbor of L, say 'nb', that is NOT the node next to L in the path.
        #    c. If 'nb' is R:
        #       Re-connect L and R. WE HAVE A CYCLE. DONE (or continue for more mixing).
        #       If we want to mix more, we just immediately break a random edge again and continue.
        #    d. If 'nb' is some internal node:
        #       Perform Backbite:
        #       Let path be L ... nb - nb_next ... R
        #       Add (L, nb).
        #       Remove (nb, nb_next).
        #       New path: nb_next ... R (tail part) ? No.
        #       The path becomes: nb_next ... R ... (wait, connectivity)
        #       Let's reverse the segment L...nb.
        #       Old: L - p1 - p2 - ... - nb - nb_next - ... - R
        #       New: L is connected to nb.
        #       Path: nb_next - ... - R (unchanged part)
        #             AND nb - ... - L (reversed part)
        #       Are they connected?
        #       We removed (nb, nb_next). So they are disjoint?
        #       AH.
        #       If we add (L, nb), we create a loop L...nb...L.
        #       The rest is nb_next...R.
        #       We need to connect the rest to the loop?
        #       NO.
        #       We remove (nb, nb_next).
        #       The new path endpoints are: nb_next and R?
        #       No.
        #       The new path is: nb_next ... R ... (via original path) -> NO.
        #
        #       Correct Logic:
        #       Path: L = v_0, v_1, ..., v_k = nb, v_{k+1}, ..., v_n = R.
        #       Add edge (L, nb).
        #       Remove edge (nb, v_{k-1})? No, remove (nb, v_{k+1}) or (nb, v_{k-1}).
        #       Usually we remove (nb, v_{k-1}) if we keep R as endpoint?
        #       Let's say we remove (nb, v_{k+1}).
        #       New endpoints: v_{k+1} and R.
        #       Path: v_{k+1} ... v_n = R. (This segment is intact).
        #       AND v_k, v_{k-1} ... v_0. (This segment is reversed L...nb).
        #       Now L is connected to nb (v_0 to v_k).
        #       We need the whole thing to be one path.
        #       It is: R ... v_{k+1} (gap) v_k ... v_0.
        #       The gap is precisely the edge we removed! So they are NOT connected.
        #
        #       WAIT. The loop L...nb...L allows us to traverse the L...nb part in ANY direction.
        #       We enter at nb (from L), go to v_{k-1}...v_0? No.
        #
        #       Let's use the standard "Reversal" move.
        #       Path: v0, v1, ..., vk, ..., vn
        #       Add (v0, vk).
        #       Remove (vk, v{k-1}).
        #       New path: v{k-1}, v{k-2}, ..., v0, vk, v{k+1}, ..., vn.
        #       Endpoints: v{k-1} and vn.
        #       Yes! This works. The segment v0...vk-1 is reversed and attached to vk.

        # Data structure:
        # Since we need to reverse segments frequently, a simple list is O(N).
        # N=256, so O(N) is cheap enough.

        # Convert adj to list path
        path = self.extract_path_from_cycle()

        for _ in range(iterations):
            # path[0] is L, path[-1] is R.
            # Randomly pick L or R to act
            if random.random() < 0.5:
                # Act on path[0]
                active_end = path[0]
                other_end = path[-1]
                idx_active = 0
            else:
                # Act on path[-1]
                active_end = path[-1]
                other_end = path[0]
                idx_active = -1

            # Get valid neighbors of active_end in grid
            r, c = active_end
            nbs = []
            for dr, dc in [(-1,0), (1,0), (0,-1), (0,1)]:
                nr, nc = r+dr, c+dc
                if 0 <= nr < self.N and 0 <= nc < self.N:
                    nbs.append((nr, nc))

            # Choose a random neighbor
            target = random.choice(nbs)

            # Case 1: Target is the OTHER endpoint -> Cycle found!
            if target == other_end:
                # We found a cycle.
                # To mix more, we "bounce" off the cycle by immediately breaking a random edge.
                # Just rotate the path randomly to pick a new start/end?
                # Or just keep the cycle and break a random edge.
                # For simplicity in list representation:
                # If we connect ends, the path is a ring.
                # We can "rotate" the ring to any offset and break connection there.

                # Effectively: path is cyclic.
                # Pick random index i.
                # New path = path[i+1:] + path[:i+1]
                cut = random.randint(0, len(path)-2)
                path = path[cut+1:] + path[:cut+1]
                continue

            # Case 2: Target is adjacent in path (already connected)
            # e.g. target is path[1] (if active is path[0])
            # Do nothing.
            if (idx_active == 0 and target == path[1]) or \
               (idx_active == -1 and target == path[-2]):
                continue

            # Case 3: Target is some internal node
            # Perform Reversal Move.
            # Find index of target
            try:
                k = path.index(target)
            except ValueError:
                # Should not happen if logic is correct
                continue

            if idx_active == 0:
                # Active is v0. Target is vk.
                # Old Path: v0 ... vk-1, vk, vk+1 ... vn
                # New Path: v{k-1} ... v0, vk, vk+1 ... vn
                # Segment 0 to k-1 is reversed.
                # Python slicing: path[0:k] needs reversal.
                # New path = reversed(path[0:k]) + path[k:]
                path = path[0:k][::-1] + path[k:]
            else:
                # Active is vn. Target is vk.
                # Old Path: v0 ... vk-1, vk, vk+1 ... vn
                # New Path: v0 ... vk-1, vk, vn, vn-1 ... v{k+1}
                # Segment k+1 to n is reversed.
                # path[k+1:] needs reversal.
                # New path = path[:k+1] + reversed(path[k+1:])
                path = path[:k+1] + path[k+1:][::-1]

        # Final step: Ensure we have a cycle
        # The loop above runs for 'iterations'. The path might not be closed at the end.
        # We need to run until it closes.
        while True:
            # Check if closed
            head, tail = path[0], path[-1]
            # Check adjacency
            is_adjacent = False
            r, c = head
            if abs(head[0]-tail[0]) + abs(head[1]-tail[1]) == 1:
                is_adjacent = True

            if is_adjacent:
                # We are done!
                break

            # Perform one more step to try to close
            # (Copy paste logic from above)
            if random.random() < 0.5:
                active_end = path[0]
                idx_active = 0
            else:
                active_end = path[-1]
                idx_active = -1

            r, c = active_end
            nbs = []
            for dr, dc in [(-1,0), (1,0), (0,-1), (0,1)]:
                nr, nc = r+dr, c+dc
                if 0 <= nr < self.N and 0 <= nc < self.N:
                    nbs.append((nr, nc))

            target = random.choice(nbs)

            if (idx_active == 0 and target == path[1]) or \
               (idx_active == -1 and target == path[-2]):
                continue

            try:
                k = path.index(target)
            except ValueError:
                continue

            if idx_active == 0:
                path = path[0:k][::-1] + path[k:]
            else:
                path = path[:k+1] + path[k+1:][::-1]

        # Convert path to grid format
        self.path_to_grid(path)
        return True

    def add_edge(self, u, v):
        if u not in self.adj: self.adj[u] = []
        if v not in self.adj: self.adj[v] = []
        self.adj[u].append(v)
        self.adj[v].append(u)

    def extract_path_from_cycle(self):
        # Convert self.adj (cycle) to a list of nodes
        # Break (0,0) - (N-1,0) connection to make it a path initially
        # Actually, self.adj is not fully populated in __init__, wait.
        # I populated self.adj in step 1.

        # Start at (0,0)
        curr = (0,0)
        path = [curr]
        visited = {curr}

        # We need to follow edges.
        # self.adj has edges.
        # Since it's a cycle, every node has degree 2.

        while len(path) < self.N * self.N:
            nbs = self.adj[curr]
            # Pick neighbor not visited
            next_node = None
            for nb in nbs:
                if nb not in visited:
                    next_node = nb
                    break

            if next_node:
                visited.add(next_node)
                path.append(next_node)
                curr = next_node
            else:
                # Should satisfy N*N if it's a Hamiltonian Cycle
                break

        return path

    def path_to_grid(self, path):
        # path is a list of coordinates
        # It forms a cycle (last connects to first)

        # Create map for quick lookup
        # Or just iterate
        n = len(path)
        for i in range(n):
            u = path[i]
            v = path[(i+1)%n] # Next node (wrapping around)

            r, c = u
            nr, nc = v

            if nr == r and nc == c - 1: self.grid[r][c] = self.LEFT
            elif nr == r and nc == c + 1: self.grid[r][c] = self.RIGHT
            elif nr == r - 1 and nc == c: self.grid[r][c] = self.UP
            elif nr == r + 1 and nc == c: self.grid[r][c] = self.DOWN

    def print_grid(self):
        for y in range(self.N):
            row_str = []
            for x in range(self.N):
                row_str.append(str(self.grid[y][x]))
            print(",".join(row_str) + ",")
        print("\n----------\n")

    def generate_html(self, filename="HamiltonianCycleBackbite.html"):
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

                x1 = MARGIN + x * cell_size + cell_size // 2
                y1 = MARGIN + y * cell_size + cell_size // 2

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
    <title>Hamiltonian Cycle Backbite {self.N}x{self.N}</title>
    <style>
        body {{ font-family: sans-serif; text-align: center; padding: 0; margin: 0; }}
        h1 {{ margin: 10px; }}
        svg {{ border: 1px solid #ccc; background: #f9f9f9; }}
    </style>
</head>
<body>
    <h1>Hamiltonian Cycle Backbite ({self.N}x{self.N})</h1>
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

    solver = HamiltonianCycleBackbite(N)
    if solver.solve():
        solver.print_grid()
        solver.generate_html("HamiltonianCycleBackbite.html")
    else:
        print("No solution found.")
