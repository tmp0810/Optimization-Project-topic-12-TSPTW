import time

# Nhập số lượng điểm (không tính điểm xuất phát)
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
    print(path)
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
