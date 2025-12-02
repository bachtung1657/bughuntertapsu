import sys
import socket
import requests
from colorama import Fore, Style, init

init(autoreset=True)

def print_banner():
    print(Fore.GREEN + """
    =================================================
    SECURITY TOOL V2 - RECONNAISSANCE (CÓ GIẢI THÍCH)
    Level: Newbie Hacker | Coder: Người anh em
    =================================================
    """)

def clean_url(url):
    return url.replace("http://", "").replace("https://", "").split('/')[0]

# --- HÀM MỚI: GIẢI MÃ THÔNG SỐ CHO NGƯỜI MỚI ---
def analyze_headers(headers):
    print(Fore.YELLOW + "\n--- [GÓC GIẢI MÃ: BÁC SĨ MẠNG PHÂN TÍCH] ---")
    
    # 1. Server đang dùng phần mềm gì?
    if 'Server' in headers:
        srv = headers['Server']
        print(f"{Fore.CYAN}[Server]: {Fore.WHITE}Web này chạy trên phần mềm '{srv}'.")
        if 'nginx' in srv.lower():
            print(f"   -> Giải thích: Nginx là server phổ biến nhất thế giới, tải nhanh, chịu tải tốt.")
        elif 'apache' in srv.lower():
            print(f"   -> Giải thích: Apache là server đời đầu, rất phổ biến, dễ cấu hình.")
        elif 'cloudflare' in srv.lower():
            print(f"   -> Giải thích: Web này được bảo vệ bởi Cloudflare (chống DDoS, giấu IP gốc).")

    # 2. Web có lưu dấu vết người dùng không?
    if 'Set-Cookie' in headers:
        print(f"{Fore.CYAN}[Set-Cookie]: {Fore.WHITE}Phát hiện web đang 'đánh dấu' bạn.")
        print(f"   -> Giải thích: Web gửi 1 file nhỏ (Cookie) để nhớ bạn là ai (duy trì đăng nhập, theo dõi thói quen).")

    # 3. Chống bị nhúng vào trang khác (Clickjacking)
    if 'X-Frame-Options' in headers:
        opt = headers['X-Frame-Options']
        print(f"{Fore.CYAN}[X-Frame-Options]: {Fore.WHITE}Cấu hình '{opt}'.")
        if 'DENY' in opt or 'SAMEORIGIN' in opt:
            print(f"   -> Giải thích: TỐT. Web này cấm người khác nhúng nó vào một cái khung (frame) giả mạo để lừa click.")

    # 4. Công nghệ phía sau (Lộ thông tin)
    if 'X-Powered-By' in headers:
        print(f"{Fore.CYAN}[X-Powered-By]: {Fore.WHITE}Lộ công nghệ '{headers['X-Powered-By']}'.")
        print(f"   -> Giải thích: NGUY HIỂM NHẸ. Hacker biết web code bằng ngôn ngữ gì (PHP, ASP.NET...) để tìm lỗi tương ứng.")

    # 5. Link Darkweb (Đặc biệt cho Z-Library)
    if 'Onion-Location' in headers:
        print(f"{Fore.CYAN}[Onion-Location]: {Fore.WHITE}Phát hiện đường dẫn Dark Web!")
        print(f"   -> Giải thích: Web này có phiên bản chạy trên mạng Tor (.onion) để ẩn danh tuyệt đối.")

    print(Fore.YELLOW + "------------------------------------------------\n")

# --- CÁC HÀM CŨ (ĐÃ CẬP NHẬT GỌI HÀM GIẢI MÃ) ---

def port_scan():
    target = input(Fore.YELLOW + "Nhập domain hoặc IP (vd: google.com): ")
    target_ip = clean_url(target)
    print(Fore.CYAN + f"\n[*] Đang quét các cổng phổ biến trên {target_ip}...")
    common_ports = {
        21: "FTP (Truyền file - Dễ bị hack nếu cũ)",
        22: "SSH (Điều khiển từ xa - Cần bảo mật kỹ)",
        80: "HTTP (Web thường - Không mã hóa)",
        443: "HTTPS (Web bảo mật - Có ổ khóa)",
        3306: "MySQL (Cơ sở dữ liệu - Tuyệt đối không được mở ra ngoài)"
    }
    try:
        for port in common_ports:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.5)
            result = sock.connect_ex((target_ip, port))
            if result == 0:
                print(Fore.GREEN + f"[+] Cổng {port} MỞ: {common_ports[port]}")
            else:
                print(Fore.RED + f"[-] Cổng {port} ĐÓNG")
            sock.close()
    except Exception as e:
        print(Fore.RED + f"Lỗi: {e}")

def header_inspector():
    url = input(Fore.YELLOW + "Nhập website (vd: z-library.sk): ")
    if not url.startswith("http"): url = "https://" + url # Mặc định dùng https cho chuẩn
    
    print(Fore.CYAN + f"\n[*] Đang lấy Header từ {url}...")
    try:
        response = requests.head(url, timeout=5)
        print(Fore.WHITE + "\n--- THÔNG TIN KỸ THUẬT (RAW) ---")
        for key, value in response.headers.items():
            print(f"{key}: {value}")
            
        # GỌI HÀM PHÂN TÍCH DỄ HIỂU Ở ĐÂY
        analyze_headers(response.headers)
            
    except Exception as e:
        print(Fore.RED + f"Lỗi kết nối: {e}")

def subdomain_finder():
    domain = input(Fore.YELLOW + "Nhập domain (vd: google.com): ")
    domain = clean_url(domain)
    sub_list = ["www", "mail", "admin", "test", "dev", "shop"]
    print(Fore.CYAN + f"\n[*] Đang dò tìm subdomain trên {domain}...")
    for sub in sub_list:
        url = f"{sub}.{domain}"
        try:
            ip = socket.gethostbyname(url)
            print(Fore.GREEN + f"[+] Tìm thấy: {url} (IP: {ip})")
        except:
            pass

def dns_lookup():
    target = input(Fore.YELLOW + "Nhập domain: ")
    try:
        ip = socket.gethostbyname(clean_url(target))
        print(Fore.GREEN + f"=> IP của nó là: {ip}")
        print(Fore.WHITE + "(Đây là địa chỉ nhà thật sự của website trên mạng Internet)")
    except:
        print(Fore.RED + "Không tìm thấy IP.")

def fake_user_agent():
    url = input(Fore.YELLOW + "Nhập link web: ")
    if not url.startswith("http"): url = "http://" + url
    headers = {'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1'}
    try:
        print(Fore.CYAN + "[*] Đang giả dạng iPhone 14 truy cập...")
        res = requests.get(url, headers=headers)
        print(Fore.GREEN + f"[+] Thành công! Web phản hồi code: {res.status_code}")
        print("Web đã tin bạn là iPhone và gửi dữ liệu về.")
    except:
        print(Fore.RED + "Lỗi.")

def main():
    while True:
        print_banner()
        print("1. Port Scanner (Quét cổng)")
        print("2. Header Inspector (Soi thông tin & Giải thích)")
        print("3. Subdomain Finder")
        print("4. DNS Lookup")
        print("5. Fake User-Agent")
        print("0. Thoát")
        choice = input(Fore.YELLOW + "\nNhập lựa chọn: ")
        if choice == '1': port_scan()
        elif choice == '2': header_inspector()
        elif choice == '3': subdomain_finder()
        elif choice == '4': dns_lookup()
        elif choice == '5': fake_user_agent()
        elif choice == '0': break

if __name__ == "__main__":
    main()