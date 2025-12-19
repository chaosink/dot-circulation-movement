#ifndef HAMILTONIAN_CYCLE_WILSON_HPP
#define HAMILTONIAN_CYCLE_WILSON_HPP

#include <vector>
#include <random>
#include <map>
#include <utility>
#include <algorithm>

class HamiltonianCycleWilson {
public:
    int N;
    std::vector<std::vector<int>> grid;
    bool is_ccw;
    const int LEFT = 1;
    const int UP = 2;
    const int RIGHT = 3;
    const int DOWN = 4;

    HamiltonianCycleWilson(int n) : N(n) {
        if (N % 2 != 0) N++; // Ensure even size
        grid.resize(N, std::vector<int>(N, 0));
    }

    void solve() {
        std::random_device rd;
        std::mt19937 gen(rd());

        // Randomly choose direction (CW or CCW)
        std::bernoulli_distribution d(0.5);
        is_ccw = d(gen);

        // 1. Initialize with 2x2 loops in every block
        for (int r = 0; r < N; r += 2) {
            for (int c = 0; c < N; c += 2) {
                if (!is_ccw) {
                    grid[r][c] = RIGHT;
                    grid[r][c + 1] = DOWN;
                    grid[r + 1][c + 1] = LEFT;
                    grid[r + 1][c] = UP;
                } else {
                    grid[r][c] = DOWN;
                    grid[r + 1][c] = RIGHT;
                    grid[r + 1][c + 1] = UP;
                    grid[r][c + 1] = LEFT;
                }
            }
        }

        // 2. Generate Uniform Spanning Tree (UST) on (N/2)x(N/2) coarse grid
        int R = N / 2;
        int C = N / 2;
        std::vector<std::vector<bool>> in_tree(R, std::vector<bool>(C, false));

        std::uniform_int_distribution<> disR(0, R - 1);
        std::uniform_int_distribution<> disC(0, C - 1);

        int root_r = disR(gen);
        int root_c = disC(gen);
        in_tree[root_r][root_c] = true;

        int remaining_nodes = R * C - 1;

        while (remaining_nodes > 0) {
            int curr_r, curr_c;
            do {
                curr_r = disR(gen);
                curr_c = disC(gen);
            } while (in_tree[curr_r][curr_c]);

            int start_r = curr_r;
            int start_c = curr_c;
            std::map<std::pair<int, int>, std::pair<int, int>> walk_path;

            int u_r = start_r;
            int u_c = start_c;

            while (!in_tree[u_r][u_c]) {
                std::vector<std::pair<int, int>> valid_moves;
                if (u_r > 0) valid_moves.push_back({u_r - 1, u_c});
                if (u_r < R - 1) valid_moves.push_back({u_r + 1, u_c});
                if (u_c > 0) valid_moves.push_back({u_r, u_c - 1});
                if (u_c < C - 1) valid_moves.push_back({u_r, u_c + 1});

                std::uniform_int_distribution<> disMove(0, static_cast<int>(valid_moves.size() - 1));
                std::pair<int, int> next = valid_moves[disMove(gen)];

                walk_path[{u_r, u_c}] = next;
                u_r = next.first;
                u_c = next.second;
            }

            u_r = start_r;
            u_c = start_c;
            while (!in_tree[u_r][u_c]) {
                in_tree[u_r][u_c] = true;
                remaining_nodes--;

                std::pair<int, int> next = walk_path[{u_r, u_c}];
                merge_blocks(u_r, u_c, next.first, next.second);
                u_r = next.first;
                u_c = next.second;
            }
        }
    }

private:
    void merge_blocks(int r1, int c1, int r2, int c2) {
        int fr1 = r1 * 2;
        int fc1 = c1 * 2;
        int fr2 = r2 * 2;
        int fc2 = c2 * 2;

        if (r2 == r1 && c2 == c1 + 1) { // Right neighbor
            if (!is_ccw) {
                grid[fr1][fc1 + 1] = RIGHT;
                grid[fr2 + 1][fc2] = LEFT;
            } else {
                grid[fr1 + 1][fc1 + 1] = RIGHT;
                grid[fr2][fc2] = LEFT;
            }
        } else if (r2 == r1 && c2 == c1 - 1) { // Left neighbor
            merge_blocks(r2, c2, r1, c1);
        } else if (c2 == c1 && r2 == r1 + 1) { // Bottom neighbor
            if (!is_ccw) {
                grid[fr1 + 1][fc1 + 1] = DOWN;
                grid[fr2][fc2] = UP;
            } else {
                grid[fr1 + 1][fc1] = DOWN;
                grid[fr2][fc2 + 1] = UP;
            }
        } else if (c2 == c1 && r2 == r1 - 1) { // Top neighbor
            merge_blocks(r2, c2, r1, c1);
        }
    }
};

#endif
