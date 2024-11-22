from ortools.linear_solver import pywraplp
from timeit import default_timer

BIG_M = 9999999

def solve(problem_inputs):
    n, e, l, d, t = problem_inputs
    e = [None] + e
    l = [None] + l
    d = [0] + d
    solver = pywraplp.Solver.CreateSolver("SAT")
    solver.SetTimeLimit(180 * 1000)
    if not solver:
        return

    TSP_path = []
    start_solving = default_timer()

    # Tạo các biến
    x = []
    for i in range(n + 1):
        temp = []
        for j in range(n + 1):
            if j == i or (i >= 1 and j >= 1 and e[i] > l[j]):
                temp.append(solver.IntVar(0, 0, f"x_{i}_{j}"))
            else:
                temp.append(solver.IntVar(0, 1, f"x_{i}_{j}"))
        x.append(temp)

    times_passed = [solver.IntVar(0, 0, f"times_passed_0")]
    for i in range(1, n + 1):
        times_passed.append(solver.IntVar(e[i], l[i], f"times_passed_{i}"))

    # Thêm các ràng buộc
    for i in range(n + 1):
        constra = solver.Constraint(1, 1, f"ct_row_{i}")
        for j in range(n + 1):
            constra.SetCoefficient(x[i][j], 1)

    for j in range(n + 1):
        constra = solver.Constraint(1, 1, f"ct_col_{j}")
        for i in range(n + 1):
            constra.SetCoefficient(x[i][j], 1)

    for i in range(n + 1):
        for j in range(1, n + 1):
            if j != i and not (i >= 1 and e[i] > l[j]):
                constra1 = solver.Constraint(
                    -solver.infinity(), BIG_M - d[i] - t[i][j], f"ct_{i}_{j}_2"
                )
                constra1.SetCoefficient(x[i][j], BIG_M)
                constra1.SetCoefficient(times_passed[j], -1)
                constra1.SetCoefficient(times_passed[i], 1)

    # Thiết lập mục tiêu của solver
    objective = solver.Objective()
    for i in range(n + 1):
        for j in range(n + 1):
            if j != 0:
                objective.SetCoefficient(x[i][j], t[i][j])
    objective.SetMinimization()

    # Giải bài toán
    status = solver.Solve()
    if status == pywraplp.Solver.OPTIMAL or status == pywraplp.Solver.FEASIBLE:
        i = 0
        print(n)  # In số lượng khách hàng
        while True:
            for j in range(n + 1):
                if x[i][j].solution_value() == 1:
                    if j != 0:
                        print(j, end=" ")  # In thứ tự các điểm ghé thăm
                        TSP_path.append(j)
                    i = j
                    break
            if i == 0:
                print()
                break
    else:
        print("Không tìm thấy giải pháp hợp lệ trong giới hạn thời gian.")

    end_solving = default_timer()
    return TSP_path

if __name__ == "__main__":
    # Đọc input từ đề bài
    n = int(input())
    e, l, d = [], [], []
    for _ in range(n):
        ei, li, di = map(int, input().split())
        e.append(ei)
        l.append(li)
        d.append(di)
    
    t = []
    for _ in range(n + 1):
        t.append(list(map(int, input().split())))
    
    TSP_path = solve((n, e, l, d, t))
    if len(TSP_path) == 0:
        print("Không tìm thấy giải pháp khả thi.")
