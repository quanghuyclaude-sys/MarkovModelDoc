# Neural Networks for Trading Signal Generation

> Source: Roan (@RohOnChain) on X — [https://x.com/RohOnChain/status/2052043443766194272](https://x.com/RohOnChain/status/2052043443766194272)
> Published: May 6, 2026
> Back to: [[HiddenMarkovTrading]] · [[NNHMMPaper]] · [[HMM-Theory]] · [[Backtesting]]

---

## Core Insight

A neural network does not predict the future. It learns the **conditional expectation** hidden inside historical data — the mathematical relationship between observable inputs and what the market is statistically most likely to do next.

Formally, a neural network minimizes mean squared error:

```
L(θ) = (1/n) Σ (yᵢ - ŷᵢ)²
```

The function that minimizes `E[(Y - f(X))²]` is exactly `E[Y|X]` — the conditional mean. The network is computing the expectation, not the next realization. A die predictor trained on 10,000 rolls will output 3.5, not any face.

---

## Industry Context

| Firm | Application |
|---|---|
| Two Sigma | 10,000+ live signals through ML models simultaneously |
| Citadel | Deep learning across equity, options, and macro strategies |
| Renaissance Medallion Fund | 66% annual return before fees over 30 years — built entirely on statistical learning |
| Entry-level quant researcher salary | $350,000–$650,000 total compensation |

---

## Part 1 — Why Price Prediction Fails (Non-Stationarity)

The most common failure: feed 500 days of closing prices into an LSTM, ask it to predict day 501. It works in-sample. Out-of-sample it predicts a constant or recent mean.

**Root cause:** Financial price series are non-stationary. The distribution governing returns in 2008 is structurally different from 2021. The model trained on 2015–2019 learns the wrong expectation function for 2020.

**Formal definition:** `{Xₜ}` is stationary if `P(Xₜ₁, Xₜ₂, ..., Xₜₙ)` is invariant to time shifts. Price series violate this in mean, variance, autocorrelation, and tail behavior.

**Solution:** Engineer features that are stationary or near-stationary.

### Stationary Feature Set

| Feature | Formula | Why Stationary |
|---|---|---|
| Log returns | `r_t = ln(P_t / P_{t-k})` for k ∈ {1, 5, 20} | Removes trend |
| Volatility ratio | `σ_short / σ_long` | Dimensionless ratio |
| Momentum/vol | `r_t / σ_t` | Return scaled by realized risk |
| Volume z-score | `(V_t - μ_V) / σ_V` over rolling window | Normalizes regime differences |
| Spread-based signals | Bid-ask spread vs historical distribution | Normalized |
| Regime indicators | VWAP deviation, distance from rolling high/low, IV/RV ratio | Bounded range |

**Target variable:** Do not predict raw price. Predict:
- Binary direction: will next-period risk-adjusted return be positive?
- Return z-scored against recent distribution

### Stationarity Test (ADF)

```python
from statsmodels.tsa.stattools import adfuller

def check_stationarity(series, name):
    result = adfuller(series.dropna())
    print(f"{name}: ADF={result[0]:.4f}, p-value={result[1]:.4f}")
    return result[1] < 0.05  # p < 0.05 = stationary

# Any feature failing this test should be first-differenced or vol-normalized
```

---

## Part 2 — LSTM Architecture for Sequential Data

Standard feedforward networks treat every input independently — they discard the sequential structure of market data. LSTM (Long Short-Term Memory) maintains context across 50–100+ time steps.

### LSTM Gate Equations

```
Forget gate:  f_t = σ(W_f · [h_{t-1}, x_t] + b_f)
Input gate:   i_t = σ(W_i · [h_{t-1}, x_t] + b_i)
              g_t = tanh(W_g · [h_{t-1}, x_t] + b_g)
Output gate:  o_t = σ(W_o · [h_{t-1}, x_t] + b_o)
Cell update:  c_t = f_t ⊙ c_{t-1} + i_t ⊙ g_t
Hidden state: h_t = o_t ⊙ tanh(c_t)
```

The **forget gate** is critical for regime-aware trading: when the market transitions between regimes, it allows the model to release outdated patterns.

### PyTorch Implementation

```python
import torch
import torch.nn as nn

class TradingLSTM(nn.Module):
    def __init__(self, input_size, hidden_size=64, num_layers=2, dropout=0.2):
        super(TradingLSTM, self).__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        
        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            dropout=dropout,
            batch_first=True
        )
        self.dropout = nn.Dropout(dropout)
        self.fc = nn.Linear(hidden_size, 1)
        self.sigmoid = nn.Sigmoid()
    
    def forward(self, x):
        h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size)
        c0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size)
        out, _ = self.lstm(x, (h0, c0))
        out = self.dropout(out[:, -1, :])
        out = self.fc(out)
        return self.sigmoid(out)

def prepare_sequences(features, target, lookback=10):
    X, y = [], []
    for i in range(len(features) - lookback):
        X.append(features[i:i+lookback])
        y.append(target[i+lookback])
    return np.array(X), np.array(y)
```

**Lookback hyperparameter:**
- Daily strategies: 10–20 trading days
- Intraday (5-min bars): 24 periods = 2 hours of context
- Determine empirically via validation performance

---

## Part 3 — Training Without Fooling Yourself

### Three-Way Sequential Split

| Split | Purpose | Rule |
|---|---|---|
| Training set | Gradient descent runs here | Earliest time period |
| Validation set | Monitor overfitting; never train on it | Middle time period |
| Test set | Used exactly once at the end | Most recent period |

**Never randomize the split.** Randomizing allows future information to contaminate training (lookahead bias).

### Early Stopping Implementation

```python
def train_model(model, train_loader, val_loader, epochs=100, lr=0.001, patience=10):
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    criterion = nn.BCELoss()
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, patience=5, factor=0.5)
    
    best_val_loss = float('inf')
    best_weights = None
    patience_counter = 0
    
    for epoch in range(epochs):
        model.train()
        for X_batch, y_batch in train_loader:
            optimizer.zero_grad()
            predictions = model(X_batch).squeeze()
            loss = criterion(predictions, y_batch)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)  # prevents exploding gradients
            optimizer.step()
        
        model.eval()
        val_loss = sum(criterion(model(X).squeeze(), y).item() for X, y in val_loader) / len(val_loader)
        scheduler.step(val_loss)
        
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            best_weights = model.state_dict().copy()
            patience_counter = 0
        else:
            patience_counter += 1
            if patience_counter >= patience:
                print(f"Early stopping at epoch {epoch}")
                break
    
    model.load_state_dict(best_weights)
    return model
```

**Gradient clipping** (`max_norm=1.0`): LSTM gradients can explode on long sequences. Clipping to norm 1.0 prevents this without harming convergence.

### Walk-Forward Validation

The most rigorous evaluation for trading. Roll a training window forward, train, test on immediately following period, advance, repeat.

```python
def walk_forward_validation(features, target, train_size, test_size, step):
    all_predictions, all_actuals = [], []
    
    for start in range(0, len(features) - train_size - test_size, step):
        train_end = start + train_size
        test_end = train_end + test_size
        
        X_train = features[start:train_end]
        X_test  = features[train_end:test_end]
        y_test  = target[train_end:test_end]
        
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train.reshape(-1, X_train.shape[-1]))
        X_test_scaled  = scaler.transform(X_test.reshape(-1, X_test.shape[-1]))
        
        model = TradingLSTM(input_size=X_train.shape[-1])
        # train model here
        
        with torch.no_grad():
            preds = model(torch.FloatTensor(X_test_scaled))
        
        all_predictions.extend(preds.numpy())
        all_actuals.extend(y_test)
    
    return np.array(all_predictions), np.array(all_actuals)
```

**Expected performance benchmark:** 52–57% directional accuracy for a well-built model. A 54% signal with Sharpe > 1.0 applied consistently across hundreds of trades compounds into strong returns.

---

## Part 4 — Complete Implementation Pipeline

### Step 1: Feature Engineering

```python
def build_features(df):
    features = pd.DataFrame(index=df.index)
    close, volume = df['Close'], df['Volume']
    returns = close.pct_change()
    vol_5  = returns.rolling(5).std()
    vol_20 = returns.rolling(20).std()
    
    features['return_1d']      = returns
    features['return_5d']      = close.pct_change(5)
    features['return_20d']     = close.pct_change(20)
    features['vol_ratio']      = vol_5 / vol_20
    features['momentum_norm']  = returns / vol_20
    features['volume_zscore']  = (volume - volume.rolling(20).mean()) / volume.rolling(20).std()
    features['range_norm']     = ((df['High'] - df['Low']) / close) / ((df['High'] - df['Low']) / close).rolling(20).mean()
    features['sma_ratio']      = close.rolling(5).mean() / close.rolling(20).mean() - 1
    
    target = (returns.shift(-1) > 0).astype(int)  # binary next-day direction
    features = features.dropna()
    return features, target.loc[features.index]
```

### Step 2: Model Evaluation Metrics

```python
def evaluate_trading_signal(predictions, actuals, returns):
    pred_direction   = (predictions > 0.5).astype(int)
    accuracy         = accuracy_score(actuals, pred_direction)
    auc              = roc_auc_score(actuals, predictions)
    signal           = np.where(pred_direction == 1, 1, -1)
    strategy_returns = signal * returns
    sharpe           = strategy_returns.mean() / strategy_returns.std() * np.sqrt(252)
    cumulative       = (1 + strategy_returns).cumprod()
    max_drawdown     = ((cumulative - cumulative.cummax()) / cumulative.cummax()).min()
    
    print(f"Directional Accuracy: {accuracy:.4f}")
    print(f"AUC-ROC: {auc:.4f}")
    print(f"Annualized Sharpe: {sharpe:.4f}")
    print(f"Maximum Drawdown: {max_drawdown:.4f}")
```

### Step 3: Position Sizing (Kelly Fraction)

```
f* = (p × b - q) / b
```

Where:
- `p` = directional accuracy
- `q` = 1 - p
- `b` = average win-to-loss ratio

**Rules:**
- Use **half Kelly** to account for parameter estimation error
- Never risk more than **2% of capital** on a single signal regardless of Kelly output
- This aligns with the 2% risk per trade in [[TradeExecution]]

### Step 4: Continuous Monitoring and Retraining

Models degrade the moment they are deployed as market regimes shift.

**Detection metric:** Kolmogorov-Smirnov statistic comparing recent live prediction distribution to historical validation distribution.

| Threshold | Action |
|---|---|
| KS statistic > 0.1 | Retrain on most recent data, re-evaluate before redeploying |
| Rolling window | 90-day training window |
| Retraining cadence | Every 30 days |
| Crypto/prediction markets | More frequent — regimes shift faster than equity |

---

## Connection to This Library

| Article Concept | Library Equivalent |
|---|---|
| Regime detection for model relevance | [[MarkovHedgeFundMethod]], [[HMM-Implementation-Python]] |
| LSTM non-linear emissions | Replaces Gaussian emission in [[HMM-Theory]] — same role as NN in [[NNHMMPaper]] |
| Walk-forward validation | [[Backtesting]] walk-forward methodology |
| 2% max risk per trade | [[TradeExecution]], [[Guardrails-RiskManagement]] |
| Regime-gated signal conviction | [[RegimeFilter-RiskManagement]] conviction thresholds |
| Daily loss halt | [[Guardrails-RiskManagement]] 3% halt |
| PyTorch framework | Same as [[NNHMMPaper]] (QuantConnect + PyTorch pipeline) |
| KS-based retraining trigger | Extends [[MarkovHedgeFundMethod]] regime stability logic |

---

## Key Takeaways for HMM Integration

1. **Non-stationarity is why HMM matters** — HMM regime detection provides exactly the stationary feature the NN needs: a probability distribution over discrete states rather than raw prices. Feeding HMM state probabilities as features to an LSTM is the natural bridge between these two approaches (see [[NNHMMPaper]]).

2. **The forget gate is the LSTM's regime detector** — mechanically equivalent to what HMM Chapman-Kolmogorov propagation does: discarding outdated regime beliefs and weighting toward recent evidence.

3. **Walk-forward = the only valid backtest** — matches [[Backtesting]] requirement for no lookahead bias.

4. **Expected accuracy 52–57%** — low enough to seem unimpressive, high enough to compound significantly with consistent sizing.

---

## Sources

- [Roan (@RohOnChain) — Neural Networks to Win Every Trade](https://x.com/RohOnChain/status/2052043443766194272)
- [[NNHMMPaper]] — academic paper combining HMM + PyTorch NN (83% return, Sharpe 0.77)
- [[HiddenMarkovTrading]] — HMM performance benchmarks
- [[HMM-Theory]] — Gaussian emission assumption that NN replaces
- [[Backtesting]] — walk-forward validation framework
