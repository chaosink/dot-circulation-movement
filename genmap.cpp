#include <iostream>
#include <cstdlib>
#include <cstring>
using namespace std;

const int N = 2;
int a[N][N];

bool Valid(int x, int y) {
	if(x < 0 || x >= N || y < 0 || y >= N) return false;
	return true;
}

void Traverse(int x, int y, int n) {
	if(n == N * N) {
		if(x == 1 && y == 0) a[x][y] = 3;
		if(x == 0 && y == 1) a[x][y] = 2;
		for(int i = 0; i < N; i++) {
			for(int j = 0; j < N; j++) cout << a[i][j] << " ";
			cout << endl;
		}
		cout << "----------" << endl;
		return;
	}
	if(Valid(x - 1, y) && !a[x - 1][y]) {
		a[x][y] = 1;
		Traverse(x - 1, y, n + 1);
		a[x][y] = 0;
	}
	if(Valid(x, y - 1) && !a[x][y - 1]) {
		a[x][y] = 2;
		Traverse(x, y - 1, n + 1);
		a[x][y] = 0;
	}
	if(Valid(x + 1, y) && !a[x + 1][y]) {
		a[x][y] = 3;
		Traverse(x + 1, y, n + 1);
		a[x][y] = 0;
	}
	if(Valid(x, y + 1) && !a[x][y + 1]) {
		a[x][y] = 4;
		Traverse(x, y + 1, n + 1);
		a[x][y] = 0;
	}
}

int main(int argc, char **argv) {
	while(1) {
		memset(a, 0, sizeof(a));
		Traverse(0, 0, 1);
	}
	return 0;
}
