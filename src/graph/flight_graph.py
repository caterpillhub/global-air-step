import heapq
from collections import defaultdict
from typing import Dict, List, Tuple, Optional
import pandas as pd

# ---------- FlightEdge ----------
class FlightEdge:
    def __init__(self, dest_code: str, airline: str, weights: Dict[str, float]):
        self.dest = dest_code
        self.airline = airline
        self.weights = weights

    def __repr__(self):
        return f"FlightEdge(dest={self.dest}, airline={self.airline}, weights={self.weights})"

# ---------- FlightGraph ----------
class FlightGraph:
    def __init__(self):
        self.adj: Dict[str, List[FlightEdge]] = defaultdict(list)

    @classmethod
    def from_routes_df(cls, routes_df: pd.DataFrame):
        graph = cls()
        for _, row in routes_df.iterrows():
            src = row["Source airport"]
            dst = row["Destination airport"]
            airline = row.get("Airline", "")
            weights = {
                "distance": float(row.get("distance_km", 0.0)),
                "delay": float(row.get("delay", 0.0)),
                "cost": float(row.get("cost", 0.0))
            }
            edge = FlightEdge(dest_code=dst, airline=airline, weights=weights)
            graph.add_edge(src, edge)
        return graph

    def add_edge(self, src_code: str, edge: FlightEdge):
        self.adj[src_code].append(edge)

    def neighbors(self, code: str) -> List[FlightEdge]:
        return self.adj.get(code, [])

    def dijkstra(self, source: str, target: str, weight_key: str = "distance") -> Tuple[Optional[float], List[str]]:
        dist = {source: 0.0}
        prev = {}
        heap = [(0.0, source)]
        while heap:
            d, node = heapq.heappop(heap)
            if d > dist.get(node, float("inf")):
                continue
            if node == target:
                break
            for edge in self.neighbors(node):
                alt = d + edge.weights.get(weight_key, float("inf"))
                if alt < dist.get(edge.dest, float("inf")):
                    dist[edge.dest] = alt
                    prev[edge.dest] = node
                    heapq.heappush(heap, (alt, edge.dest))

        if target not in dist:
            return None, []

        path = []
        cur = target
        while cur != source:
            path.append(cur)
            cur = prev.get(cur)
            if cur is None:
                break
        path.append(source)
        path.reverse()
        return dist[target], path

    def bellman_ford(self, source: str, target: str, weight_key: str = "distance") -> Tuple[Optional[float], List[str], bool]:
        nodes = set(self.adj.keys())
        for edges in self.adj.values():
            for e in edges:
                nodes.add(e.dest)

        dist = {node: float("inf") for node in nodes}
        prev = {}
        dist[source] = 0.0

        for _ in range(len(nodes) - 1):
            updated = False
            for u in self.adj:
                for edge in self.adj[u]:
                    if dist[u] + edge.weights.get(weight_key, float("inf")) < dist[edge.dest]:
                        dist[edge.dest] = dist[u] + edge.weights.get(weight_key, float("inf"))
                        prev[edge.dest] = u
                        updated = True
            if not updated:
                break

        neg_cycle = False
        for u in self.adj:
            for edge in self.adj[u]:
                if dist[u] + edge.weights.get(weight_key, float("inf")) < dist[edge.dest]:
                    neg_cycle = True
                    break
            if neg_cycle:
                break

        if dist.get(target, float("inf")) == float("inf"):
            return None, [], neg_cycle

        path = []
        cur = target
        while cur != source:
            path.append(cur)
            cur = prev.get(cur)
            if cur is None:
                break
        path.append(source)
        path.reverse()
        return dist[target], path, neg_cycle

# ---------- MAIN TEST ----------
if __name__ == "__main__":
    # Load the cleaned routes.csv
    routes_df = pd.read_csv("data/new/routes.csv")
    print(f"[INFO] Loaded {len(routes_df)} routes from data/new/routes.csv")

    # Build the graph
    graph = FlightGraph.from_routes_df(routes_df)
    print(f"[INFO] Graph constructed with {len(graph.adj)} nodes.")

    # Take user input
    source = input("Enter Source Airport Code (e.g. MAA): ").strip().upper()
    target = input("Enter Destination Airport Code (e.g. JFK): ").strip().upper()
    weight = input("Enter Weight Metric (distance / cost / delay): ").strip().lower()

    # Validate source/destination
    if source not in graph.adj:
        print(f"[ERROR] Source airport code '{source}' not found in the graph.")
    elif target not in graph.adj and all(target != edge.dest for edges in graph.adj.values() for edge in edges):
        print(f"[ERROR] Destination airport code '{target}' not found in the graph.")
    else:
        print(f"\n[Dijkstra] Finding shortest path from {source} to {target} by {weight}...")
        dist, path = graph.dijkstra(source, target, weight_key=weight)
        if dist is not None:
            print(f"[Dijkstra] Distance: {dist}, Path: {path}")
        else:
            print("[Dijkstra] No path found.")

        print(f"\n[Bellman-Ford] Finding shortest path from {source} to {target} by {weight}...")
        bf_dist, bf_path, neg_cycle = graph.bellman_ford(source, target, weight_key=weight)
        if bf_dist is not None:
            print(f"[Bellman-Ford] Distance: {bf_dist}, Path: {bf_path}, Negative cycle: {neg_cycle}")
        else:
            print("[Bellman-Ford] No path found.")
