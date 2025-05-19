import re
import sys

def parse_and_simplify_log(line, seq_num):
    # 样本详细日志格式关键字段抓取思路：
    # 时间戳#进程#pid#父pid#1#<操作符><操作>#连接#线程id#程序路径#<NA>#服务名#...# 参数
    
    parts = line.strip().split('#')
    if len(parts) < 13:
        return None

    # 时间戳
    timestamp = parts[0].split()[1]  # 只取 时间部分 12:12:57.837995388
    # 精度不变，保留完整时间字符串（如12:12:57.837995388）
    # 进程名
    procname = parts[1]
    # pid
    pid = parts[2]
    # 操作段
    operation_full = parts[5]  # 格式如 >#read 之类，但这里#是分隔符，真实内容是 ">" + "accept4"
    # operation_full 会有类似 >#accept4, 先合并第5和第6字段
    # 修正: operation可能被分成了两个字段，5和6，要合并
    op_index = 5
    operation = parts[op_index]
    # 之前分隔用#导致操作实际是两个字符串，形如 '>' 和 'accept4'
    # 需要拼接判断
    if parts[op_index] in ('>', '<'):
        if len(parts) > op_index+1:
            operation = parts[op_index] + ' ' + parts[op_index+1]
            # 删除后一项避免重复
            # 注意后续解析要调整offset，但这里暂时跳过
    else:
        operation = parts[op_index]

    # 连接部分（ip端口等）
    connection = parts[op_index+2] if len(parts) > op_index+2 else '<NA>'

    # 线程号（tid），程序路径, 服务名
    tid = parts[op_index+3] if len(parts) > op_index+3 else '<NA>'
    prog_path = parts[op_index+4] if len(parts) > op_index+4 else '<NA>'
    service = parts[op_index+6] if len(parts) > op_index+6 else '<NA>'

    # 参数串就是最后几个字段拼接
    params = parts[op_index+7:] if len(parts) > op_index+7 else []

    # 抽取文件描述符fd=xxx和可能的size=xxx或者res=xxx，以及连接描述
    # 拼成类似：fd=3(<...>) size=4096 res=-11(EAGAIN) 这类格式

    # 从params数组中找fd=..., size=..., res=..., data=...
    param_str = ' '.join(params)

    # 重新拼接简洁日志格式
    # seq_num 时间(只取时间部分) 0 procname(pid) 操作 参数
    # 这里“0”是固定占位符，对应你示例的固定0

    simplified_line = f"{seq_num} {timestamp} 0 {procname} ({pid}) {operation} "

    # 连接和参数包含重复信息，一起加到后面
    # 如果connection为空或<NA>不加入
    if connection != '<NA>':
        simplified_line += f"{connection} "

    if param_str:
        simplified_line += param_str

    # 去除多余空格
    return simplified_line.strip()


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python convert.py <logfile> <outfile>")
        sys.exit(1)

    logfile = sys.argv[1]
    outfile = sys.argv[2]

    with open(logfile, 'r', encoding='utf-8') as f, open(outfile, 'w', encoding='utf-8') as out_f:
        for i, log in enumerate(f, 1):
            simplified = parse_and_simplify_log(log, i)
            if simplified:
                out_f.write(simplified + '\n')