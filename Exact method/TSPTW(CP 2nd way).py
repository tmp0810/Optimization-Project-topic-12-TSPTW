from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp

# Hàm tạo dữ liệu đầu vào
def create_data_model():
    N = int(input())  # Nhập số lượng nút (địa điểm)
    data = {}
    data["time_windows"] = [(0,0),]  # Khởi tạo khoảng thời gian (time windows)
    d_list=[0,]  # Danh sách thời gian xử lý tại mỗi nút
    for _ in range(N):
        e, l, d = map(int, input().split())  # Nhập thời gian bắt đầu, kết thúc, và thời gian xử lý
        data["time_windows"].append((e, l))  # Thêm khoảng thời gian vào danh sách
        d_list.append(d)  # Thêm thời gian xử lý vào danh sách
    data["time_matrix"] = []  # Khởi tạo ma trận thời gian
    for i in range(N+1):
        line = list(map(int, input().split()))  # Nhập thời gian di chuyển giữa các nút
        new_line = []
        for j in range(N+1):
            if j == i:
                new_line.append(0)  # Nếu là chính nút đó, thời gian là 0
            else:
                new_line.append(line[j] + d_list[i])  # Thêm thời gian xử lý tại nút
        data["time_matrix"].append(new_line)  # Thêm dòng vào ma trận thời gian
    data["num_vehicles"] = 1  # Số lượng phương tiện
    data["depot"] = 0  # Nút bắt đầu (depot)
    return N, data

# Hàm in kết quả
def print_solution(N, data, manager, routing, solution):
    print(N)  # In số lượng nút
    for vehicle_id in range(data["num_vehicles"]):
        index = routing.Start(vehicle_id)  # Lấy điểm bắt đầu
        plan_output = ""  # Chuỗi lưu lộ trình
        while not routing.IsEnd(index):  # Lặp đến khi kết thúc lộ trình
            if index != 0:
                plan_output += (
                    f"{manager.IndexToNode(index)} "  # Thêm nút vào chuỗi kết quả
                )
            index = solution.Value(routing.NextVar(index))  # Chuyển đến nút tiếp theo
        print(plan_output)  # In lộ trình

# Hàm chính
def main():
    N, data = create_data_model()  # Tạo dữ liệu đầu vào

    # Tạo đối tượng quản lý chỉ số
    manager = pywrapcp.RoutingIndexManager(
        N+1, data["num_vehicles"], data["depot"]
    )

    # Tạo mô hình định tuyến
    routing = pywrapcp.RoutingModel(manager)

    # Hàm callback tính thời gian di chuyển giữa các nút
    def time_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)  # Lấy nút xuất phát
        to_node = manager.IndexToNode(to_index)  # Lấy nút đích
        return data["time_matrix"][from_node][to_node]  # Trả về thời gian di chuyển

    transit_callback_index = routing.RegisterTransitCallback(time_callback)  # Đăng ký callback
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)  # Đặt chi phí cạnh

    time = "Time"  # Tên cho chiều thời gian
    routing.AddDimension(
        transit_callback_index,
        999999,  # Cho phép thời gian chờ
        999999999999,  # Giới hạn thời gian tối đa
        False,  # Không bắt buộc thời gian khởi đầu phải bằng 0
        time,
    )
    time_dimension = routing.GetDimensionOrDie(time)  # Lấy đối tượng chiều thời gian

    # Thêm ràng buộc khoảng thời gian cho từng địa điểm (trừ depot)
    for location_idx, time_window in enumerate(data["time_windows"]):
        if location_idx == data["depot"]:
            continue
        index = manager.NodeToIndex(location_idx)  # Lấy chỉ số nút
        time_dimension.CumulVar(index).SetRange(time_window[0], time_window[1])  # Đặt khoảng thời gian

    # Thêm ràng buộc khoảng thời gian cho nút xuất phát của phương tiện
    depot_idx = data["depot"]  # Chỉ số depot
    for vehicle_id in range(data["num_vehicles"]):
        index = routing.Start(vehicle_id)  # Chỉ số nút bắt đầu
        time_dimension.CumulVar(index).SetRange(
            data["time_windows"][depot_idx][0], data["time_windows"][depot_idx][1]
        )

    # Khởi tạo thời gian bắt đầu và kết thúc hợp lệ cho các tuyến đường
    for i in range(data["num_vehicles"]):
        routing.AddVariableMinimizedByFinalizer(
            time_dimension.CumulVar(routing.Start(i))
        )
        routing.AddVariableMinimizedByFinalizer(time_dimension.CumulVar(routing.End(i)))

    # Đặt chiến lược tìm giải pháp ban đầu
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC  # Chiến lược chọn cạnh rẻ nhất
    )

    # Giải bài toán
    solution = routing.SolveWithParameters(search_parameters)

    # In kết quả lên màn hình
    if solution:
        print_solution(N, data, manager, routing, solution)


# Điểm bắt đầu chương trình
if __name__ == "__main__":
    main()
