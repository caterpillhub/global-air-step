import pandas as pd
import heapq
from typing import List, Dict

# ------------------ Baggage Class ------------------
class Baggage:
    def __init__(self, passenger_id, priority, bag_type, risk_level):
        self.passenger_id = passenger_id
        self.priority = int(priority)
        self.bag_type = bag_type
        self.risk_level = risk_level

    def urgency_score(self):
        risk_map = {"low": 2, "medium": 1, "high": 0}
        return self.priority * 10 + risk_map.get(self.risk_level.lower(), 2)

    def __lt__(self, other):
        return self.urgency_score() < other.urgency_score()

    def __repr__(self):
        return f"(ID:{self.passenger_id}, P:{self.priority}, T:{self.bag_type}, R:{self.risk_level})"

# ------------------ BST ------------------
class BaggageBSTNode:
    def __init__(self, baggage: Baggage):
        self.baggage = baggage
        self.left = None
        self.right = None

class BaggageBST:
    def __init__(self):
        self.root = None

    def insert(self, baggage: Baggage):
        def _insert(node, baggage):
            if not node:
                return BaggageBSTNode(baggage)
            if baggage.passenger_id < node.baggage.passenger_id:
                node.left = _insert(node.left, baggage)
            else:
                node.right = _insert(node.right, baggage)
            return node
        self.root = _insert(self.root, baggage)

    def search(self, passenger_id):
        def _search(node, pid):
            if not node:
                return None
            if pid == node.baggage.passenger_id:
                return node.baggage
            elif pid < node.baggage.passenger_id:
                return _search(node.left, pid)
            else:
                return _search(node.right, pid)
        return _search(self.root, passenger_id)

    def inorder(self):
        result = []
        def _inorder(node):
            if not node:
                return
            _inorder(node.left)
            result.append(node.baggage)
            _inorder(node.right)
        _inorder(self.root)
        return result

# ------------------ Min Heap ------------------
class BaggageMinHeap:
    def __init__(self):
        self.heap = []

    def push(self, baggage: Baggage):
        heapq.heappush(self.heap, baggage)

    def pop(self):
        return heapq.heappop(self.heap) if self.heap else None

    def all_baggage(self):
        return list(self.heap)

# ------------------ Main Flow ------------------
def load_baggage_data(csv_path: str) -> List[Baggage]:
    df = pd.read_csv(csv_path)
    bag_list = []
    for _, row in df.iterrows():
        bag = Baggage(
            passenger_id=row["PassengerID"],
            priority=row["Priority"],
            bag_type=row["BaggageType"],
            risk_level=row["RiskLevel"]
        )
        bag_list.append(bag)
    return bag_list

def run_baggage_flow(csv_path: str):
    bags = load_baggage_data(csv_path)

    # Build BST
    bst = BaggageBST()
    for bag in bags:
        bst.insert(bag)
    sorted_bags = bst.inorder()

    # Build Min Heap
    heap = BaggageMinHeap()
    for bag in bags:
        heap.push(bag)

    # Heap processing order
    heap_order = []
    while True:
        next_bag = heap.pop()
        if not next_bag:
            break
        heap_order.append(next_bag)

    # Show results
    print("\n[Sorted by Passenger ID - BST]:")
    for b in sorted_bags:
        print(b)

    print("\n[Sorted by Urgency - Min Heap]:")
    for b in heap_order:
        print(b)

    # Optional: search
    pid = input("\nEnter Passenger ID to search: ").strip().upper()
    found = bst.search(pid)
    if found:
        print(f"[FOUND] {found}")
    else:
        print("[NOT FOUND] Passenger ID not in system.")

# ------------------ Entry ------------------
if __name__ == "__main__":
    run_baggage_flow("data/raw/baggage.csv")
