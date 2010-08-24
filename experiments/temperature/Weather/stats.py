from Weather.data import rows

class DistStats:
    def __init__(self,outlier=1000):
        self.sequence = []
        for x in rows():
            d = float(x[-1])
            if d > outlier: continue
            self.sequence.append(d)
    def median(self):
        self.sequence.sort()
        return self.sequence[len(self.sequence) // 2]
    def avg(self):
        return sum(self.sequence) / len(self.sequence)
    def stdev(self):
        sd = sum([(i - self.avg()) ** 2 for i in self.sequence])
        return (sd / (len(self.sequence) - 1)) ** .5
    def min(self): return min(self.sequence)
    def max(self): return max(self.sequence)
    def __repr__(self):
        return '%.3f/%.3f/%.3f/%.3f/%.3f'% \
            (self.min(),self.median(),self.max(),self.avg(),self.stdev())

if __name__ == '__main__':
    print DistStats()