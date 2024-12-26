from collections import deque
import time
start_time = time.time()
n = int(input().strip())
e = [-1]
l = [-1]
d = [-1]
for _ in range(n):
    e_, l_, d_ = map(int, input().strip().split())
    e.append(e_)
    l.append(l_)
    d.append(d_)
t = []
for _ in range(n + 1):
    t.append(list(map(int, input().strip().split())))

def start_path(a):
    greedy = list(a)
    greedy.sort()

    start_path_visited = [False for i in range (n + 1)]
    path = []
    for i in range (1, n + 1):
        for j in range (1, n + 1):
            if greedy[i] == a[j] and start_path_visited[j] == False:
                path.append(j)
                start_path_visited[j] = True
                break
    return path

def Calculate(path):
    check = True
    cur_pos = 0
    total_time = 0
    travel_time = 0
    for i in range (0, n):
        total_time += t[cur_pos][path[i]]
        travel_time += t[cur_pos][path[i]]
        if total_time <= l[path[i]]:   
            total_time = max(total_time, e[path[i]])
            total_time += d[path[i]]
            cur_pos = path[i]
        else: 
            check = False
            break
    if check == True:
        return travel_time
    else:   
        return 99999999999

start_path1 = start_path(e)
start_path2 = start_path(l)
tabu = deque()
tabu.append((1, start_path1))
tabu.append((1, start_path2))

value_path1 = Calculate(start_path1)
value_path2 = Calculate(start_path2)
cur_MIN = min(value_path1, value_path2)
optimal_path = None
if cur_MIN == value_path1:
    optimal_path = start_path1
else: optimal_path = start_path2

run_time = 180
depth = 6 if n <= 30 else (2 if n <= 300 else 1)
vertex_check = n // 2 if n < 100 else (n // 6 if n <= 300 else 10)

while len(tabu) > 0: 
    element = tabu.popleft()
    if element[0] <= depth:
        cur_best_element = [] 
        found_better = False
        for i in range (0, n - 1):
            for j in range (i + 1, min(i + vertex_check, n)):
                try_path = element[1][:]
                try_path = try_path[:i] + try_path[i + 1:j] + try_path[i:i+1] + try_path[j:]
                travel_time = Calculate(try_path)
                if travel_time < cur_MIN:
                    found_better = True 
                    cur_best_element = []
                    cur_best_element.append((0, try_path[:]))
                    optimal_path = try_path[:]
                    cur_MIN = travel_time 
                elif travel_time == cur_MIN:
                    cur_best_element.append((0, try_path))
                else:
                    cur_best_element.append((element[0] + 1, try_path))
                if time.time() - start_time > run_time: 
                    break
        if found_better == True and len(cur_best_element) > 0:
            tabu.clear()
        for i in cur_best_element:
            tabu.append(i)
    if time.time() - start_time > run_time: 
        break

print(n)
for i in optimal_path:
    print(i, end = ' ')
    
