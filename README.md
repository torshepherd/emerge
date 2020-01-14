# emerge
Emergent Behavior Modeling

![Simulation running](emerge.gif)

As part of the course 'Bio-Inspired Design', my group designed a program to simulate the emergent behavior that arises when ants work collaboratively. The mechanism we implemented was map-sharing.

## Map Sharing
As agents navigate a 2d grid, they move almost randomly, trying to expand their knowledge frontier about the map. When two agents are next to one another, their maps synchronize, becoming the union of each of their previous maps.

The effect is that they can approximately delegate parts of the map for each to search, telling each other that their sector is clear when they happen to bump into each other.

## Results
This project was completed during my undergrad; I had not learned much about dynamic system modeling, ML, or even just smarter search algorithms which could have made the experiment have far better performance.

However, the resultant behavior of increasing the number of agents does show that performance increased significantly more when map-sharing was enabled than without.

## Requirements
Python 3xx
Requires numpy, pygame
