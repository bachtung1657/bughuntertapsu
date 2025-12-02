import sys
import requests
import re
import json
from html import unescape
from colorama import Fore, Style, init

init(autoreset=True)

EVIDENCE_FILE = ""

def print_banner():
    print(Fore.RED + """
    =======================================================
    SECURITY TOOL V8 - HIDDEN DATA HUNTER (SPA INSPECTOR)
    (Soi dữ liệu JSON ẩn - Kiểm tra lỗi lộ thông tin trước khi thanh toán)
    Level: Logic Hunter | Coder: Người anh em
    =======================================================
    """)

def log_evidence(url, findings):
    with open(EVIDENCE_FILE, "a", encoding="utf-8") as f:
        f.write(f"\n[URL]: {url}\n")
        f.write("-" * 50 + "\n")
        f.write(findings + "\n")
        f.write("=" * 50 + "\n")

def scan_nuxt_data(url):
    print(Fore.CYAN + f"\n[*] Đang phân tích dữ liệu ngầm (Nuxt/State) tại: {url}")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
    }
    
    try:
        res = requests.get(url, headers=headers, timeout=10)
        html = res.text
        
        # 1. TÌM DỮ LIỆU JSON CỦA NUXT/NEXT/REACT
        # Thường nằm trong biến window.__NUXT__ hoặc <script id="__NEXT_DATA__">
        patterns = [
            r'window\.__NUXT__\s*=\s*(\{.*?\});',
            r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>',
            r'var\s+__PRELOADED_STATE__\s*=\s*(\{.*?\});'
        ]
        
        found_data = None
        for p in patterns:
            match = re.search(p, html, re.DOTALL)
            if match:
                print(Fore.GREEN + "[+] Đã tìm thấy cục dữ liệu STATE khổng lồ (Client-side Data).")
                found_data = match.group(1)
                break
        
        if not found_data:
            print(Fore.YELLOW + "[-] Không tìm thấy cục data Nuxt/Next lộ thiên. Web này giấu kỹ hoặc render server-side.")
            # Quét text thường
            found_data = html
        
        # 2. SOI CÁC TỪ KHÓA NHẠY CẢM (TK, MK, PASS, CREDENTIALS)
        print(Fore.CYAN + "[*] Đang soi kính hiển vi tìm acc/pass ẩn...")
        
        # Các từ khóa thường dùng trong JSON của shop game
        keywords = ['password', 'matkhau', 'mat_khau', 'mk', 'taikhoan', 'tai_khoan', 'username', 'credential', 'info_login']
        
        leaked_info = []
        
        # Chuyển data về string thường để tìm kiếm
        data_str = str(found_data)
        
        for kw in keywords:
            # Tìm xung quanh từ khóa 50 ký tự
            matches = re.finditer(f'"{kw}"\s*:\s*"(.*?)"', data_str, re.IGNORECASE)
            for m in matches:
                val = m.group(1)
                # Lọc bớt các giá trị rác (null, undefined, rỗng)
                if val and len(val) > 2 and "null" not in val:
                    leak = f"PHÁT HIỆN '{kw}': {val}"
                    print(Fore.RED + f"    [!] {leak}")
                    leaked_info.append(leak)

        # 3. KIỂM TRA LOGIC GIÁ TIỀN (PRICE TAMPERING CHECK)
        # Xem giá tiền có nằm tơ hơ trong HTML không
        price_matches = re.findall(r'"price"\s*:\s*([0-9]+)', data_str)
        if price_matches:
            print(Fore.YELLOW + f"[*] Tìm thấy thông tin giá trong Code: {price_matches[:3]}...")
            leaked_info.append(f"Cấu trúc giá lộ phía Client: {price_matches[:3]}")
            print(Fore.WHITE + "    -> Nguy cơ: Nếu server tin tưởng giá này gửi lên từ client, hacker có thể sửa giá thành 0đ.")

        # KẾT LUẬN
        if leaked_info:
            print(Fore.RED + "\n[KẾT LUẬN]: CÓ DẤU HIỆU LỘ DỮ LIỆU!")
            evidence = "TÌM THẤY DỮ LIỆU NHẠY CẢM TRONG SOURCE CODE (KHÔNG CẦN THANH TOÁN):\n" + "\n".join(leaked_info)
            log_evidence(url, evidence)
            print(Fore.GREEN + f"Đã ghi lại bằng chứng vào file: {EVIDENCE_FILE}")
        else:
            print(Fore.GREEN + "\n[AN TOÀN] Không tìm thấy mật khẩu/tài khoản dạng văn bản rõ (Cleartext) trong code.")
            print(Fore.WHITE + "Server này có vẻ đã ẩn thông tin đăng nhập kỹ (chỉ trả về sau khi thanh toán thành công).")
            
            # Ghi log an toàn để báo cáo trung thực
            log_evidence(url, "Web an toàn với lỗi lộ thông tin Client-side. Dữ liệu nhạy cảm được che giấu tốt.")

    except Exception as e:
        print(Fore.RED + f"Lỗi: {e}")

def main():
    global EVIDENCE_FILE
    print_banner()
    
    target = input(Fore.YELLOW + "Nhập URL chi tiết Acc (vd: https://google.com/...): ").strip()
    domain = target.split("//")[-1].split("/")[0]
    EVIDENCE_FILE = f"BANG_CHUNG_DATA_AN_{domain}.txt"
    
    # Tạo file log
    with open(EVIDENCE_FILE, "w", encoding="utf-8") as f:
        f.write("BÁO CÁO KIỂM TRA DỮ LIỆU ẨN (LOGIC DATA LEAK)\n")
        f.write("Mục đích: Kiểm chứng xem Web có gửi Acc/Pass về máy khách hàng TRƯỚC khi thanh toán không.\n")
        f.write("="*60 + "\n")
        
    scan_nuxt_data(target)

if __name__ == "__main__":
    main()