# counters.py
class Counters:
    def __init__(self):
        self.reset()
    
    def reset(self):
        self.WORKDAY = 1
        self.SALARYDAY = 1
        self.EMPDETAIL = 1

counters = Counters()