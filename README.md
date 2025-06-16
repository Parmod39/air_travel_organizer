# Air Travel Organizer ✈️

A Python‑based flight management and route planning application with interactive web UI and customizable suggestion strategies. Build, visualize, and explore flight networks by cost, number of stops, or cheapest routing.


## 🌟 Features

- **Manage Airports**  
  - Add automatically‑generated or custom airport codes & names  
  - Delete airports (cascade‑removes related flights)

- **Manage Flights**  
  - Add/delete flights with departure/arrival times, economy & business fares  
  - Random default suggestions to speed up testing

- **Flight Suggestions**  
  - **Find Cheapest Route** (Dijkstra’s algorithm)  
  - **Find All Routes by Max Cost** (depth‑first search)  
  - **Find All Routes by Max Stops** (breadth‑first search)  
  - Visualize individual suggestions on interactive graphs

- **Full Flight Map**  
  - See your entire network of airports & flights in a single Graphviz diagram  
  - Nodes colored per suggestion or default light blue  
  - Edges display economy & business fares, automatically blend colors for overlapping routes

- **Web UI** powered by [PyWebIO](https://github.com/pywebio/PyWebIO)  
- **Graph Visualization** with [Graphviz](https://graphviz.org)

---


## ⚙️ Prerequisites

- **Python 3.8+**  
- **Graphviz** installed & added to your system PATH  
  - Windows: download from https://graphviz.org/download/  
  - macOS: `brew install graphviz`  
  - Linux: `sudo apt install graphviz`  

---

## 🚀 Installation & Setup

1. **Clone the repository**  
   ```bash
   git clone https://github.com/Parmod39/air_travel_organizer.git
   cd air_travel_organizer

2.(Optional) Create a virtual environment
   ```bash
   python -m venv venv
   source venv/bin/activate    # macOS/Linux
   venv\Scripts\activate       # Windows

3.Install Python dependencies
  ```bash
  pip install pywebio graphviz

4.Verify Graphviz
  ```bash
  dot -V
You should see the Graphviz version info. If not, ensure the Graphviz bin folder is in your PATH.

---

## Usage

Run the application:

  ```bash
  python main.py

Then open your browser to:
  http://localhost:8080

---

## Project Structure

air_travel_organizer/
│
├── organizer/                  
│   ├── __init__.py             
│   └── airtravel_organizer.py   # Core Manager class & UI handlers
│
├── strategies/                 
│   ├── __init__.py             
│   ├── cheapest_strategy.py     # Dijkstra’s algorithm
│   ├── cost_strategy.py         # DFS under max cost
│   ├── stops_strategy.py        # BFS under max stops
│   └── suggestion_strategy.py   # Abstract base class
│
├── venv/                        # (Optional) virtual environment
│
├── main.py                      # Entry‑point: starts PyWebIO server
├── README.md                    # You are here!
└── requirements.txt             # (Optional) freeze of installed packages

---

## How It Works

AirTravelOrganizer maintains:

1.A set of airport codes

2.A dict of flights keyed by origin airport

3.Counters for auto‑generating unique airport & flight IDs

4.A palette of colors for rendering highlighted routes


Strategies implement the suggest(manager, …) interface:

1.CheapestStrategy uses a priority queue (Dijkstra’s) to find minimum‑cost path.

2.CostStrategy does a depth‑first search to collect all paths under a given cost.

3.StopsStrategy does a breadth‑first search to collect all paths up to a max number of stops.


Visualization:

1.Builds a Graphviz Digraph

2.Colors nodes/edges based on highlighted paths or default styling

3.Renders the graph to PNG and embeds it in the web page


Web UI (PyWebIO):

1.Presents forms and buttons to the user

2.Uses use_scope to update result & graph areas dynamically

3.Clear separation of UI handlers (welcome, manage_airports, etc.)

---

🙋‍♂️ Author
Parmod Budhiraja
https://github.com/Parmod39/air_travel_organizer

---

## 🌐 Live Project

Access the live **Air Travel Organizer** app here:  
🔗 https://parmod231.pythonanywhere.com/
	
