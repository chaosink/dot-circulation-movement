import sys
from config import N, SVG_SIZE, MARGIN

class HamiltonianCycleInteractiveGenerator:
    def __init__(self, N=N):
        self.N = N

    def generate(self, filename="HamiltonianCycleBackbiteInteractive.html"):
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Hamiltonian Cycle Backbite Interactive</title>
    <style>
        body {{
            font-family: sans-serif;
            display: flex;
            flex-direction: column;
            align-items: center;
            background-color: #f0f0f0;
            margin: 0;
            padding: 0;
        }}
        h1 {{ margin: 10px; }}
        canvas {{
            background-color: white;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            margin-top: 20px;
        }}
        .controls {{
            margin-top: 20px;
            text-align: center;
        }}
        .status {{
            margin-top: 10px;
            font-weight: bold;
            color: #333;
        }}
        .instructions {{
            color: #666;
            margin-bottom: 10px;
        }}
    </style>
</head>
<body>
    <h1>Hamiltonian Cycle Backbite Interactive ({self.N}x{self.N})</h1>
    <div class="instructions">
        Press <strong>SPACE</strong> to perform one Backbite step.<br>
        Press <strong>ENTER</strong> to auto-play/pause.<br>
        Press <strong>+</strong> to speed up (reduce delay), <strong>-</strong> to slow down (increase delay).
    </div>
    <canvas id="gridCanvas" width="{SVG_SIZE}" height="{SVG_SIZE}"></canvas>
    <div class="status" id="statusText">State: Cycle (Closed)</div>
    <div class="status" id="speedText">Delay: 50 ms</div>

    <script>
        const N = {self.N};
        const canvas = document.getElementById('gridCanvas');
        const ctx = canvas.getContext('2d');
        const statusText = document.getElementById('statusText');
        const speedText = document.getElementById('speedText');

        // Calculate cell size based on canvas width
        const margin = {MARGIN};
        const width = canvas.width - 2 * margin;
        const cellSize = width / N;

        // Path representation: array of coordinates (r, c)
        let path = [];
        let isPlaying = false;
        let animationId = null;
        let frameDelay = 50; // Initial delay in ms

        function init() {{
            // Initialize with simple snake path
            path = [];
            for (let r = 0; r < N; r++) {{
                if (r % 2 === 0) {{
                    for (let c = 0; c < N; c++) path.push({{r: r, c: c}});
                }} else {{
                    for (let c = N - 1; c >= 0; c--) path.push({{r: r, c: c}});
                }}
            }}
            // Draw initial state
            draw();
        }}

        function draw() {{
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            // Draw Grid (Optional)
            ctx.strokeStyle = '#eee';
            ctx.lineWidth = 1;
            for(let i=0; i<=N; i++) {{
                let p = margin + i * cellSize;
                ctx.beginPath(); ctx.moveTo(p, margin); ctx.lineTo(p, margin + N*cellSize); ctx.stroke();
                ctx.beginPath(); ctx.moveTo(margin, p); ctx.lineTo(margin + N*cellSize, p); ctx.stroke();
            }}

            if (path.length === 0) return;

            // Draw Path
            ctx.lineWidth = 1;
            ctx.lineCap = 'round';
            ctx.lineJoin = 'round';

            for (let i = 0; i < path.length - 1; i++) {{
                const u = path[i];
                const v = path[i+1];

                const x1 = margin + u.c * cellSize + cellSize / 2;
                const y1 = margin + u.r * cellSize + cellSize / 2;
                const x2 = margin + v.c * cellSize + cellSize / 2;
                const y2 = margin + v.r * cellSize + cellSize / 2;

                // Color gradient
                const ratio = i / path.length;
                const r = Math.floor(255 * ratio);
                const b = Math.floor(255 * (1 - ratio));
                ctx.strokeStyle = `rgb(${{r}}, 0, ${{b}})`;

                ctx.beginPath();
                ctx.moveTo(x1, y1);
                ctx.lineTo(x2, y2);
                ctx.stroke();
            }}

            // Highlight Endpoints
            const head = path[0];
            const tail = path[path.length - 1];

            const hx = margin + head.c * cellSize + cellSize / 2;
            const hy = margin + head.r * cellSize + cellSize / 2;
            const tx = margin + tail.c * cellSize + cellSize / 2;
            const ty = margin + tail.r * cellSize + cellSize / 2;

            // Start (Blue)
            ctx.fillStyle = 'blue';
            ctx.beginPath(); ctx.arc(hx, hy, 2, 0, Math.PI * 2); ctx.fill();

            // End (Red)
            ctx.fillStyle = 'red';
            ctx.beginPath(); ctx.arc(tx, ty, 2, 0, Math.PI * 2); ctx.fill();

            // Check closure
            const isClosed = (Math.abs(head.r - tail.r) + Math.abs(head.c - tail.c)) === 1;

            if (isClosed) {{
                // Draw closing link
                ctx.strokeStyle = 'purple';
                ctx.lineWidth = 1;
                ctx.beginPath();
                ctx.moveTo(hx, hy);
                ctx.lineTo(tx, ty);
                ctx.stroke();
                statusText.innerText = "State: Cycle (Closed)";
                statusText.style.color = "purple";

                // Auto-pause if playing
                if (isPlaying) {{
                    isPlaying = false;
                    clearTimeout(animationId);
                }}
            }} else {{
                statusText.innerText = "State: Path (Open)";
                statusText.style.color = "#333";
            }}
        }}

        function backbite() {{
            let changed = false;
            let attempts = 0;
            const maxAttempts = 100; // Prevent infinite loop if stuck (unlikely)

            while (!changed && attempts < maxAttempts) {{
                attempts++;

                // 1. Pick an endpoint (0 or length-1)
                const idxActive = Math.random() < 0.5 ? 0 : path.length - 1;
                const activeEnd = path[idxActive];

                // 2. Pick a neighbor
                const nbs = [];
                const dirs = [[-1,0], [1,0], [0,-1], [0,1]];
                for(let d of dirs) {{
                    const nr = activeEnd.r + d[0];
                    const nc = activeEnd.c + d[1];
                    if (nr >= 0 && nr < N && nc >= 0 && nc < N) {{
                        nbs.push({{r: nr, c: nc}});
                    }}
                }}

                const target = nbs[Math.floor(Math.random() * nbs.length)];

                // Helper to check object equality
                const eq = (a, b) => a.r === b.r && a.c === b.c;

                // Case 1: Target is the other endpoint -> Cycle!
                // Just rotate the cycle randomly
                if ((idxActive === 0 && eq(target, path[path.length-1])) ||
                    (idxActive !== 0 && eq(target, path[0]))) {{

                    // It's already closed. We can simply rotate the array to pick a new breakpoint.
                    const cut = Math.floor(Math.random() * (path.length - 1));
                    // path = path[cut+1:] + path[:cut+1]
                    const part1 = path.slice(0, cut + 1);
                    const part2 = path.slice(cut + 1);
                    path = part2.concat(part1);

                    changed = true; // Count rotation as a change (endpoints move)
                    continue;
                }}

                // Case 2: Target is adjacent in path (neighbor in list) -> Ignore
                if (idxActive === 0) {{
                    if (eq(target, path[1])) continue;
                }} else {{
                    if (eq(target, path[path.length - 2])) continue;
                }}

                // Case 3: Reversal
                // Find index k of target
                let k = -1;
                for(let i=0; i<path.length; i++) {{
                    if (eq(path[i], target)) {{
                        k = i;
                        break;
                    }}
                }}

                if (k === -1) continue; // Should not happen

                if (idxActive === 0) {{
                    const segment = path.slice(0, k);
                    segment.reverse();
                    path = segment.concat(path.slice(k));
                }} else {{
                    const segment = path.slice(k + 1);
                    segment.reverse();
                    path = path.slice(0, k + 1).concat(segment);
                }}
                changed = true;
            }}
        }}

        // Input Handling
        window.addEventListener('keydown', (e) => {{
            if (e.code === 'Space') {{
                e.preventDefault(); // Prevent scrolling
                if (isPlaying) {{
                    isPlaying = false;
                    cancelAnimationFrame(animationId);
                }}
                backbite();
                draw();
            }} else if (e.code === 'Enter') {{
                e.preventDefault();
                isPlaying = !isPlaying;
                if (isPlaying) {{
                    loop();
                }} else {{
                    clearTimeout(animationId);
                }}
            }} else if (e.key === '+' || e.key === '=') {{
                // Speed up = Decrease delay
                frameDelay = Math.max(frameDelay - 10, 0);
                speedText.innerText = `Delay: ${{frameDelay}} ms`;
            }} else if (e.key === '-' || e.key === '_') {{
                // Slow down = Increase delay
                frameDelay = Math.min(frameDelay + 10, 1000);
                speedText.innerText = `Delay: ${{frameDelay}} ms`;
            }}
        }});

        function loop() {{
            if (!isPlaying) return;

            backbite();
            draw();

            // Use setTimeout for variable delay
            animationId = setTimeout(loop, frameDelay);
        }}

        init();
    </script>
</body>
</html>
"""
        with open(filename, "w", encoding="utf-8") as f:
            f.write(html_content)
        print(f"HTML generator saved to {filename}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        try:
            N = int(sys.argv[1])
        except:
            pass

    generator = HamiltonianCycleInteractiveGenerator(N)
    generator.generate("HamiltonianCycleBackbiteInteractive.html")
