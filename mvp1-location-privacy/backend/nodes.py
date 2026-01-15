import random
from datetime import datetime, timedelta
from typing import List, Dict

class Node:
    def __init__(self, node_id: int, name: str, contact_info: str):
        self.node_id = node_id
        self.name = name
        self.contact_info = contact_info
        self.location_history = self.generate_location_history()

    def generate_location_history(self) -> List[Dict]:
        history = []
        base_time = datetime.now() - timedelta(days=30)
        for i in range(100):
            timestamp = base_time + timedelta(hours=i * 7)
            if self.node_id == 0 and i == 50:
                # Node 1 will always be in Kansas City at this timestamp
                lat = 39.0997
                lon = -94.5786
            else:
                lat = random.uniform(25.0, 49.0)
                lon = random.uniform(-125.0, -67.0)
            history.append({
                'latitude': lat,
                'longitude': lon,
                'timestamp': timestamp.isoformat()
            })
        return history




# Outlandish, silly, and Impractical Jokers name game names
FIRST_NAMES = [
    "Rollie", "Willie", "Bingo", "Funky", "Ziggy", "Pickles", "Scooter", "Moxie", "Twinkle", "Bubbles",
    "Snickers", "Waldo", "Dizzy", "Tater", "Wiggles", "Gizmo", "Peanut", "Sparky", "Banjo", "Goober",
    "Glen", "Travis", "Tug", "Herbert", "Gordon", "Lenny", "Burt", "Hank", "Larry", "Don", "Chip", "Rick", "Sal", "Murray", "Doug", "Todd"
]
LAST_NAMES = [
    "Fingers", "Balonely", "McGillicuddy", "Von Doodle", "Wobbleton", "Snickerdoodle", "Fizzlebottom", "Bumblebee",
    "Wigglepants", "Pickleman", "Snoot", "Flapjack", "Wafflestein", "Twist", "McMuffin", "Jellybean", "Sprinkles", "Doodlehopper", "Bananarama", "Giggles",
    "Cunningham", "McGee", "McFadden", "McElroy", "McGillicuddy", "McClintock", "McMurray", "McDuff", "McNulty", "McPhee", "McCracken", "McBain", "McCloud", "McCoy", "McBride", "McCallister"
]

import random
def random_employee_name():
    return f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"

# Generate a list of simulated nodes with random names
NODES = [
    Node(node_id=i, name=random_employee_name(), contact_info=f"node{i+1}@example.com")
    for i in range(10)
]
