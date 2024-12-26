import sys

def read_input_from_file(filename):
    '''
    This function reads an input file for the TSPTW problem using manual input-like structure.
    It parses the input file and returns the following:
        + n: The number of points (excluding the starting point)
        + e: List of earliest start times for each point
        + l: List of latest end times for each point
        + d: List of service times for each point
        + t: Travel time matrix (size (n+1) x (n+1))
    '''
    try:
        with open(filename, 'r') as file_handle:
            # Read all lines from the file and strip whitespace
            content = [line.strip() for line in file_handle.readlines() if line.strip()]

            # Ensure there is at least one line for the number of points
            if not content:
                raise ValueError("Input file is empty or not formatted correctly.")

            # Read the number of points (n)
            n = int(content[0])

            # Initialize lists for e, l, and d with a placeholder for the starting point
            e = [-1]  # Earliest start times
            l = [-1]  # Latest end times
            d = [-1]  # Service times

            # Parse the e, l, d values
            for i in range(1, n + 1):
                ei, li, di = map(int, content[i].split())
                e.append(ei)
                l.append(li)
                d.append(di)

            # Parse the travel time matrix (n+1 x n+1)
            t = []
            for i in range(n + 1):
                t_row = list(map(int, content[n + 1 + i].split()))
                if len(t_row) != n + 1:
                    raise ValueError("Travel time matrix row size mismatch.")
                t.append(t_row)

            return n, e, l, d, t

    except FileNotFoundError:
        print(f"Error: The file '{filename}' was not found.")
        return None
    except ValueError as ve:
        print(f"Value Error: {ve}")
        return None
    except Exception as ex:
        print(f"An unknown error occurred: {ex}")
        return None

if len(sys.argv) > 1:
    n,e,l,d,t = read_input_from_file(sys.argv[1])
else:
    n = int(input())

    # Khởi tạo danh sách e, l, d để lưu các giá trị thời gian
    e = [-1]  # Thời gian bắt đầu sớm nhất tại mỗi điểm
    l = [-1]  # Thời gian kết thúc muộn nhất tại mỗi điểm
    d = [-1]  # Thời gian phục vụ tại mỗi điểm

    # Nhập các thông số e, l, d từ người dùng
    for i in range(n):
        _ = list(map(int, input().split()))
        e.append(_[0])
        l.append(_[1])
        d.append(_[2])

    # Nhập ma trận thời gian di chuyển t
    t = []
    for i in range(n + 1):
        _ = list(map(int, input().split()))
        t.append(_)

# Biến lưu kết quả tốt nhất
Min = 99999999999  # Giá trị thời gian di chuyển tối thiểu ban đầu (cực đại)
check = [False for i in range(n + 1)]  # Đánh dấu các điểm đã đi qua
path = [0 for i in range(n + 1)]  # Lưu đường đi hiện tại
ans_path = None  # Đường đi tốt nhất

# Hàm tính toán chi phí đường đi
def Calculate(path):
    global Min, ans_path
    check_valid = True  # Kiểm tra đường đi hợp lệ
    cur_pos = 0  # Vị trí hiện tại (bắt đầu từ điểm 0)
    total_time = 0  # Tổng thời gian hiện tại
    travel_time = 0  # Tổng thời gian di chuyển

    for i in range(0, n):
        # Tính thời gian di chuyển từ điểm hiện tại đến điểm kế tiếp
        total_time += t[cur_pos][path[i]]
        travel_time += t[cur_pos][path[i]]

        # Kiểm tra xem có đến đúng thời gian cho phép không
        if total_time <= l[path[i]]:
            total_time = max(total_time, e[path[i]])  # Đợi đến thời gian bắt đầu nếu cần
            total_time += d[path[i]]  # Thêm thời gian phục vụ
            cur_pos = path[i]  # Di chuyển đến điểm tiếp theo
        else:
            check_valid = False  # Đường đi không hợp lệ
            break

    # Tính thời gian quay lại điểm xuất phát
    travel_time += t[path[n - 1]][0]

    # Nếu tìm thấy một đường đi hợp lệ tốt hơn, cập nhật kết quả
    # print(path)
    if travel_time < Min and check_valid == True:
        ans_path = path
        Min = travel_time
        print("FOUND A SOLUTION: ", path)

# Hàm thử tất cả các hoán vị đường đi
def Try(k):
    for i in range(1, n + 1):
        # Nếu điểm i chưa được đi qua
        if check[i] == False:
            path[k] = i  # Đưa điểm i vào vị trí k trong đường đi
            check[i] = True  # Đánh dấu điểm i đã được chọn

            # Nếu đã đủ n điểm, tính toán chi phí
            if k == n:
                Calculate(path[1:])
            else:
                # Tiếp tục thử các điểm còn lại
                Try(k + 1)

            # Backtrack: Đánh dấu lại điểm i chưa được đi qua
            check[i] = False

# Bắt đầu thử từ vị trí đầu tiên
Try(1)

# In kết quả
print(n)
for i in range(0, n):
    print(ans_path[i], end=' ')
