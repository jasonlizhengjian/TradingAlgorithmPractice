# region imports
from collections import deque
from AlgorithmImports import *
# endregion

class MuscularSkyBlueParrot(QCAlgorithm):

    def Initialize(self):
        self.SetStartDate(2020, 1, 1)  # Set Start Date
        self.SetEndDate(2021,1,1)
        self.SetCash(100000)  # Set Strategy Cash
        self.spy = self.AddEquity("SPY", Resolution.Daily).Symbol
        
        self.EnableAutomaticIndicatorWarmUp = True

        self.max = self.MAX(self.spy, 365, Resolution.Daily)
        self.min = self.MIN(self.spy, 365, Resolution.Daily)

        self.sma = self.SMA(self.spy, 30, Resolution.Daily)
        closing_prices = self.History(self.spy, 30, Resolution.Daily)["close"]
        #for time, price in closing_prices.loc[self.spy].items():
        #    self.sma.Update(time, price)


    def OnData(self, data: Slice):
        if not self.sma.IsReady:
            return

        low = self.min.Current.Value
        high = self.max.Current.Value
        

        price = self.Securities[self.spy].Price

        if price * 1.05 >= high and self.sma.Current.Value < price:
            if not self.Portfolio[self.spy].IsLong:
                self.SetHoldings(self.spy, 1)
        
        elif price * 0.9 <= low and self.sma.Current.Value > price:
            if not self.Portfolio[self.spy].IsShort:
                self.SetHoldings(self.spy, -1)

        else:
            self.Liquidate()

        self.Plot("Benchmark", "52w-High", high)
        self.Plot("Benchmark", "52w-Low", low)
        self.Plot("Benchmark", "SMA", self.sma.Current.Value)
        
class CustomSimpleMoving(PythonIndicator):

    def __init__(self, name, period):
        self.Name = name
        self.Time = datetime.min
        self.Value = 0
        self.queue = deque(maxlen=period)

    def Update(self, input):
        self.queue.appendleft(input.Close)
        self.Time = input.EndTime
        count = len(self.queue)
        self.Value = sum(self.queue) / count
        return (count == self.queue.maxlen)
