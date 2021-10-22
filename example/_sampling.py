"""
Tracking min/max/mean of a sampled sequence.
"""

class Sampler:
    def __init__(self) -> None:
        self.num = 0.0
        self.mean = 0.0
        self.maximum = 0.0
        self.minimum = 0.0

    def sample(self, value: float) -> None:
        if self.num == 0:
            self.maximum = value
            self.minimum = value
        else:
            self.mean *= self.num / (self.num + 1)
            self.maximum = max(self.maximum, value)
            self.minimum = min(self.minimum, value)
        self.num += 1
        self.mean += value / self.num
