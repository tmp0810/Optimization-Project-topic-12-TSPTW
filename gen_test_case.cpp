// g++ -std=c++17 -O2 gen_org.cpp -o genData

#include <bits/stdc++.h>
#define MAX_SIZE 1001
using namespace std;
int n;
int t[MAX_SIZE][MAX_SIZE]; // Travel time array
int e[MAX_SIZE], l[MAX_SIZE], d[MAX_SIZE]; // earliest time, latest time, service duration
int arrivalTime[MAX_SIZE];
int departureTime[MAX_SIZE];
int serviceTime[MAX_SIZE];
int s[MAX_SIZE];
vector<int> route;

void genTestCase(char* filename, int N, int MAX_COORDINATE){
    n = N;
    srand(time(NULL));
    FILE* f = fopen(filename,"w");
    fprintf(f, "%d\n", n);

    int x[MAX_SIZE], y[MAX_SIZE];

    // Generate random coordinates
    for(int i = 1; i <= n; i++){
        x[i] = rand() % MAX_COORDINATE;
        y[i] = rand() % MAX_COORDINATE;
    }
    x[0] = 0;
    y[0] = 0;

    // Compute travel times based on Euclidean distance
    for(int i = 0; i <= n; i++){
        for(int j = 0; j <= n; j++){
            t[i][j] = int(sqrt(pow(x[i] - x[j], 2) + pow(y[i] - y[j], 2)));
            t[i][j] = t[i][j] * 10;
        }
    }

    // Generate a random route permutation s[]
    for(int i = 1; i <= n; i++){
        s[i] = i;
    }
    for(int k = 1; k <= n; k++){
        int i = rand() % n + 1;
        int j = rand() % n + 1;
        int tmp = s[i];
        s[i] = s[j];
        s[j] = tmp;
    }

    // Assign random service durations
    for(int i = 1; i <= n; i++){
        d[i] = (rand()%4 + 1) * 5; // e.g. 5, 10, 15, 20
    }

    // Simulate a route to derive arrival/service times
    departureTime[0] = 0;
    int current = 0;
    for(int i = 1; i <= n; i++){
        int next = s[i];
        arrivalTime[next]  = departureTime[current] + t[current][next];
        serviceTime[next]  = arrivalTime[next] + (rand()%5 + 1);
        departureTime[next] = serviceTime[next] + d[next];

        // e[next] / l[next] derived from arrival + random offset
        e[next] = serviceTime[next] - (rand()%10 + 1);
        l[next] = e[next] + (rand()%5 + 1) * 10;
        current = next;
    }

    // Write earliest, latest, and service durations
    for(int i = 1; i <= n; i++){
        fprintf(f, "%d %d %d\n", e[i], l[i], d[i]);
    }

    // Write the travel-time matrix
    for(int i = 0; i <= n; i++){
        for(int j = 0; j <= n; j++){
            fprintf(f, "%d ", t[i][j]);
        }
        fprintf(f, "\n");
    }

    fclose(f);
}

int main(int argc, char* argv[]) {
    // We expect exactly 3 command-line arguments:
    //   1) filename        -> e.g., "test_20.txt"
    //   2) N               -> e.g., "20"
    //   3) MAX_COORDINATE  -> e.g., "100"
    //
    // Usage example:
    //   ./genData test_20.txt 20 100

    if(argc < 4) {
        cerr << "Usage: " << argv[0]
             << " <filename> <N> <MAX_COORDINATE>\n\n"
             << "Example:\n"
             << "  " << argv[0] << " test_20.txt 20 100\n";
        return 1;
    }

    char* filename = argv[1];
    int N = stoi(argv[2]);
    int maxCoord = stoi(argv[3]);
    genTestCase(filename, N, maxCoord);

    cout << "Generated file: " << filename
         << " with N=" << N << " and MAX_COORDINATE=" << maxCoord << ".\n";

    return 0;
}
