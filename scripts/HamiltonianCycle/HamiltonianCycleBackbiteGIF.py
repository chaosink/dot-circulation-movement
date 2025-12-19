import sys
import random
from PIL import Image, ImageDraw
from config import N, SVG_SIZE, MARGIN

# Increase recursion depth just in case
sys.setrecursionlimit(2000)

class HamiltonianCycleGIF:
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

        # Visualization settings
        self.width = SVG_SIZE
        self.height = SVG_SIZE
        self.margin = MARGIN
        self.cell_size = (self.width - 2 * self.margin) / self.N
        self.frames = []

    def solve(self, steps=1000, frame_interval=10):
        # 1. Initialize with a simple snake path (Hamiltonian Cycle)
        # adj[u] = {v1, v2}
        self.adj = {}

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

        # Close the loop
        self.add_edge((self.N-1, 0), (0, 0))

        # Convert to path list for Backbite
        path = self.extract_path_from_cycle()

        # Capture initial frame
        self.frames.append(self.draw_frame(path))

        # 2. Perform Backbite Moves and Capture Frames
        print(f"Generating {steps} steps of evolution...")

        for step in range(steps):
            # Backbite logic (one step)
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

            # Case 1: Close cycle (just rotate)
            if (idx_active == 0 and target == path[-1]) or \
               (idx_active == -1 and target == path[0]):
                cut = random.randint(0, len(path)-2)
                path = path[cut+1:] + path[:cut+1]

            # Case 2: Adjacent in path (ignore)
            elif (idx_active == 0 and target == path[1]) or \
                 (idx_active == -1 and target == path[-2]):
                pass

            # Case 3: Reversal
            else:
                try:
                    k = path.index(target)
                    if idx_active == 0:
                        path = path[0:k][::-1] + path[k:]
                    else:
                        path = path[:k+1] + path[k+1:][::-1]
                except ValueError:
                    pass

            # Capture frame every 'frame_interval' steps
            if step % frame_interval == 0:
                self.frames.append(self.draw_frame(path))

        # Ensure closure at the end
        print("Finalizing cycle...")
        max_attempts = 10000
        for _ in range(max_attempts):
            head, tail = path[0], path[-1]
            if abs(head[0]-tail[0]) + abs(head[1]-tail[1]) == 1:
                break

            # One more step
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
                if idx_active == 0:
                    path = path[0:k][::-1] + path[k:]
                else:
                    path = path[:k+1] + path[k+1:][::-1]
            except ValueError:
                continue

        self.frames.append(self.draw_frame(path, is_closed=True))

        # Save GIF
        print("Saving GIF...")
        self.frames[0].save('HamiltonianCycleBackbiteGIF.gif',
                           save_all=True,
                           append_images=self.frames[1:],
                           optimize=False,
                           duration=200,
                           loop=0)
        print("Done! Saved to HamiltonianCycleBackbiteGIF.gif")

        # Update final grid state for printing
        self.path_to_grid(path)
        return True

    def add_edge(self, u, v):
        if u not in self.adj: self.adj[u] = []
        if v not in self.adj: self.adj[v] = []
        self.adj[u].append(v)
        self.adj[v].append(u)

    def extract_path_from_cycle(self):
        curr = (0,0)
        path = [curr]
        visited = {curr}
        while len(path) < self.N * self.N:
            nbs = self.adj[curr]
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
                break
        return path

    def draw_frame(self, path, is_closed=False):
        img = Image.new('RGB', (self.width, self.height), color='white')
        draw = ImageDraw.Draw(img)

        # Draw path segments
        # Color gradient? Or just simple color.
        # Let's use a gradient from start (Blue) to end (Red) to visualize the snake nature
        n = len(path)
        for i in range(n - 1):
            u = path[i]
            v = path[i+1]

            x1 = self.margin + u[1] * self.cell_size + self.cell_size // 2
            y1 = self.margin + u[0] * self.cell_size + self.cell_size // 2
            x2 = self.margin + v[1] * self.cell_size + self.cell_size // 2
            y2 = self.margin + v[0] * self.cell_size + self.cell_size // 2

            # Interpolate color
            r_val = int(255 * (i / n))
            b_val = int(255 * (1 - i / n))
            color = (r_val, 0, b_val)

            draw.line([(x1, y1), (x2, y2)], fill=color, width=3)
            # draw.rectangle([x1-2, y1-2, x1+2, y1+2], fill=color)

        # Highlight endpoints
        head = path[0]
        tail = path[-1]

        hx = self.margin + head[1] * self.cell_size + self.cell_size // 2
        hy = self.margin + head[0] * self.cell_size + self.cell_size // 2
        tx = self.margin + tail[1] * self.cell_size + self.cell_size // 2
        ty = self.margin + tail[0] * self.cell_size + self.cell_size // 2

        draw.ellipse([hx-4, hy-4, hx+4, hy+4], fill='blue', outline='black') # Start
        draw.ellipse([tx-4, ty-4, tx+4, ty+4], fill='red', outline='black')  # End

        if is_closed:
            draw.line([(hx, hy), (tx, ty)], fill='purple', width=3)

        return img

    def path_to_grid(self, path):
        n = len(path)
        for i in range(n):
            u = path[i]
            v = path[(i+1)%n]
            r, c = u
            nr, nc = v
            if nr == r and nc == c - 1: self.grid[r][c] = self.LEFT
            elif nr == r and nc == c + 1: self.grid[r][c] = self.RIGHT
            elif nr == r - 1 and nc == c: self.grid[r][c] = self.UP
            elif nr == r + 1 and nc == c: self.grid[r][c] = self.DOWN

if __name__ == "__main__":
    if len(sys.argv) > 1:
        try:
            N = int(sys.argv[1])
        except:
            pass

    # Need Pillow library
    try:
        import PIL
    except ImportError:
        print("Error: Pillow library is required for GIF generation.")
        print("Please run: pip install Pillow")
        sys.exit(1)

    solver = HamiltonianCycleGIF(N)
    # Generate GIF with more frames (capturing every 1 step of 2000 total steps to keep file size reasonable)
    solver.solve(steps=2000, frame_interval=1)
