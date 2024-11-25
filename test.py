import re


def parse_log(log: str):  
    # 正则表达式用于提取信息  
    pattern = r'(?P<srcId>\d+) (?P<timestamp>\d{2}:\d{2}:\d{2}\.\d+) (?P<srcType>\d+) (?P<dstType>\w+) \((?P<dstId>\d+)\) (?P<edgeType>[<>]) (?P<action>.+)'  
    
    # 使用正则表达式匹配日志字符串  
    match = re.match(pattern, log)  
    
    if match:  
        srcId = int(match.group('srcId'))  
        timestamp = match.group('timestamp')  
        srcType = match.group('srcType')  
        dstId = int(match.group('dstId'))  
        dstType = match.group('dstType')  
        edgeType = match.group('action')
        
        return [srcId, srcType, dstId, dstType, edgeType, timestamp]  
    else:  
        return []
    
print(parse_log("2 20:34:50.022198413 6 apache2 (9347) < select res=0"))
print(parse_log("12 20:34:50.537101297 2 apache2 (9402) > futex addr=7FEBD8E0C164 op=129 val=1"))
print(parse_log("9 20:34:50.537090582 2 apache2 (9402) < epoll_wait res=1"))
print(parse_log("131933 00:04:22.931472052 0 cve-2014-6271-web-1 (cd3fa651c6dd) runc:[1:CHILD] (38477:1) < openat fd=3(<f>/proc/self/fd/5) dirfd=-100(AT_FDCWD) name=/proc/self/fd/5 flags=4098(O_WRONLY|O_CLOEXEC) mode=0 dev=1A"))