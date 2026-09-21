#include <vector>
#include <algorithm>
#include <iostream>

using namespace std;

int n, k;


void gen(int i, int c){
    if (i == n - k + 1 && c){
        for (int j = 0; j <= n - k; j++){
            if (j == 0) cout << "AAA";
            else if (j == 1) cout << "A";
            else cout << "B";
            cout << "\n";
        }
        return;
    }
    else{
        for (int j = 0; j <= 2; j++){
            if (c == 1) continue;
            else{
                v[i] = j;
                if (j == 0) c = 1;
                gen(i + 1, c);
            }
        }
        return;
    }
}

vector<int> v;

int main(){
    cin >> n >> k;
    v.resize(n - k + 1);
    gen(0, 0);
    return 0;
}
