from typing import Dict
from ...models.domain import Flight, TripPackage
from dataclasses import dataclass

@dataclass
class ScoreWeights:
    price: float = 0.35
    flight: float = 0.40
    hotel: float = 0.20
    destination: float = 0.05

class TripScorer:
    def __init__(self, weights: ScoreWeights = ScoreWeights()):
        self.weights = weights

    # Rest of the implementation...
