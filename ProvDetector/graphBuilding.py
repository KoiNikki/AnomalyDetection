import datetime
import re
import numpy as np
from Graph import *

pattern_CBDS = re.compile(
    r"(?P<evt_num>\d+)\s+"  # 捕获事件编号
    r"(?P<evt_time>\d{2}:\d{2}:\d{2}\.\d+)\s+"  # 捕获事件时间
    r"(?P<evt_cpu>\d+)\s+"  # 捕获 CPU 编号
    r"(?P<proc_name>\S+)\s+"  # 捕获进程名称
    r"\((?P<thread_tid>\d+)\)\s+"  # 捕获线程 ID
    r"(?P<evt_dir>[<>])\s+"  # 捕获事件方向（如 > 或 <）
    r"(?P<evt_type>\S+)"  # 捕获事件类型（如 close、write 等）
    r"(?:\s+(?P<evt_args>.+))?"  # 可选捕获事件参数
)

pattern_LIDDS = re.compile(
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


def parse_log(log: str):

    # Flexible regex to capture key fields
    match = pattern_CBDS.search(log)
    if not match:
        match = pattern_LIDDS.search(log)
        if not match:
            return None

    # Extract components from the log line
    evt_time = match.group("evt_time")
    # proc_name = match.group("proc_name")
    thread_tid = match.group("thread_tid")
    # evt_dir = match.group("evt_dir")
    evt_type = match.group("evt_type")
    evt_args = match.group("evt_args")

    if not evt_args:
        return None

    # Debugging: Print the parsed groups
    # print(
    #     f"time: {time}, process_name: {process_name}, pid: {pid}, direction: {direction}, operation: {operation}, details: {details}"
    # )

    # Initialize nodes and edge
    src_id = None
    src_type = None
    dst_id = None
    dst_type = None
    edge_type = None
    timestamp = None

    if evt_type in {"read", "readv", "write", "writev"}:
        fd_match = re.search(r"fd=(\d+)", evt_args)
        if fd_match:
            fd = fd_match.group(1)
            socket_match = re.search(r"<.*?>([\S]+)->([\S]+)", evt_args)
            if socket_match:
                # src_ip_port = socket_match.group(1)
                # dst_ip_port = socket_match.group(2)
                src_id = thread_tid
                src_type = "Process"
                dst_id = fd
                dst_type = "Socket"
                edge_type = "Read" if evt_type in {"read", "readv"} else "Write"
                timestamp = evt_time
            else:
                file_path_match = re.search(r"<f>([\S]+)", evt_args)
                if file_path_match:
                    file_path = file_path_match.group(1)
                    src_id = thread_tid
                    src_type = "Process"
                    dst_id = file_path
                    dst_type = "File"
                    edge_type = "Read" if evt_type in {"read", "readv"} else "Write"
                    timestamp = evt_time
    elif evt_type == "execve":
        file_path_match = re.search(r"filename=(\S+)", evt_args)
        if file_path_match:
            file_path = file_path_match.group(1)
            src_id = thread_tid
            src_type = "Process"
            dst_id = file_path
            dst_type = "File"
            edge_type = "Execute"
            timestamp = evt_time
    elif evt_type == "clone":
        # first one
        child_pid_match = re.search(r"res=(\d+)", evt_args)
        if child_pid_match and thread_tid:
            child_pid = child_pid_match.group(1)
            src_id = thread_tid
            src_type = "Process"
            dst_id = child_pid
            dst_type = "Process"
            edge_type = "Execute"
            timestamp = evt_time

    # Return the parsed components
    if src_id and src_type and dst_id and dst_type and edge_type and timestamp:
        return [src_id, src_type, dst_id, dst_type, edge_type, timestamp]
    return None


def convert_timestamp(timestamp: str) -> int:
    # 拆分时间字符串
    time_part, nano_part = timestamp.split(".")
    hours, minutes, seconds = map(int, time_part.split(":"))

    nanoseconds = int(nano_part.ljust(9, "0"))

    # 计算总纳秒数
    total_nanoseconds = (hours * 3600 + minutes * 60 + seconds) * 10**9 + nanoseconds

    return total_nanoseconds


def graphBuilding(path_list):
    G = []
    for i in path_list:
        f_now = open(i, "r", encoding="utf-8")
        G_now = Graph()
        cnt = 0
        line_now = []
        ts_now = []
        for line in f_now:
            parsed_line = parse_log(line)
            if parsed_line:
                parsed_line[5] = convert_timestamp(parsed_line[5])
                line_now.append(parsed_line)
                ts_now.append(parsed_line[5])
        sorted_index = np.argsort(ts_now, axis=0)
        line_now = np.array(line_now)[sorted_index]

        for line in line_now:  # srcId srcType dstId dstType edgeType timestamp
            # line = line.strip('\n').split('\t')
            temp = float(line[5])
            if G_now.min_ts < 0:
                G_now.min_ts = temp
            if G_now.max_ts < 0:
                G_now.max_ts = temp
            if temp < G_now.min_ts:
                G_now.min_ts = temp
            if temp > G_now.max_ts:
                G_now.max_ts = temp

            if not line[0] in G_now.nodeId_map.keys():
                G_now.nodeId_map[line[0]] = G_now.node_cnt
                G_now.nodeName_map[G_now.node_cnt] = line[0]
                G_now.out_edges[G_now.node_cnt] = []
                G_now.in_edges[G_now.node_cnt] = []
                G_now.flag[line[0]] = 1
                G_now.node_cnt += 1
            if not line[2] in G_now.nodeId_map.keys():
                G_now.nodeId_map[line[2]] = G_now.node_cnt
                G_now.nodeName_map[G_now.node_cnt] = line[2]
                G_now.out_edges[G_now.node_cnt] = []
                G_now.in_edges[G_now.node_cnt] = []
                G_now.flag[line[2]] = 0
                G_now.node_cnt += 1
            if G_now.flag[line[2]] == 1:
                G_now.nodeId_map[line[2]] = G_now.node_cnt
                G_now.nodeName_map[G_now.node_cnt] = line[2]
                G_now.out_edges[G_now.node_cnt] = []
                G_now.in_edges[G_now.node_cnt] = []
                G_now.flag[line[2]] = 0
                G_now.node_cnt += 1

            G_now.flag[line[0]] = 1  # 修改，避免环路问题

            G_now.nodeType_map[G_now.nodeId_map[line[0]]] = line[1]
            G_now.nodeType_map[G_now.nodeId_map[line[2]]] = line[3]
            G_now.out_edges[G_now.nodeId_map[line[0]]].append(G_now.edge_cnt)
            G_now.in_edges[G_now.nodeId_map[line[2]]].append(G_now.edge_cnt)
            G_now.e_src.append(G_now.nodeId_map[line[0]])
            G_now.e_dst.append(G_now.nodeId_map[line[2]])
            G_now.e_type.append(line[4])
            G_now.e_ts.append(float(line[5]))
            G_now.edge_cnt += 1

        G_now.nodeType_map[G_now.node_cnt] = "start"
        G_now.nodeId_map["Start_node"] = G_now.node_cnt
        G_now.nodeName_map[G_now.node_cnt] = "Start_node"
        G_now.out_edges[G_now.node_cnt] = []
        G_now.in_edges[G_now.node_cnt] = []
        G_now.node_cnt += 1
        G_now.nodeType_map[G_now.node_cnt] = "end"
        G_now.nodeId_map["End_node"] = G_now.node_cnt
        G_now.nodeName_map[G_now.node_cnt] = "End_node"
        G_now.out_edges[G_now.node_cnt] = []
        G_now.in_edges[G_now.node_cnt] = []
        G_now.node_cnt += 1
        for j in range(G_now.node_cnt - 2):
            if len(G_now.in_edges[j]) == 0:
                G_now.out_edges[G_now.node_cnt - 2].append(G_now.edge_cnt)
                G_now.in_edges[j].append(G_now.edge_cnt)
                G_now.e_src.append(G_now.node_cnt - 2)
                G_now.e_dst.append(j)
                G_now.e_type.append("start_edge")
                G_now.e_ts.append(max(G_now.min_ts - 100, 0))
                G_now.edge_cnt += 1

            if len(G_now.out_edges[j]) == 0:
                G_now.out_edges[j].append(G_now.edge_cnt)
                G_now.in_edges[G_now.node_cnt - 1].append(G_now.edge_cnt)
                G_now.e_src.append(j)
                G_now.e_dst.append(G_now.node_cnt - 1)
                G_now.e_type.append("end_edge")
                G_now.e_ts.append(G_now.min_ts + 100)
                G_now.edge_cnt += 1

        G.append(G_now)
    return G
