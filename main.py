import os
import sys
import socket
import requests
import webbrowser
import time
import subprocess
import re
from colorama import Fore, Style, init

# Khởi tạo màu sắc
init(autoreset=True)

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_banner():
    print(Fore.GREEN + """
    ===========================================
    CYBER SECURITY LEARNING TOOL - V2 (LITE)
    Coder: Người anh em thiện lành
    ===========================================
    """)

# 1. KIỂM TRA THÔNG TIN MẠNG (DÙNG LỆNH HỆ THỐNG)
def get_network_info():
    print(Fore.CYAN + "\n[*] Đang lấy thông tin mạng nội bộ...")
    
    # Cách 1: Lấy IP nội bộ đang dùng để kết nối Internet (Chính xác nhất)
    try:
        # Tạo một kết nối giả đến Google DNS để biết máy đang dùng IP nào ra ngoài
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        print(f"IP Nội bộ (Local IPv4): {Fore.GREEN}{local_ip}")
    except Exception:
        print(Fore.RED + "Không xác định được IP nội bộ.")

    print(Fore.YELLOW + "\n[*] Chi tiết Interface (MAC, IPv6, Loại mạng):")
    # Cách 2: Gọi lệnh hệ thống để xem chi tiết (Thay thế psutil)
    try:
        if os.name == 'nt': # Windows
            # Chạy lệnh ipconfig /all
            os.system("ipconfig /all") 
            print(Fore.MAGENTA + "\n[Tip] Nhìn dòng 'Physical Address' để thấy MAC Address.")
            print(Fore.MAGENTA + "[Tip] Nhìn dòng 'Description' để biết là WiFi hay Wireless.")
        else: # Linux / Termux
            # Chạy lệnh ifconfig
            os.system("ifconfig")
            print(Fore.MAGENTA + "\n[Tip] wlan0 thường là WiFi, rmnet là 4G.")
    except Exception as e:
        print(Fore.RED + f"Lỗi không gọi được lệnh hệ thống: {e}")

    input(Fore.BLUE + "\nNhấn Enter để quay lại...")

# 2. KIỂM TRA TỐC ĐỘ (PING GOOGLE)
def check_network_speed():
    print(Fore.CYAN + "\n[*] Đang kiểm tra kết nối (Ping Google)...")
    try:
        # Lệnh ping: Windows dùng -n, Termux/Linux dùng -c
        param = '-n' if os.name == 'nt' else '-c'
        command = ['ping', param, '4', 'google.com']
        
        # Chạy lệnh và in trực tiếp ra màn hình
        subprocess.run(command)
        
        # Phần Speedtest (Vẫn giữ nguyên vì rất hữu ích)
        choice = input(Fore.YELLOW + "\nBạn có muốn test tốc độ tải (Speedtest) không? (y/n): ")
        if choice.lower() == 'y':
            print(Fore.CYAN + "Đang đo tốc độ (Chờ xíu)...")
            import speedtest
            st = speedtest.Speedtest()
            st.get_best_server()
            download = st.download() / 1_000_000
            upload = st.upload() / 1_000_000
            print(f"Ping: {st.results.ping} ms")
            print(f"Download: {Fore.GREEN}{download:.2f} Mbps")
            print(f"Upload: {Fore.GREEN}{upload:.2f} Mbps")

    except Exception as e:
        print(Fore.RED + f"Lỗi: {e}")
    input(Fore.BLUE + "\nNhấn Enter để quay lại...")

# 3. MỞ Z-LIBRARY
def open_zlibrary():
    url = "https://vi.z-library.sk"
    print(Fore.CYAN + f"\n[*] Đang mở trình duyệt: {url}")
    try:
        # Trên termux lệnh này có thể cần cài thêm 'termux-open-url' package hoặc setup riêng
        # Nhưng trên Windows thì chạy tốt
        webbrowser.open(url)
        
        if not os.name == 'nt':
            print(Fore.WHITE + "Trên Termux, nếu không tự mở, hãy copy link trên dán vào Chrome.")
    except Exception as e:
        print(Fore.RED + f"Lỗi: {e}")
    input(Fore.BLUE + "\nNhấn Enter để quay lại...")

# 4. VỊ TRÍ (GEO IP)
def get_location():
    print(Fore.CYAN + "\n[*] Đang truy vết vị trí qua IP công khai...")
    try:
        response = requests.get('http://ip-api.com/json/')
        data = response.json()
        if data['status'] == 'success':
            print(f"IP Public: {Fore.GREEN}{data['query']}")
            print(f"Quốc gia: {Fore.WHITE}{data['country']}")
            print(f"Thành phố: {Fore.WHITE}{data['city']}")
            print(f"Nhà mạng: {Fore.YELLOW}{data['isp']}")
            print(f"Tọa độ: {data['lat']}, {data['lon']}")
        else:
            print(Fore.RED + "Thất bại.")
    except Exception as e:
        print(Fore.RED + f"Lỗi kết nối: {e}")
    input(Fore.BLUE + "\nNhấn Enter để quay lại...")

# MENU
def main():
    while True:
        clear_screen()
        print_banner()
        print("1. Kiểm tra thông tin mạng (IP, MAC - System Cmd)")
        print("2. Kiểm tra tốc độ mạng (Ping & Speedtest)")
        print("3. Truy cập Z-Library")
        print("4. Kiểm tra vị trí (GeoIP)")
        print("0. Thoát")
        
        choice = input(Fore.YELLOW + "\nNhập lựa chọn: ")
        
        if choice == '1': get_network_info()
        elif choice == '2': check_network_speed()
        elif choice == '3': open_zlibrary()
        elif choice == '4': get_location()
        elif choice == '0': break
        else: time.sleep(1)

if __name__ == "__main__":
    main()