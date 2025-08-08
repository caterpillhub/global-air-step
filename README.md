# ✈️ Global Air Hackathon Project

## 🧩 Project Modules

### 1. **Data Cleaning & Graph-based Shortest Path Finder**
- **Objective:** Clean messy flight data and enable quickest/cheapest routing between airports.
- **How It Works:**
  - Loads and cleans `airports.dat` and `routes.dat`.
  - Constructs a directed weighted graph using Python data structures.
  - Implements **Dijkstra’s** and **Bellman-Ford** algorithms for shortest path finding.
  - CLI prompts users for:
    - Source airport code
    - Destination airport code
    - Weight metric (**distance**, **cost**, or **delay**)
  - Input validation ensures only valid airport codes.
  - Outputs best route and complete path metrics.

***

### 2. **Baggage Flow System (BST + Min Heap)**
- **Objective:** Ensure priority-based and secure baggage handling.
- **How It Works:**
  - Utilizes a **Binary Search Tree (BST)** to filter baggage by passenger priority, type, and risk.
  - Employs a **Min Heap** for instantly sorting by urgency.
  - Loads from a synthetic `baggage.csv` for realistic simulation.
  - Demo CLI: Add, search, classify, and sort baggage—ideal for front-line staff and security.

***

### 3. **Lost Baggage Tracker (Doubly Linked List + Hash Table)**
- **Objective:** Find and manage lost baggage instantly.
- **How It Works:**
  - Uses a **Doubly Linked List** to track baggage checkpoints and maintain the order of lost reports.
  - Implements a **Hash Table** for O(1) lookup by Bag ID.
  - CLI allows viewing, adding, updating, and deleting lost baggage entries.
  - Data is loaded from `lost_baggage_synthetic.csv` and saved upon changes for full persistence.

***

## 🗂️ Datasets

- **Source Datasets:**
  - `airports.dat` & `routes.dat` (OpenFlights)
- **Synthetic Datasets:**
  - `baggage.csv` (Generated for baggage flow module)
  - `lost_baggage_synthetic.csv` (Generated for lost baggage tracker)

> Ensure these files are placed as follows:
```
/data/raw/airports.dat
/data/raw/routes.dat
/data/new/airports_cleaned.csv
/data/new/routes_cleaned.csv
/data/baggage.csv
/data/lost_baggage_synthetic.csv
```

***

## 💾 Installation & Quick Start

### **Requirements**
- Python 3.x
- Libraries: `pandas`, `heapq`, `collections`, `math`, `json`, `os`

### **Setup**
```bash
git clone https://github.com/your-github/global-air-hackathon.git
cd global-air-hackathon
pip install -r requirements.txt
```
> *(Ensure the datasets are in the correct folders as above.)*

### **Module Execution**

#### 1. Flight Path Finder
```bash
python flight_graph.py
```
*Follow the prompts to pick airports and path metrics!*

#### 2. Baggage Flow System
```bash
python baggage_flow.py
```
*Sort and prioritize baggage from the command line!*

#### 3. Lost Baggage Tracker
```bash
python lost_baggage_tracker.py
```
*Add/view/update lost baggage instantly!*

***

## 🎮 Example Usage

### **Shortest Path Finder**
```
Enter source airport code: JFK
Enter destination airport code: DXB
Select metric (distance/cost/delay): distance

Shortest path from JFK to DXB:
JFK → LHR → DXB
Total distance: 6,854 miles
```

### **Baggage Flow System**
```
[1] Add new baggage
[2] View all baggage sorted by urgency
Select option: 2

[Baggage List...sorted by min-heap priority]
```

### **Lost Baggage Tracker**
```
[1] Search bag by ID
[2] Update bag status
[3] Remove lost bag entry
[4] List all lost bags
Select option: 1
Enter Bag ID: BAG1029

[Output: Bag details, last known checkpoint, etc.]
```

***

## 🎯 Why This Project Stands Out

- **Modern Data Structures:** Graphs, BSTs, Min Heaps, Doubly Linked Lists & Hash Tables—each chosen for their real-world performance in airline operations.
- **Synthetic & Real Data Flexibility:** Easily plug in new data or use our ready-made samples.
- **Production-Ready CLI:** No GUI required. Fast, scriptable, and perfect for rapid ops.
- **Easy Extension:** Modular design—add new airline modules as you wish!

***
