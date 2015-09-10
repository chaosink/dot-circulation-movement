#include <iostream>
#include <cstdlib>
#include <cstring>
using namespace std;

int N = 2;

string Arrow(int n) {
	switch(n) {
		case 1: return "←"; break;
		case 2: return "↑"; break;
		case 3: return "→"; break;
		case 4: return "↓"; break;
	}
	return "";
}

bool Valid(int y, int x) {
	if(y < 0 || y >= N || x < 0 || x >= N) return false;
	return true;
}

void Traverse(int *a, int x, int y, int n) {
	if(n == N * N && ((x == 1 && y == 0) || (x == 0 && y == 1))) {
		if(x == 1 && y == 0) a[y * N + x] = 1;
		if(x == 0 && y == 1) a[y * N + x] = 4;
		cout << endl;
//		for(int i = N - 1; i >= 0; i--) {
		for(int i = 0; i < N; i++) {
//			for(int j = 0; j < N; j++) cout << Arrow(a[i * N + j]) << " ";
			for(int j = 0; j < N; j++) cout << a[i * N + j] << ",";
			cout << endl;
		}
		cout << endl << "----------" << endl;
		a[y * N + x] = 0;
		return;
	}
	if(Valid(y - 1, x) && !a[(y - 1) * N + x]) {
		a[y * N + x] = 4;
		Traverse(a, x, y - 1, n + 1);
		a[y * N + x] = 0;
	}
	if(Valid(y, x - 1) && !a[y * N + x - 1]) {
		a[y * N + x] = 1;
		Traverse(a, x - 1, y, n + 1);
		a[y * N + x] = 0;
	}
	if(Valid(y + 1, x) && !a[(y + 1) * N + x]) {
		a[y * N + x] = 2;
		Traverse(a, x, y + 1, n + 1);
		a[y * N + x] = 0;
	}
	if(Valid(y, x + 1) && !a[y * N + x + 1]) {
		a[y * N + x] = 3;
		Traverse(a, x + 1, y, n + 1);
		a[y * N + x] = 0;
	}
}

int main(int argc, char **argv) {
	if(argc > 1) N = atoi(argv[1]);

	cout << "----------" << endl;
	int *a = new int[N * N];
	Traverse(a, 0, 0, 1);

	return 0;
}
