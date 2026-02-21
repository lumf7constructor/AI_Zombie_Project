# AI Zombie Project

An AI simulation project exploring pathfinding algorithms and adversarial agent interactions. 

## 🚀 Project Phases
- **Phase 1:** Survivor uses **Breadth-First Search (BFS)** to find the shortest path to supplies.
- **Phase 2:** Introduces an **Adversarial Zombie** that uses a **Greedy Heuristic (Manhattan Distance)** to hunt the survivor.

---

## 🛠️ Setup Instructions

Follow these steps to get the environment running on your local machine.

### 1. Clone the Project
```bash
git clone [https://github.com/lumf7constructor/AI_Zombie_Project.git](https://github.com/lumf7constructor/AI_Zombie_Project.git)
cd AI_Zombie_Project
```

### 2. Create and Activate Virtual Environment
- This ensures that the project dependencies don't interfere with your system settings.

MacOS/Linux
```bash
python3 -m venv venv
source venv/bin/activate
```
Windows
```bash
python -m venv venv
.\venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Simulation
```bash
# To run the Phase 1 (Search Logic)
python3 phase1_search.py
```

```bash
# To run the Phase 2 (Zombie Interaction)
python3 phase2_zombie.py
```
