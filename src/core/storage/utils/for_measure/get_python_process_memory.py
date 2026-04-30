import os
import psutil

def get_python_process_memory():
    """
    Trả về tổng lượng RAM (MB) mà tiến trình Python hiện tại đang chiếm dụng.
    Tương đương với giá trị hiển thị trong Task Manager.
    """
    # Lấy PID của script hiện tại
    pid = os.getpid()
    process = psutil.Process(pid)
    
    # Lấy thông số Resident Set Size (RSS)
    mem_info = process.memory_info()
    memory_mb = mem_info.rss / (1024 * 1024)
    
    return memory_mb