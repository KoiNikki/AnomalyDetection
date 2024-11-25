import networkx as nx
import re
from patterns import Patterns


class GraphBuilding:
    def __init__(self):
        # Initialize a directed graph
        self.G = nx.DiGraph()

    def build_by_path(self, path, pattern):
        """
        Build the graph by reading the log file line by line
        """
        with open(path, "r") as file:
            for line in file:
                # Parse the line to extract relevant information
                result = self._parse_line(line, pattern)
                if result:
                    # Unpack the result
                    src_node, dst_node, edge = result
                    # Add nodes and edge to the graph
                    self.G.add_node(src_node["id"], **src_node["attrs"])
                    self.G.add_node(dst_node["id"], **dst_node["attrs"])
                    self.G.add_edge(src_node["id"], dst_node["id"], **edge)

    def _parse_line(self, line, pattern):
        """
        Parse a single log line to extract time, process name, pid, direction, operation, and details.
        This version is flexible and works with various log formats.
        """
        # Flexible regex to capture key fields
        match = pattern.search(line)
        if not match:
            return None

        # Extract components from the log line
        evt_time = match.group("evt_time")
        proc_name = match.group("proc_name")
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
        src_node = None
        dst_node = None
        edge = None

        if evt_type in {"read", "readv", "write", "writev"}:
            fd_match = re.search(r"fd=(\d+)", evt_args)
            if fd_match:
                fd = fd_match.group(1)
                socket_match = re.search(r"<.*?>([\S]+)->([\S]+)", evt_args)
                if socket_match:
                    src_ip_port = socket_match.group(1)
                    dst_ip_port = socket_match.group(2)
                    src_node = {
                        "id": f"Process:{thread_tid}",
                        "attrs": {
                            "type": "Process",
                            "Pid": thread_tid,
                            "Executable path": proc_name,
                        },
                    }
                    dst_node = {
                        "id": f"Socket:{fd}",
                        "attrs": {
                            "type": "Socket",
                            "Src IP": src_ip_port,
                            "Dst IP": dst_ip_port,
                        },
                    }
                    edge = {
                        "rel": "Read" if evt_type in {"read", "readv"} else "Write",
                        "time": evt_time,
                    }
                else:
                    file_path_match = re.search(r"<f>([\S]+)", evt_args)
                    if file_path_match:
                        file_path = file_path_match.group(1)
                        src_node = {
                            "id": f"Process:{thread_tid}",
                            "attrs": {
                                "type": "Process",
                                "Pid": thread_tid,
                                "Executable path": proc_name,
                            },
                        }
                        dst_node = {
                            "id": f"File:{file_path}",
                            "attrs": {"type": "File", "File path": file_path},
                        }
                        edge = {
                            "rel": "Read" if evt_type in {"read", "readv"} else "Write",
                            "time": evt_time,
                        }
        elif evt_type == "execve":
            file_path_match = re.search(r"filename=(\S+)", evt_args)
            if file_path_match:
                file_path = file_path_match.group(1)
                src_node = {
                    "id": f"Process:{thread_tid}",
                    "attrs": {
                        "type": "Process",
                        "Pid": thread_tid,
                        "Executable path": proc_name,
                    },
                }
                dst_node = {
                    "id": f"File:{file_path}",
                    "attrs": {"type": "File", "File path": file_path},
                }
                edge = {"rel": "Execute", "time": evt_time}
        elif evt_type == "clone":
            # first one
            child_pid_match = re.search(r"res=(\d+)", evt_args)
            if child_pid_match and thread_tid:
                child_pid = child_pid_match.group(1)
                src_node = {
                    "id": f"Process:{thread_tid}",
                    "attrs": {
                        "type": "Process",
                        "Pid": thread_tid,
                        "Executable path": proc_name,
                    },
                }
                dst_node = {
                    "id": f"Process:{child_pid}",
                    "attrs": {
                        "type": "Process",
                        "Pid": child_pid,
                        "Executable path": proc_name,
                    },
                }
                edge = {"rel": "Start", "time": evt_time}

        # Return the parsed components
        if src_node and dst_node and edge:
            return src_node, dst_node, edge
        return None

    def print_graph(self):
        """
        Print the graph in a human-readable format using NetworkX's methods.
        Lists all nodes with their attributes and all edges with their relationships and attributes.
        """
        print("=== Nodes ===")
        for node, attrs in self.G.nodes(data=True):
            print(f"Node: {node}, Attributes: {attrs}")

        print("\n=== Edges ===")
        for src, dst, attrs in self.G.edges(data=True):
            print(f"Edge: {src} -> {dst}, Attributes: {attrs}")
            
    def save_graph(self, path):
        nx.write_gexf(self.G, path)

if __name__ == "__main__":
    graph_builder = GraphBuilding()
    graph_builder.build_by_path(
        "/home/yichi/Ayane/AnomalyDetection/Data/CVE-2016-9962/1.log",
        Patterns().CBDS
    )
    graph_builder.print_graph() 
