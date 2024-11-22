from ortools.sat.python import cp_model

# Lớp dùng để in các giải pháp tạm thời
class Printer(cp_model.CpSolverSolutionCallback):
    def __init__(self, variables):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self._vars = variables
        self._count = 0

    def on_solution_callback(self):
        # Tăng số lượng giải pháp tìm được
        self._count += 1
        # In giá trị của các biến trong giải pháp hiện tại
        for var in self._vars:
            print(f'{var} = {self.Value(var)} |', end=' ')
        print()

    def count(self):
        # Trả về số lượng giải pháp đã tìm được
        return self._count

# Hàm đọc dữ liệu từ file đầu vào
def load_file(file='TSPTW_test_1.txt'):
    try:
        with open(file, 'r') as f:
            # Đọc và tách dữ liệu từ file
            lines = f.read().strip().split('\n')
            n = int(lines[0])  # Số lượng điểm
            start, end, service = [0] * n, [0] * n, [0] * n
            matrix = []
            # Đọc các thông số thời gian
            for i in range(n):
                start[i], end[i], service[i] = map(int, lines[i + 1].split())
            # Thêm các điểm xuất phát và kết thúc
            service = [0] + service + [0]
            start = [0] + start + [0]
            end = [0] + end + [999999]
            # Đọc ma trận thời gian di chuyển
            for i in range(n + 1):
                matrix.append(list(map(int, lines[i + n + 1].split())) + [0])
            matrix.append([0] * (n + 2))
            return n, start, end, service, matrix
    except FileNotFoundError:
        # Trả về None nếu không tìm thấy file
        return None
    except:
        # Xử lý lỗi không xác định
        return None

# Hàm nhập dữ liệu trực tiếp từ bàn phím
def input_data():
    num = int(input())  # Nhập số lượng điểm
    s, e, d = [], [], []
    for _ in range(num):
        # Nhập các thông số thời gian
        a, b, c = map(int, input().split())
        s.append(a)
        e.append(b)
        d.append(c)
    # Thêm các điểm xuất phát và kết thúc
    d = [0] + d + [0]
    s = [0] + s + [0]
    e = [0] + e + [999999999]
    # Nhập ma trận thời gian di chuyển
    t = []
    for _ in range(num + 1):
        t.append(list(map(int, input().split())) + [0])
    t.append([0] * (num + 2))
    return num, s, e, d, t

# Hàm giải quyết bài toán TSPTW
def solve_problem(n, s, e, d, t):
    mdl = cp_model.CpModel()  # Tạo model
    arcs = []  # Tập các cung có thể đi
    for i in range(n + 2):
        for j in range(n + 2):
            # Chỉ thêm các cung hợp lệ
            if j != 0 and i != (n + 1) and i != j:
                arcs.append((i, j))
    # Biến quyết định cho các cung
    route = [[mdl.NewIntVar(0, 1, f"route[{i},{j}]") for i in range(0, n + 2)] for j in range(0, n + 2)]
    # Biến thời gian đến từng điểm
    time = [mdl.NewIntVar(0, 999999, f"time[{i}]") for i in range(0, n + 2)]
    # Ràng buộc thời gian đến điểm đầu tiên
    mdl.Add(time[0] == 0)
    # Ràng buộc chỉ được rời mỗi điểm một lần
    for i in range(1, n + 1):
        mdl.Add(sum([route[i][j] for j in [edge[1] for edge in arcs if edge[0] == i]]) == 1)
    # Ràng buộc chỉ được đến mỗi điểm một lần
    for i in range(1, n + 1):
        mdl.Add(sum([route[j][i] for j in [edge[0] for edge in arcs if edge[1] == i]]) == 1)
    # Ràng buộc cung xuất phát và kết thúc
    mdl.Add(sum([route[0][j] for j in range(1, n + 1)]) == 1)
    mdl.Add(sum([route[j][n + 1] for j in range(1, n + 1)]) == 1)
    # Ràng buộc thời gian di chuyển và thời gian phục vụ
    for i, j in arcs:
        b = mdl.NewBoolVar('bool')  # Biến bool kiểm tra cung được chọn
        mx = mdl.NewIntVar(0, 999999, 'max')  # Giá trị thời gian tối đa
        mdl.AddMaxEquality(mx, [time[i], s[i]])
        mdl.Add(route[i][j] == 1).OnlyEnforceIf(b)
        mdl.Add(route[i][j] != 1).OnlyEnforceIf(b.Not())
        mdl.Add(time[j] == mx + d[i] + t[i][j]).OnlyEnforceIf(b)
    # Ràng buộc thời gian đến phải nằm trong cửa sổ thời gian
    for i in range(1, n + 1):
        mdl.Add(time[i] <= e[i])
    # Hàm mục tiêu: tối thiểu hóa tổng thời gian di chuyển
    mdl.Minimize(sum([route[i][j] * t[i][j] for i in range(n + 2) for j in range(n + 2)]))
    slv = cp_model.CpSolver()  # Bộ giải
    slv.parameters.max_time_in_seconds = 180  # Giới hạn thời gian giải
    status = slv.Solve(mdl)  # Giải bài toán
    run_time = slv.WallTime()  # Thời gian chạy
    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        sequence = []  # Lưu lại đường đi
        current = 0
        while len(sequence) < n:
            for next_point in range(n + 1):
                if slv.Value(route[current][next_point]) == 1:
                    sequence.append(next_point)
                    current = next_point
                    break
        return sequence, slv.ObjectiveValue(), run_time
    else:
        return 'None', 'None', 'None'

# Nhập dữ liệu và giải bài toán
num, start, end, service, matrix = input_data()
result_path, cost, exec_time = solve_problem(num, start, end, service, matrix)
print(num)  # In số lượng điểm
print(*result_path)  # In đường đi
