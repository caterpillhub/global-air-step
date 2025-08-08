import pandas as pd
import os

# Node for doubly linked list
class BaggageNode:
    def __init__(self, bag_id, last_checkpoint, metadata):
        self.bag_id = bag_id
        self.last_checkpoint = last_checkpoint
        self.metadata = metadata
        self.prev = None
        self.next = None

# Lost Baggage Tracker
class LostBaggageTracker:
    def __init__(self):
        self.head = None
        self.tail = None
        self.lookup = {}  # Hash table: Bag ID -> Node

    def insert_baggage(self, bag_id, last_checkpoint, metadata):
        """Insert a baggage into linked list & hash table"""
        if bag_id in self.lookup:
            print(f"Bag {bag_id} already exists. Updating checkpoint.")
            self.update_checkpoint(bag_id, last_checkpoint)
            return
        node = BaggageNode(bag_id, last_checkpoint, metadata)
        if not self.head:
            self.head = self.tail = node
        else:
            self.tail.next = node
            node.prev = self.tail
            self.tail = node
        self.lookup[bag_id] = node

    def update_checkpoint(self, bag_id, new_checkpoint):
        """Update last checkpoint for a given baggage"""
        node = self.lookup.get(bag_id)
        if node:
            node.last_checkpoint = new_checkpoint
        else:
            print(f"Bag {bag_id} not found.")

    def remove_baggage(self, bag_id):
        """Remove baggage from linked list & hash table"""
        node = self.lookup.pop(bag_id, None)
        if not node:
            print(f"Bag {bag_id} not found.")
            return False
        if node.prev:
            node.prev.next = node.next
        else:
            self.head = node.next
        if node.next:
            node.next.prev = node.prev
        else:
            self.tail = node.prev
        return True

    def get_baggage_info(self, bag_id):
        """O(1) lookup for baggage info"""
        node = self.lookup.get(bag_id)
        if node:
            return {
                "bag_id": node.bag_id,
                "last_checkpoint": node.last_checkpoint,
                "metadata": node.metadata
            }
        return None

    def traverse_order(self):
        """Return baggage flow order as a list"""
        current = self.head
        order = []
        while current:
            order.append({
                "bag_id": current.bag_id,
                "checkpoint": current.last_checkpoint,
                "metadata": current.metadata
            })
            current = current.next
        return order

# Load baggage from CSV
def load_baggage_csv(path):
    tracker = LostBaggageTracker()
    if not os.path.exists(path):
        print(f"File {path} not found. Starting with empty tracker.")
        return tracker
    df = pd.read_csv(path)
    for _, row in df.iterrows():
        tracker.insert_baggage(
            bag_id=row["BagID"],
            last_checkpoint=row["LastCheckpoint"],
            metadata={"owner": row["Owner"], "flight": row["Flight"]}
        )
    return tracker

# Save baggage to CSV
def save_baggage_csv(tracker, path):
    flow = tracker.traverse_order()
    rows = []
    for item in flow:
        rows.append({
            "BagID": item["bag_id"],
            "LastCheckpoint": item["checkpoint"],
            "Owner": item["metadata"]["owner"],
            "Flight": item["metadata"]["flight"]
        })
    pd.DataFrame(rows).to_csv(path, index=False)
    print(f"Data saved to {path}")

# Simple CLI menu
def run_cli(tracker, path):
    while True:
        print("\n--- Lost Baggage Tracker ---")
        print("1. View baggage flow")
        print("2. Search baggage")
        print("3. Add baggage")
        print("4. Update checkpoint")
        print("5. Remove baggage")
        print("6. Save & Exit")
        choice = input("Choose option: ")

        if choice == "1":
            for bag in tracker.traverse_order():
                print(bag)
        elif choice == "2":
            bag_id = input("Enter Bag ID: ").upper()
            info = tracker.get_baggage_info(bag_id)
            print(info if info else "Bag not found.")
        elif choice == "3":
            bag_id = input("Bag ID: ").upper()
            checkpoint = input("Last checkpoint: ")
            owner = input("Owner name: ")
            flight = input("Flight number: ")
            tracker.insert_baggage(bag_id, checkpoint, {"owner": owner, "flight": flight})
        elif choice == "4":
            bag_id = input("Bag ID: ").upper()
            checkpoint = input("New checkpoint: ")
            tracker.update_checkpoint(bag_id, checkpoint)
        elif choice == "5":
            bag_id = input("Bag ID: ").upper()
            tracker.remove_baggage(bag_id)
        elif choice == "6":
            save_baggage_csv(tracker, path)
            break
        else:
            print("Invalid choice.")

# === Run Program ===
if __name__ == "__main__":
    csv_path = "data/raw/lost_baggage.csv"  # Change if needed
    tracker = load_baggage_csv(csv_path)
    run_cli(tracker, csv_path)
