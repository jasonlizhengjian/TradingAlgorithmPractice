#region imports
from AlgorithmImports import *
#endregion
from tensorflow.keras.models import Sequential
import json

class SmoothSkyBlueMosquito(QCAlgorithm):

    def Initialize(self):
        #self.SetStartDate(2018, 1, 1)  # Set Start Date
        self.SetStartDate(2020, 1, 1)  # Set End Date
        
        # Get model
        model_key = 'spy_price_predictor'       
        if self.ObjectStore.ContainsKey(model_key):
            model_str = self.ObjectStore.Read(model_key)
            config = json.loads(model_str)['config']
            self.model = Sequential.from_config(config)

        self.SetCash(100000)  # Set Strategy Cash
        self.symbol = self.AddEquity("SPY", Resolution.Daily).Symbol
        self.SetBenchmark(self.symbol)


    def OnData(self, data):
        prediction = self.GetPrediction()
        if prediction > 0.5:
            self.SetHoldings(self.symbol, (prediction-0.5)*2)
        else:
            self.SetHoldings(self.symbol, -0.5)
    
    def GetPrediction(self):
        # instead of history requests, use rolling window for more efficiency
        df = self.History(self.symbol, 50).loc[self.symbol]
        df_change = df[["close", "open", "high", "low", "volume"]].pct_change().dropna()
        model_input = []
        # turn history into right input format for model
        for index, row in df_change.tail(30).iterrows():
            model_input.append(np.array(row))
        model_input = np.array([model_input])
        return self.model.predict(model_input)[0][0]
