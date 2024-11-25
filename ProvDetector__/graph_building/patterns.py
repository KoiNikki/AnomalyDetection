import re


class Patterns:
    def __init__(self):
        self.CBDS = re.compile(
            r"(?P<evt_num>\d+)\s+"  # 捕获事件编号
            r"(?P<evt_time>\d{2}:\d{2}:\d{2}\.\d+)\s+"  # 捕获事件时间
            r"(?P<evt_cpu>\d+)\s+"  # 捕获 CPU 编号
            r"(?P<proc_name>\S+)\s+"  # 捕获进程名称
            r"\((?P<thread_tid>\d+)\)\s+"  # 捕获线程 ID
            r"(?P<evt_dir>[<>])\s+"  # 捕获事件方向（如 > 或 <）
            r"(?P<evt_type>\S+)"  # 捕获事件类型（如 close、write 等）
            r"(?:\s+(?P<evt_args>.+))?"  # 可选捕获事件参数
        )
        self.LIDDS = re.compile(
            r"(?P<evt_num>\d+)\s+"  # 捕获事件编号
            r"(?P<evt_time>\d{2}:\d{2}:\d{2}\.\d+)\s+"  # 捕获事件时间
            r"(?P<evt_cpu>\d+)\s+"  # 捕获 CPU 编号
            r"\d+\s+"
            r"(?P<proc_name>\S+)\s+"  # 捕获进程名称
            r"(?P<thread_tid>\d+)\s+"  # 捕获线程 ID
            r"(?P<evt_dir>[<>])\s+"  # 捕获事件方向（如 > 或 <）
            r"(?P<evt_type>\S+)"  # 捕获事件类型（如 close、write 等）
            r"(?:\s+(?P<evt_args>.+))?"  # 可选捕获事件参数
        )


if __name__ == "__main__":
    log_entry = (
        "38723 00:11:30.370311880 1 999 mysqld 22577 < fcntl res=0(<f>/dev/null)"
    )

    pattern = Patterns()
    match = pattern.LIDDS.match(log_entry)

    if match:
        print(match.groupdict())
    else:
        print("No match found.")
