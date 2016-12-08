"""
Implements a weighted list whereby a 'take' from the list will be based on the probability
of the item. Each item will have a weight associated at insertion time, and the total weight
will be used to choose from
"""
import random


class RackUrgency:
    HIGH = 100
    MID = 50
    LOW = 10


class Rack:
    
    def __init__(self):
        self.items = []
        self.total_weight = 0

    def add(self, item, weight):
        self.items.append((weight, item))
        self.total_weight += weight

    def __len__(self):
        return len(self.items)

    def __iter__(self):
        return iter(self.items)

    def clear(self):
        del self.items[:]
        self.total_weight = 0

    def take(self):
        """
        Probabilistially grab a value
        """
        if not self.total_weight:
            return Nil

        ticket = random.randint(1, self.total_weight)
        ticket_sum = 0
        for i in range(len(self.items)):
            node = self.items[i]
            ticket_sum += node[0]
            if ticket_sum >= ticket:
                self.items.pop(i)
                self.total_weight -= node[0]
                return node[1]








