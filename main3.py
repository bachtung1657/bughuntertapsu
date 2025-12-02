import sys
import socket
import requests
import ssl
import re
import threading
import time
from urllib.parse import urlparse
from colorama import Fore, Style, init

init(autoreset=True)

# --- CẤU HÌNH ---
TIMEOUT = 3
TARGET_URL = ""
TARGET_DOMAIN = ""
TARGET_IP = ""

def print_banner():
    print(Fore.GREEN + """
    =======================================================
    SECURITY TOOL V3 - PRO RECONNAISSANCE (10 KỸ NĂNG)
    Level: Intermediate | Coder: Người anh em thiện lành
    =======================================================
    """)

# HÀM HỖ TRỢ
def get_target():
    global TARGET_URL, TARGET_DOMAIN, TARGET_IP
    url = input(Fore.YELLOW + "Nhập mục tiêu (vd: dantri.com.vn): ").strip()
    if not url.startswith("http"):
        TARGET_URL = "https://" + url
    else:
        TARGET_URL = url
    
    parsed = urlparse(TARGET_URL)
    TARGET_DOMAIN = parsed.netloc
    try:
        TARGET_IP = socket.gethostbyname(TARGET_DOMAIN)
        print(Fore.CYAN + f"[*] Mục tiêu: {TARGET_DOMAIN} ({TARGET_IP})")
    except:
        print(Fore.RED + "Lỗi: Không tìm thấy IP của tên miền này.")
        return False
    return True

# --- 10 KỸ NĂNG TRINH SÁT ---

# 1. FAST PORT SCAN (Quét cổng đa luồng)
def skill_1_fast_port_scan():
    print(Fore.CYAN + "\n[1] FAST PORT SCANNER (Đa luồng)...")
    ports = [21, 22, 23, 25, 53, 80, 110, 443, 445, 1433, 3306, 3389, 8080, 8443]
    
    def scan(port):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        if s.connect_ex((TARGET_IP, port)) == 0:
            print(Fore.GREEN + f"   [+] Cổng {port} ĐANG MỞ!")
        s.close()

    threads = []
    for port in ports:
        t = threading.Thread(target=scan, args=(port,))
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join() # Chờ tất cả chạy xong

# 2. SSL CERTIFICATE INSPECTOR (Kiểm tra chứng chỉ bảo mật)
def skill_2_ssl_check():
    print(Fore.CYAN + "\n[2] SSL CERTIFICATE INSPECTOR...")
    try:
        ctx = ssl.create_default_context()
        with ctx.wrap_socket(socket.socket(), server_hostname=TARGET_DOMAIN) as s:
            s.settimeout(TIMEOUT)
            s.connect((TARGET_DOMAIN, 443))
            cert = s.getpeercert()
            
            print(f"   - Cấp cho: {Fore.WHITE}{cert['subject'][0][0][1]}")
            print(f"   - Cấp bởi: {Fore.WHITE}{cert['issuer'][1][0][1]}")
            print(f"   - Hết hạn: {Fore.YELLOW}{cert['notAfter']}")
            print(Fore.GREEN + "   [OK] Web có HTTPS hợp lệ.")
    except Exception as e:
        print(Fore.RED + f"   [!] Lỗi SSL hoặc Web không có HTTPS: {e}")

# 3. HTTP OPTIONS (Kiểm tra các phương thức được phép)
def skill_3_http_methods():
    print(Fore.CYAN + "\n[3] CHECK HTTP METHODS...")
    try:
        res = requests.options(TARGET_URL, timeout=TIMEOUT)
        methods = res.headers.get('Allow', 'Không tìm thấy')
        print(f"   Các lệnh được phép: {Fore.WHITE}{methods}")
        if 'TRACE' in methods or 'TRACK' in methods:
            print(Fore.RED + "   [CẢNH BÁO] Phương thức TRACE được bật (Nguy cơ Cross-Site Tracing).")
    except:
        print(Fore.RED + "   Không kiểm tra được.")

# 4. ROBOTS.TXT READER (Đọc bản đồ cấm)
def skill_4_robots_txt():
    print(Fore.CYAN + "\n[4] ROBOTS.TXT ANALYZER...")
    url = f"{TARGET_URL}/robots.txt"
    try:
        res = requests.get(url, timeout=TIMEOUT)
        if res.status_code == 200:
            print(Fore.GREEN + "   [+] Tìm thấy robots.txt!")
            # Tìm các dòng Disallow (Cấm)
            for line in res.text.splitlines():
                if "Disallow" in line:
                    print(f"   {Fore.YELLOW}{line.strip()}")
        else:
            print(Fore.WHITE + "   [-] Không có file robots.txt")
    except:
        pass

# 5. CMS DETECTOR (Đoán nền tảng web)
def skill_5_cms_detect():
    print(Fore.CYAN + "\n[5] CMS DETECTOR (Wordpress/Joomla?)...")
    try:
        res = requests.get(TARGET_URL, timeout=TIMEOUT)
        content = res.text.lower()
        if "wp-content" in content:
            print(Fore.GREEN + "   [+] Phát hiện: WORDPRESS")
        elif "joomla" in content:
            print(Fore.GREEN + "   [+] Phát hiện: JOOMLA")
        elif "shopify" in content:
            print(Fore.GREEN + "   [+] Phát hiện: SHOPIFY")
        else:
            print(Fore.WHITE + "   [-] Chưa nhận diện được CMS phổ biến.")
    except:
        pass

