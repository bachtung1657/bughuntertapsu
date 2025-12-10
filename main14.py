import sys
import requests
import threading
import time
from urllib.parse import urlparse, urljoin
from colorama import Fore, Style, init

init(autoreset=True)

# CẤU HÌNH
TARGET_URL = ""
FOUND_VULNS = []

def print_banner():
    print(Fore.RED + """
    =======================================================
    SECURITY TOOL V14 - THE API FUZZER (IDOR HUNTER)
    (Dò tìm API ẩn & Kiểm tra lỗi truy cập chéo IDOR)
    Level: API BREAKER | Coder: Người anh em
    =======================================================
    """)

# 1. KỸ THUẬT FUZZING CÁC ĐƯỜNG DẪN NHẠY CẢM
def fuzz_endpoints(base_url):
    print(Fore.CYAN + "\n[*] Đang dò tìm các đường dẫn 'Cửa hậu' (Hidden Endpoints)...")
    
    # Danh sách các đường dẫn Admin/Dev hay quên xóa
    # Đây là "Wordlist" tinh gọn cho Shop bán hàng
    paths = [
        "/admin", "/administrator", "/quan-tri", "/login", "/dashboard",
        "/api/users", "/api/orders", "/api/v1/config",
        "/debug", "/console", "/_profiler", "/metrics", "/health", "/info",
        "/phpinfo.php", "/.env", "/config.json", "/backup.sql", "/database.sql",
        "/log", "/logs", "/error_log"
    ]
    
    headers = {'User-Agent': 'Security-Audit-V14'}
    
    for path in paths:
        url = urljoin(base_url, path)
        try:
            res = requests.get(url, headers=headers, timeout=5)
            
            # Phân tích phản hồi
            if res.status_code == 200:
                print(Fore.GREEN + f"[!!!] TÌM THẤY CỬA HỞ (200 OK): {url}")
                print(Fore.GREEN + f"      -> Title/Content: {res.text[:50]}...")
                FOUND_VULNS.append(f"Hidden Endpoint: {url}")
            elif res.status_code == 403:
                print(Fore.YELLOW + f"[!] Tìm thấy (nhưng bị cấm 403): {url} (Chứng tỏ đường dẫn này TỒN TẠI)")
            elif res.status_code == 401:
                print(Fore.YELLOW + f"[!] Tìm thấy (Cần đăng nhập 401): {url}")
            # 404 là không tìm thấy -> Bỏ qua
            
        except:
            pass

# 2. KỸ THUẬT IDOR (THAY ĐỔI ID ĐỂ XEM DỮ LIỆU NGƯỜI KHÁC)
def check_idor(url):
    print(Fore.CYAN + "\n[*] Đang kiểm tra lỗi IDOR (Truy cập dữ liệu chéo)...")
    
    # Phân tích URL để tìm số ID
    # VD: ...?w=2017293.aBk1oGUD
    import re
    # Tìm chuỗi số dài > 4 ký tự
    matches = re.findall(r'(\d{5,})', url)
    
    if not matches:
        print(Fore.WHITE + "[-] Không tìm thấy ID dạng số trong URL để test IDOR.")
        return

    original_id = matches[0]
    print(Fore.YELLOW + f"[*] Phát hiện ID mục tiêu: {original_id}")
    
    # Thử thay đổi ID: Tăng 1 và Giảm 1
    # Nếu server trả về 200 OK và nội dung khác rỗng -> LỖI IDOR
    test_ids = [str(int(original_id) + 1), str(int(original_id) - 1)]
    
    for test_id in test_ids:
        # Thay thế ID cũ bằng ID mới trong URL
        attack_url = url.replace(original_id, test_id)
        
        # Thử 2 trường hợp: 
        # 1. Giữ nguyên phần đuôi hash (nếu server code ngu, chỉ check ID)
        print(f"    -> Thử truy cập ID {test_id} (Giữ nguyên Token)...")
        try:
            res = requests.get(attack_url, timeout=5)
            if res.status_code == 200 and "không tồn tại" not in res.text.lower():
                print(Fore.GREEN + f"[!!!] PHÁT HIỆN IDOR TIỀM NĂNG!")
                print(Fore.GREEN + f"      URL: {attack_url}")
                print(Fore.GREEN + f"      Server trả về 200 OK. Có thể đã xem được đơn hàng của người khác!")
                FOUND_VULNS.append(f"Potential IDOR: {attack_url}")
            else:
                print(Fore.WHITE + f"       -> Thất bại (Code {res.status_code} hoặc Acc không tồn tại).")
                
        except:
            pass

        # 2. Thử bỏ luôn phần đuôi hash (nếu server code cực ngu)
        # VD: ?w=2017293.hash -> ?w=2017294
        clean_url = attack_url.split('.')[0] # Cắt bỏ phần sau dấu chấm
        if clean_url != attack_url:
            print(f"    -> Thử truy cập ID {test_id} (Bỏ qua Token)...")
            try:
                res = requests.get(clean_url, timeout=5)
                if res.status_code == 200:
                    print(Fore.GREEN + f"[!!!] PHÁT HIỆN IDOR (KHÔNG CẦN TOKEN)!")
                    print(Fore.GREEN + f"      URL: {clean_url}")
                    FOUND_VULNS.append(f"Critical IDOR (No Token): {clean_url}")
            except:
                pass

def save_report():
    if FOUND_VULNS:
        filename = f"LOI_BAO_MAT_API_{int(time.time())}.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write("BÁO CÁO LỖ HỔNG API & IDOR\n")
            f.write("==========================\n")
            for v in FOUND_VULNS:
                f.write(v + "\n")
        print(Fore.GREEN + f"\n[DONE] Đã xuất file báo cáo: {filename}")
        print(Fore.GREEN + "Gửi cái này cho họ. Nếu dính IDOR, họ sẽ lộ thông tin khách hàng khác.")
    else:
        print(Fore.YELLOW + "\n[KẾT LUẬN]: Hệ thống phân quyền khá tốt hoặc API được giấu kỹ.")

def main():
    global TARGET_URL
    print_banner()
    TARGET_URL = input(Fore.YELLOW + "Nhập URL chi tiết (vd: ...?w=2017293...): ").strip()
    
    parsed = urlparse(TARGET_URL)
    base_url = f"{parsed.scheme}://{parsed.netloc}"
    
    # 1. Chạy Fuzzing Endpoints
    fuzz_endpoints(base_url)
    
    # 2. Chạy IDOR Check
    check_idor(TARGET_URL)
    
    save_report()

if __name__ == "__main__":
    main()