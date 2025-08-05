import argparse
import pandas as pd
from src.graph.flight_graph import FlightGraph

def main():
    parser = argparse.ArgumentParser(description="Query shortest path in flight graph")
    parser.add_argument("--from", dest="src", required=True, help="Source airport code (primary_code)")
    parser.add_argument("--to", dest="dst", required=True, help="Destination airport code")
    parser.add_argument("--weight", dest="weight", default="distance", choices=["distance", "cost", "delay"], help="Edge weight to optimize")
    args = parser.parse_args()

    routes_df = pd.read_csv("data/cleaned/routes.csv")
    graph = FlightGraph.from_routes_df(routes_df)
    if args.weight == "delay":
        # example: if negative delays are modeled you might use Bellman-Ford; else Dijkstra
        dist, path = graph.dijkstra(args.src, args.dst, weight_key=args.weight)
        print(f"[Dijkstra] {args.src} -> {args.dst} by {args.weight}: distance={dist}, path={path}")
    else:
        dist, path = graph.dijkstra(args.src, args.dst, weight_key=args.weight)
        print(f"{args.src} -> {args.dst} by {args.weight}: cost={dist}, path={path}")

if __name__ == "__main__":
    main()