# 6. EMAIL SCRAPER (Tìm Email ẩn trong trang chủ)
def skill_6_email_scraper():
    print(Fore.CYAN + "\n[6] EMAIL HARVESTER (Quét Email)...")
    try:
        res = requests.get(TARGET_URL, timeout=TIMEOUT)
        # Regex tìm email
        emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', res.text)
        unique_emails = set(emails)
        if unique_emails:
            for email in unique_emails:
                print(Fore.GREEN + f"   [+] Tìm thấy: {email}")
        else:
            print(Fore.WHITE + "   [-] Không thấy email nào trên trang chủ.")
    except:
        pass

# 7. LINK EXTRACTOR (Lấy toàn bộ link)
def skill_7_link_extractor():
    print(Fore.CYAN + "\n[7] LINK EXTRACTOR (Tìm liên kết)...")
    try:
        res = requests.get(TARGET_URL, timeout=TIMEOUT)
        links = re.findall(r'href=[\'"]?([^\'" >]+)', res.text)
        count = 0
        for link in links:
            if link.startswith("http") and count < 5: # Chỉ in 5 link demo
                print(f"   -> {link}")
                count += 1
        print(Fore.WHITE + f"   (Tổng cộng tìm thấy {len(links)} liên kết)")
    except:
        pass

# 8. WAF DETECTOR (Phát hiện tường lửa)
def skill_8_waf_detect():
    print(Fore.CYAN + "\n[8] WAF DETECTOR (Tường lửa Web)...")
    try:
        res = requests.get(TARGET_URL, timeout=TIMEOUT)
        headers = str(res.headers).lower()
        if "cloudflare" in headers:
            print(Fore.MAGENTA + "   [!] Phát hiện: CLOUDFLARE")
        elif "aws" in headers or "cloudfront" in headers:
            print(Fore.MAGENTA + "   [!] Phát hiện: AMAZON AWS WAF")
        elif "akamai" in headers:
            print(Fore.MAGENTA + "   [!] Phát hiện: AKAMAI")
        else:
            print(Fore.WHITE + "   [-] Không phát hiện WAF danh tiếng.")
    except:
        pass

# 9. COOKIE SECURITY (Kiểm tra bảo mật Cookie)
def skill_9_cookie_audit():
    print(Fore.CYAN + "\n[9] COOKIE SECURITY AUDIT...")
    try:
        res = requests.get(TARGET_URL, timeout=TIMEOUT)
        cookies = res.cookies
        if not cookies:
            print("   [-] Web không set cookie.")
        for cookie in cookies:
            print(f"   Cookie: {cookie.name}")
            if cookie.secure:
                print(Fore.GREEN + "     [Secure]: OK (Chỉ truyền qua HTTPS)")
            else:
                print(Fore.RED + "     [Secure]: MISSING (Có thể bị bắt gói tin)")
            
            if cookie.has_nonstandard_attr('HttpOnly') or cookie.get_nonstandard_attr('HttpOnly'):
                # Note: Python requests xử lý HttpOnly hơi khác tùy version
                print(Fore.GREEN + "     [HttpOnly]: OK (JavaScript không đọc được)")
            else:
                print(Fore.YELLOW + "     [HttpOnly]: Check thủ công (Tool chưa xác định rõ)")
    except:
        pass

# 10. ADMIN PANEL FINDER (Dò trang quản trị cơ bản)
def skill_10_admin_finder():
    print(Fore.CYAN + "\n[10] ADMIN PANEL FINDER (Thử vận may)...")
    admin_paths = ['admin', 'login', 'wp-admin', 'dashboard', 'panel', 'user']
    
    for path in admin_paths:
        check_url = f"{TARGET_URL}/{path}"
        try:
            res = requests.get(check_url, timeout=2)
            if res.status_code == 200:
                print(Fore.GREEN + f"   [+] CÓ KHẢ NĂNG: {check_url} (Code 200)")
            elif res.status_code == 403:
                print(Fore.YELLOW + f"   [!] BỊ CẤM (403): {check_url} (Có tồn tại nhưng bị chặn)")
        except:
            pass

# MAIN RUNNER
def main():
    while True:
        print_banner()
        if get_target():
            print(Fore.YELLOW + "\n[*] BẮT ĐẦU QUÉT TOÀN DIỆN (CHỜ KHOẢNG 10-20s)...")
            
            skill_1_fast_port_scan()
            skill_2_ssl_check()
            skill_3_http_methods()
            skill_4_robots_txt()
            skill_5_cms_detect()
            skill_6_email_scraper()
            skill_7_link_extractor()
            skill_8_waf_detect()
            skill_9_cookie_audit()
            skill_10_admin_finder()
            
            print(Fore.GREEN + "\n================ HOÀN THÀNH ================")
        
        choice = input("\nNhấn Enter để quét trang khác, hoặc '0' để thoát: ")
        if choice == '0': break

if __name__ == "__main__":
    main()