import heapq  
import networkx as nx  
import math  


class RepresentationExtraction:  
    def __init__(self):  
        pass  

    def extract(self, G: nx.DiGraph, T: int, K: int):  
        """  
        Eppstein 算法主函数，用于提取前K条最不常见路径  
        :param G: 溯源图 (nx.DiGraph)，包含节点和边的相关属性  
        :param T: 时间窗口大小  
        :param K: 返回路径数量  
        :return: 前K条最不常见路径的列表  
        """  
        # 第一步：为图中的边计算权重，并构建单源单汇流图  
        weighted_graph = self._calculate_edge_weights(G, T)  

        # 第二步：通过 Eppstein 算法获取前K条路径  
        uncommon_paths = self._eppstein_k_paths(weighted_graph, K)  

        return uncommon_paths  

    def _calculate_edge_weights(self, G: nx.DiGraph, T: int):  
        """  
        计算边的权重，将规律性分数转化为边权  
        :param G: 溯源图 (nx.DiGraph)  
        :param T: 时间窗口大小  
        :return: 添加权重后的图  
        """  
        # 初始化稳定性字典  
        out_stability = {node: 0 for node in G.nodes}  
        in_stability = {node: 0 for node in G.nodes}  

        # 统计每个节点的出边和入边在时间窗口内的分布  
        for node in G.nodes:  
            out_times = set()  
            in_times = set()  
            for _, dst, edge_data in G.out_edges(node, data=True):  
                out_times.add(int(edge_data['timestamp'] / T))  
            for src, _, edge_data in G.in_edges(node, data=True):  
                in_times.add(int(edge_data['timestamp'] / T))  
            
            # 计算稳定性  
            total_windows = max(1, len(out_times | in_times))  
            out_stability[node] = len(out_times) / total_windows  
            in_stability[node] = len(in_times) / total_windows  

        # 为每条边分配权重  
        for src, dst, edge_data in G.edges(data=True):  
            event_type = edge_data['type']  
            out_score = out_stability[src]  
            in_score = in_stability[dst]  
            # 假设 He/H 总是 1，计算 R(e)  
            regularity_score = out_score * in_score  
            weight = -math.log2(regularity_score) if regularity_score > 0 else float('inf')  
            G[src][dst]['weight'] = weight  

        return G  

    def _eppstein_k_paths(self, G: nx.DiGraph, K: int):  
        """  
        利用 Eppstein 算法找到前K条最短路径（实际上是负权下的最长路径问题）  
        :param G: 添加权重后的图 (nx.DiGraph)  
        :param K: 返回路径数量  
        :return: 前K条路径的列表  
        """  
        # 添加伪源节点和伪汇节点，转为单源单汇图  
        source = 'pseudo_source'  
        sink = 'pseudo_sink'  
        G.add_node(source)  
        G.add_node(sink)  

        for node in G.nodes:  
            if G.in_degree(node) == 0 and node != source and node != sink:  
                G.add_edge(source, node, weight=1)  
            if G.out_degree(node) == 0 and node != source and node != sink:  
                G.add_edge(node, sink, weight=1)  

        # 第一步：计算每个节点到伪汇节点的最短路径（单源最短路径）  
        dist, parent = self._single_source_shortest_path(G, sink)  

        # 第二步：构建偏差树（deviation tree）  
        deviation_tree = self._construct_deviation_tree(G, dist, parent)  

        # 第三步：使用优先级队列找前K条路径  
        paths = self._find_k_best_paths(G, source, sink, deviation_tree, K)  

        return paths  

    def _single_source_shortest_path(self, G, sink):  
        """  
        使用反向Dijkstra算法，计算所有节点到伪汇节点的最短路径  
        :param G: 图  
        :param sink: 汇点  
        :return: 最短路径距离字典，路径父节点字典  
        """  
        dist = {node: float('inf') for node in G.nodes}  
        dist[sink] = 0  
        parent = {node: None for node in G.nodes}  

        queue = [(0, sink)]  # (距离, 节点)  
        visited = set()  

        while queue:  
            curr_dist, curr_node = heapq.heappop(queue)  

            if curr_node in visited:  
                continue  
            visited.add(curr_node)  

            for pred, _, edge_data in G.in_edges(curr_node, data=True):  
                weight = edge_data['weight']  
                if curr_dist + weight < dist[pred]:  
                    dist[pred] = curr_dist + weight  
                    parent[pred] = curr_node  
                    heapq.heappush(queue, (dist[pred], pred))  

        return dist, parent  

    def _construct_deviation_tree(self, G, dist, parent):  
        """  
        根据最短路径构建偏差树，用于记录分支路径  
        :param G: 图  
        :param dist: 最短路径距离  
        :param parent: 最短路径父节点  
        :return: 偏差树  
        """  
        deviation_tree = {node: [] for node in G.nodes}  

        for node in G.nodes:  
            for _, neighbor, edge_data in G.out_edges(node, data=True):  
                if parent[node] == neighbor:  
                    # 主路径（最短路径）上的边不加入偏差树  
                    continue  
                deviation_tree[node].append((neighbor, edge_data['weight']))  

        return deviation_tree  

    def _find_k_best_paths(self, G, source, sink, deviation_tree, K):  
        """  
        使用偏差树和优先级队列找前K条路径  
        :param G: 图  
        :param source: 源点  
        :param sink: 汇点  
        :param deviation_tree: 偏差树  
        :param K: 目标路径数量  
        :return: 前K条路径  
        """  
        queue = []  
        heapq.heappush(queue, (0, [source]))  # (路径长度, 路径)  

        paths = []  

        while queue and len(paths) < K:  
            curr_len, curr_path = heapq.heappop(queue)  
            curr_node = curr_path[-1]  

            if curr_node == sink:  
                paths.append((curr_len, curr_path))  
                continue  

            # 从偏差树中扩展分支路径  
            for neighbor, weight in deviation_tree[curr_node]:  
                heapq.heappush(queue, (curr_len + weight, curr_path + [neighbor]))  

            # 将主路径的下一步加入队列  
            for _, neighbor, edge_data in G.out_edges(curr_node, data=True):  
                if neighbor not in curr_path:  # 避免环  
                    heapq.heappush(queue, (curr_len + edge_data['weight'], curr_path + [neighbor]))  

        # 格式化路径为字符串形式  
        formatted_paths = []  
        for _, path in paths:  
            formatted_paths.append(" -> ".join(path))  

        return formatted_paths