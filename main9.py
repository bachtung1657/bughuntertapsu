import sys
import requests
import threading
import time
import statistics
from colorama import Fore, Style, init

init(autoreset=True)

# CẤU HÌNH TEST (Chỉ test nhỏ để chứng minh, không DoS thật)
TEST_COUNT = 30       # Số lượng request gửi đi
CONCURRENT_THREADS = 10 # Số luồng chạy song song
TARGET_URL = ""
RESULTS = []

def print_banner():
    print(Fore.RED + """
    =======================================================
    SECURITY TOOL V9 - THE PULSE JAMMER (DOS SIMULATOR)
    (Kiểm tra khả năng chịu tải & Rate Limiting của API)
    Level: System Breaker | Coder: Người anh em
    =======================================================
    """)

def make_request(index):
    try:
        start_time = time.time()
        # Thêm tham số ngẫu nhiên để tránh Cache của Cloudflare
        # Đánh vào chức năng tìm kiếm hoặc load API thường tốn CPU xử lý nhất
        headers = {
            'User-Agent': f'Stress-Test-V9-{index}',
            'Cache-Control': 'no-cache'
        }
        # Giả lập search để server phải tính toán
        params = {'q': f'test_load_{index}', 't': time.time()} 
        
        res = requests.get(TARGET_URL, params=params, headers=headers, timeout=5)
        latency = (time.time() - start_time) * 1000 # Đổi ra ms
        
        RESULTS.append({
            'code': res.status_code,
            'latency': latency,
            'size': len(res.content)
        })
        
        # Phân loại phản hồi
        if res.status_code == 200:
            print(Fore.GREEN + f"   [Request #{index}] -> 200 OK (Time: {latency:.2f}ms) - Server vẫn nhận!")
        elif res.status_code == 429:
            print(Fore.RED + f"   [Request #{index}] -> 429 TOO MANY REQUESTS (Bị chặn - Tốt!)")
        elif res.status_code >= 500:
            print(Fore.MAGENTA + f"   [Request #{index}] -> {res.status_code} SERVER ERROR (Server bắt đầu lỗi!)")
        else:
            print(Fore.YELLOW + f"   [Request #{index}] -> {res.status_code}")

    except Exception as e:
        print(Fore.RED + f"   [Request #{index}] -> TIMEOUT/ERROR (Server có thể đã bị treo!)")
        RESULTS.append({'code': 0, 'latency': 5000, 'size': 0})

def analyze_results():
    print(Fore.YELLOW + "\n" + "="*50)
    print(Fore.YELLOW + "   PHÂN TÍCH CHIẾN THUẬT HẠ TẦNG")
    print(Fore.YELLOW + "="*50)
    
    total = len(RESULTS)
    success = len([r for r in RESULTS if r['code'] == 200])
    blocked = len([r for r in RESULTS if r['code'] == 429])
    errors = len([r for r in RESULTS if r['code'] == 0 or r['code'] >= 500])
    
    if total == 0: return

    latencies = [r['latency'] for r in RESULTS if r['code'] != 0]
    avg_latency = statistics.mean(latencies) if latencies else 0
    max_latency = max(latencies) if latencies else 0
    
    print(f"Tổng Request gửi đi: {total}")
    print(f"Server chấp nhận (200 OK): {Fore.RED if success == total else Fore.GREEN}{success}")
    print(f"Server chặn lại (Rate Limit): {Fore.GREEN if blocked > 0 else Fore.RED}{blocked}")
    print(f"Độ trễ trung bình: {avg_latency:.2f}ms")
    print(f"Độ trễ cao nhất: {max_latency:.2f}ms")
    
    print("\n" + "-"*50)
    print(Fore.CYAN + "[KẾT LUẬN CHIẾN LƯỢC]:")
    
    if blocked > 0:
        print(Fore.GREEN + "=> HỆ THỐNG AN TOÀN CAO.")
        print("Họ đã cấu hình Rate Limiting. Server biết từ chối khi bị spam.")
        print("Tư duy: Không thể tấn công DoS theo cách thông thường.")
    elif success == total:
        print(Fore.RED + "=> HỆ THỐNG YẾU KÉM VỀ CẤU HÌNH (VULNERABLE).")
        print("Lý do: Tôi đã gửi dồn dập nhưng Server vẫn ngây thơ nhận hết.")
        print(Fore.WHITE + "CHIẾN THUẬT PHÁ VỠ:")
        print("1. Nếu tôi tăng số luồng lên 10,000 (Botnet), CPU server sẽ chạm đỉnh 100%.")
        print("2. Database sẽ bị khóa (Deadlock) vì quá nhiều lệnh Search cùng lúc.")
        print("3. Kết quả: Web sẽ sập (Error 502 Bad Gateway) mà không cần hack vào code.")
    elif errors > 0:
        print(Fore.MAGENTA + "=> SERVER KHÔNG ỔN ĐỊNH.")
        print("Chỉ với bài test nhỏ mà server đã timeout hoặc lỗi 500.")
        print("Hệ thống này cực kỳ mong manh, dễ sập.")

    # Tạo file báo cáo
    with open(f"BAO_CAO_HA_TANG_{int(time.time())}.txt", "w", encoding="utf-8") as f:
        f.write("BÁO CÁO KIỂM TOÁN HẠ TẦNG (INFRASTRUCTURE AUDIT)\n")
        f.write(f"Mục tiêu: {TARGET_URL}\n")
        f.write("Kỹ thuật: HTTP Flood Simulation (Layer 7 Stress Test)\n")
        f.write("-" * 50 + "\n")
        f.write(f"Kết quả: Gửi {total} request trong thời gian cực ngắn.\n")
        f.write(f"- Chấp nhận: {success} (Nguy hiểm nếu là 100%)\n")
        f.write(f"- Đã chặn: {blocked} (Tốt)\n")
        f.write(f"- Lỗi server: {errors}\n")
        if success == total:
            f.write("\nNHẬN ĐỊNH: Server KHÔNG CÓ RATE LIMITING.\n")
            f.write("Rủi ro: Có thể bị đánh sập (DoS) dễ dàng bằng tool cơ bản.\n")
    
    print(Fore.GREEN + f"\n[DONE] Đã xuất file phân tích. Gửi cái này cho họ để chứng minh hạ tầng họ yếu.")

def main():
    global TARGET_URL
    print_banner()
    
    print("Công cụ này sẽ gửi nhiều request đồng thời để xem Server phản ứng thế nào.")
    # Khuyên dùng URL tốn tài nguyên server (VD: Tìm kiếm, Lọc sản phẩm)
    # Shop Hào Sữa thường có chức năng tìm kiếm hoặc lọc acc
    TARGET_URL = input(Fore.YELLOW + "Nhập URL (Nên dùng link Tìm kiếm/Search): ").strip()
    
    if not TARGET_URL.startswith("http"):
        print(Fore.RED + "Nhập sai URL.")
        return
        
    print(Fore.YELLOW + f"\n[*] Đang khởi động {CONCURRENT_THREADS} luồng tấn công giả lập...")
    print(Fore.YELLOW + "[*] Mục tiêu: Kiểm tra xem Server có 'thở dốc' không...")
    
    threads = []
    for i in range(TEST_COUNT):
        t = threading.Thread(target=make_request, args=(i+1,))
        threads.append(t)
        t.start()
        # Chỉnh delay cực nhỏ để tạo áp lực, nhưng không quá nhanh để thành DoS thật
        time.sleep(0.05) 
        
    for t in threads:
        t.join()
        
    analyze_results()

if __name__ == "__main__":
    main()