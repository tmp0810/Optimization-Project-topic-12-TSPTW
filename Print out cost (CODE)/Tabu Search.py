from collections import deque
import time
start_time = time.time() # start_time of the code

'''
    Nhập đầu vào từ file các giá trị e, l, d, t - Read from file, input e, l, d, t
'''
with open(' ', 'r') as file: # Please insert your path to your test case here
    n = int(file.readline().strip())
    e = [-1]
    l = [-1]
    d = [-1]
    for _ in range(n):
        e_, l_, d_ = map(int, file.readline().strip().split())
        e.append(e_)
        l.append(l_)
        d.append(d_)
    t = []
    for _ in range(n + 1):
        t.append(list(map(int, file.readline().strip().split())))

'''
    Sắp xếp e, l vào 1 tuple sau đó sắp xếp lại tuple theo e (e bằng nhau thì theo l)
    Đây sẽ là start_path - đường đi thỏa mãn các ràng buộc đề bài, cho đây là đường đi xuất phát và cần tối ưu

    Using 2 sorted path by e: start of time window and l: end of time window as the 2 starting path of tabu search
'''

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

'''
    Hàm tính toán giá trị thời gian của đường đi - Function for path time calculation (must be n vertices)
'''

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

'''
    Khởi tạo các biến - Initialization
'''

start_path1 = start_path(e)
start_path2 = start_path(l)
tabu = deque()
tabu.append((1, start_path1))
tabu.append((1, start_path2))

'''
    Sử dụng thuật toán tabu và dịch chuyển 1 điểm để tìm đường đi tối ưu hơn đường đi trước:
    - Tabu Search: Trong trường hợp nếu dịch chuyển 1 điểm xuống mà đường đi không tốt hơn, lưu nó lại vào tabu. Trong trường hợp tìm được đường đi mới tốt hơn, xóa mọi phần tử trong tabu và tìm kiếm từ đường đi mới. 
    - Code:
        + Tabu: một list (Queue) trong đó lưu 2 giá trị
            • Giá trị đầu tiên lưu số depth - số lần chấp nhận đi đường đi thiệt thòi để tìm local maximum tốt hơn
            • Giá trị thứ hai lưu đường đi hiện tại 

    Using the tabu algorithm and 1-shift mode to find a more optimal path than the previous path:
    - Tabu Search: In the case where shifting a point back does not result in a better path, store it in the tabu list. If a new, better path is found, clear all elements in the tabu list and continue searching from the new path.
    - Code:
        + Tabu: a list (deque) that stores 2 values
            • The first value stores depth - the number of times to accept taking a suboptimal path to find a better local maximum.
            • The second value stores the current path.
    Ex: (2, [1, 2, 3, 4, 5]) is a tuple in tabu
         ^         ^
         |         |
       depth      path
''' 

value_path1 = Calculate(start_path1)
value_path2 = Calculate(start_path2)
cur_MIN = min(value_path1, value_path2)
optimal_path = None
if cur_MIN == value_path1:
    optimal_path = start_path1
else: optimal_path = start_path2

'''
    Trong vòng lặp while True, chạy đến khi nào thời gian tối đa cho phép (180 giây)
    Trong đó:
        - Pop phần tử đầu tiên của tabu, nếu depth lớn hơn cho phép thì xóa luôn, nếu không tìm kiếm từ đó
        - list_optimal_path: lưu lại những đường đi thỏa mãn ràng buộc đề bài và tốt hơn giá trị start_path để sau vòng lặp thêm nó vào tabu (cho TH từ 1 đường đi cho ra nhiều đường đi tối ưu như nhau)
        - Mỗi bước lặp lấy ra phần tử đầu tiên của tabu 
            + Nếu đường đi nhanh hơn cur_MIN hiện tại ==> đã tìm được một local_maximum mới ==> bool found_better = True khi đó sẽ xóa toàn bộ phần tử trong tabu và tiếp tục tìm kiếm từ đường đi đấy, reset giá trị đầu tiên về 0 và lưu vào cur_best_element
            + Nếu đường đi nhanh = cur_MIN hiện tại ==> thêm nó vào cur_best_element
            + Nếu không tăng depth cho đường đi đó (path.depth, path) -> (path.depth + 1, path) và thêm vào cur_best_element
        - Sau khi xử lý xong, thêm các phần tử trong cur_best_element vào tabu và tiếp tục vòng while
    Các tham số có thể thay đổi nhằm tối ưu:
        + depth: số lần "chịu thiệt" 
        + vertex_check: số điểm tối đa cho phép 1 điểm dịch xuống

    In while True loop, we will run until time limit exceed (180 seconds)
    Denote:
        - Pop the first element of tabu, if depth is higher than max-depth, then we will remove it, else continue searching from there
        - list_optimal_path: store paths that satisfy the problem constraints and are better than the start_path value to add back to the tabu later (in case from 1 path there exist more than 1 better solution).
        - For each iteration, we will pop the first element in the tabu
            + If the new path is better than cur_Min ==> we have found a new local minimum ==> bool found_better = True which mean we will erase everything from the tabu table and continue searching from there, reset the path's depth to 0 and save to cur_best_element
            + If the new path is = cur_Min ==> only save it back to cur_best_element
            + Else increase the path depth from (path.depth, path) -> (path.depth + 1, path) and add to cur_best_element
        - After iteration, we will add everything from cur_best_element to tabu and continue searching
    Parameters we can change to further optimize:
        + depth: the maximum number of "worsening move" we accept
        + vertex_check: the number of vertex at most a point can shift back
'''

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

'''
    In ra kết quả tìm được, trong TH không tìm được in ra 99999999999 
    Print out the answer. In case no solution found print 99999999999
'''

# print("TIME_TAKEN:", time.time() - start_time)
# print("START_PATH:", start_path1)
# print("START_PATH_VALUE:", Calculate(start_path1))
# print("CURRENT_OPTIMAL_PATH:", optimal_path)
# print("CURRENT_OPTIMAL_PATH_VALUE:", Calculate(optimal_path))
if Calculate(optimal_path) == 99999999999:
    print("NO SOLUTION")
else:
    print(Calculate(optimal_path))