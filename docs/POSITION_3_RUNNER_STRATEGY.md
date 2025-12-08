# 🏃 Position 3 "Runner" Strategy

## What Is a Runner Strategy?

A **runner** is a position that stays open after the main profit target (TP2) is reached, using a trailing stop to capture extended price moves.

### Classic Scaling Out:
1. **Position 1**: Takes quick profit at TP1 ✅
2. **Position 2**: Takes main profit at TP2 ✅
3. **Position 3**: **Stays open** with trailing stop 🏃💨

**Result**: You secure profits while still capturing big trends!

---

## How It Works

### **Phase 1: Before TP2 (Normal Trading)**

```
Signal: BUY GOLD 4193-4188
TP1: 4230
TP2: 4250

Positions Placed:
- Position 1 (4193): SL 4180, TP 4230
- Position 2 (middle): SL 4175, TP 4250
- Position 3 (4188): SL 4170, NO TP (runner!)
```

**Position 3 has NO TP** - it will run with trailing stop after TP2!

---

### **Phase 2: TP1 Hit (4230)**

```
Price reaches 4230

✅ Position 1 closes at TP1 (37 pips profit)
⏳ Position 2 still open (fixed SL at 4175)
⏳ Position 3 still open (fixed SL at 4170)
```

Position 3 is still using **fixed SL** (not trailing yet).

---

### **Phase 3: TP2 Hit (4250) - ACTIVATION!**

```
Price reaches 4250

✅ Position 2 closes at TP2 (75 pips profit)
🏃 Position 3 RUNNER ACTIVATED!
   - Does NOT close
   - Switches from fixed SL to TRAILING STOP
   - Trailing distance: 20 pips
   - New SL: 4249.80 (20 pips below 4250)
```

**This is the key moment**: Position 3 transforms into a runner!

---

### **Phase 4: Extended Move (Runner in Action)**

```
Price continues rising beyond TP2...

Price at 4260:
- Position 3 SL moves to 4259.80
- 🔒 Locking 71.8 pips profit

Price at 4270:
- Position 3 SL moves to 4269.80
- 🔒 Locking 81.8 pips profit

Price at 4280:
- Position 3 SL moves to 4279.80
- 🔒 Locking 91.8 pips profit

Price at 4290:
- Position 3 SL moves to 4289.80
- 🔒 Locking 101.8 pips profit!
```

The runner captures the **entire extended move**!

---

### **Phase 5: Reversal (Trailing Stop Works)**

```
Price reverses...

Price drops to 4289.80
💥 Position 3 closes at trailing SL

Final Result:
✅ Position 1: 37 pips
✅ Position 2: 75 pips  
✅ Position 3: 101.8 pips (runner!)

Total: 213.8 pips from one signal! 🎉
```

**Without runner**: Would have closed all at TP2 (max 75 pips each)
**With runner**: Captured an extra 101.8 pips on Position 3!

---

## Visual Example - BUY Trade

```
Price
  ↑
4290 │                    Position 3 running here!
     │                    SL: 4289.80 (trailing)
4280 │                    ↑
     │                    │
4270 │              Position 3 trailing
     │                    ↑
4260 │                    │
     │                    │
4250 ──────── TP2 ─────── ⚡ RUNNER ACTIVATED!
     │        Position 2 closes
     │        Position 3 switches to trailing
     │
4230 ──────── TP1 ────────
     │        Position 1 closes
     │
4193 ═════════════════════ Position 1 Entry
     │
4190 ─────── Middle ───────
     │
4188 ═════════════════════ Position 3 Entry (RUNNER)
     │
4180 ─────── Initial SL ───
     │
     └──────────────────→ Time
```

Position 3 climbs with the price after TP2! 📈

---

## For SELL Trades

Same concept, but reversed:

```
Entry Order:
- Position 1 (upper): RUNNER (farthest from current price)
- Position 2 (middle): Closes at TP2
- Position 3 (lower): Closes at TP1

When TP2 hit:
- Position 1 becomes runner (trailing stop ABOVE price)
- Follows price DOWN as it continues to fall
```

---

## Configuration

In `config.env`:

```env
# Position 3 "Runner" Strategy (Advanced)
POSITION_3_RUNNER_ENABLED=true          # Enable runner strategy
POSITION_3_TRAILING_AFTER_TP2=true      # Activate trailing after TP2

# Trailing Stop Settings (used by runner)
TRAILING_STOP_PIPS=20                   # Trailing distance
```

---

## Benefits

### **1. Capture Extended Trends**
- Don't miss big moves beyond TP2
- Maximize profit on strong trends
- No need to predict how far price will go

### **2. Risk-Free After TP2**
- Already secured profits from Position 1 & 2
- Runner is "playing with the house's money"
- Can afford to let it run

### **3. Automatic Management**
- No manual intervention needed
- Trailing stop adjusts automatically
- Locks in profits as price moves

### **4. Best of Both Worlds**
- Fixed profits: Position 1 & 2 secured
- Unlimited upside: Position 3 catches runners

---

## Comparison: With vs Without Runner

### **Scenario: Strong Trend Beyond TP2**

**WITHOUT Runner Strategy:**
```
Signal: BUY 4193-4188, TP2: 4250
Price reaches 4280 (extended move)

Position 1: Closes at TP1 (4230) = 37 pips
Position 2: Closes at TP2 (4250) = 75 pips
Position 3: Closes at TP2 (4250) = 62 pips

Total: 174 pips
Missed opportunity: 30 pips (price went to 4280!)
```

**WITH Runner Strategy:**
```
Signal: BUY 4193-4188, TP2: 4250
Price reaches 4280 (extended move)

Position 1: Closes at TP1 (4230) = 37 pips
Position 2: Closes at TP2 (4250) = 75 pips
Position 3: Runner catches move to 4280 = 92 pips!

Total: 204 pips (+30 pips extra!)
Captured the full move! 🎉
```

---

## When Runner Strategy Shines

### ✅ **Perfect For:**
- **Strong trends** that continue beyond TP2
- **Breakout moves** (e.g., news events)
- **Trending markets** (gold, major forex pairs)
- **High conviction signals**

### ❌ **Less Effective In:**
- **Ranging markets** (price oscillates, hits stops)
- **Choppy conditions** (whipsaws)
- **Low volatility** (doesn't move much past TP2)

---

## Real Trade Example

### **Signal from Telegram:**
```
BUY GOLD 4193-4188
SL: 4180, 4175, 4170
TP: 4230, 4250
```

### **Bot Actions:**

**1. Entry Phase**
```
Position 1 at 4193: SL 4180, TP 4230
Position 2 at 4190: SL 4175, TP 4250
Position 3 at 4188: SL 4170, NO TP (runner)

Logs show:
[INFO] 🏃 Position 3 configured as RUNNER (no TP, trailing stop after TP2)
```

**2. TP1 Hit**
```
Price: 4230
Position 1 closes
Profit: $37 per lot

Logs show:
[INFO] Position #123456 closed at TP1
```

**3. TP2 Hit - ACTIVATION!**
```
Price: 4250
Position 2 closes
Position 3 stays open!

Logs show:
[WARNING] 🎯 TP2 REACHED for signal abc123 at price 4250
[WARNING] 🏃 Position 3 #789 RUNNER activated - Trailing stop now enabled!
[WARNING] 🔒 Trailing Stop moved for #789: SL=4249.80 (locking 61.8 pips profit)
```

**4. Extended Move**
```
Price: 4260
Logs show:
[WARNING] 🔒 Trailing Stop moved for #789: SL=4259.80 (locking 71.8 pips profit)

Price: 4270
[WARNING] 🔒 Trailing Stop moved for #789: SL=4269.80 (locking 81.8 pips profit)

Price: 4280
[WARNING] 🔒 Trailing Stop moved for #789: SL=4279.80 (locking 91.8 pips profit)
```

**5. Reversal & Close**
```
Price reverses to 4279.80
Position 3 closes at trailing SL

Final tally:
Position 1: $37
Position 2: $75
Position 3: $91.80

Total: $203.80 per lot! 🎉
```

---

## Logs You'll See

```
[INFO] 🏃 Position 3 configured as RUNNER (no TP, trailing stop after TP2)
[INFO] ✅ BUY LIMIT #789: XAUUSD 0.10 lot @ 4188.0 | SL=4170.0 TP=None ATTACHED

[WARNING] 🎯 TP2 REACHED for signal abc123 at price 4250.0
[WARNING] 🏃 Position 3 #789 RUNNER activated - Trailing stop now enabled!

[WARNING] 🔒 Trailing Stop moved for #789: SL=4249.80 (locking 61.8 pips profit)
[WARNING] 🔒 Trailing Stop moved for #789: SL=4259.80 (locking 71.8 pips profit)
[WARNING] 🔒 Trailing Stop moved for #789: SL=4269.80 (locking 81.8 pips profit)
```

---

## FAQ

### Q: What if price never reaches TP2?
**A:** Position 3 keeps its fixed SL and stays open like normal. It will close at SL if price reverses.

### Q: Can Position 3 close before TP2?
**A:** Yes, if price hits Position 3's SL, it closes at a loss (like any normal position).

### Q: What if price hits TP2 then immediately reverses?
**A:** Position 3 activates trailing at TP2, so it has protection 20 pips below TP2. It will close with good profit.

### Q: Does this work for both BUY and SELL?
**A:** Yes! 
- **BUY**: Position 3 is the lowest entry (farthest below)
- **SELL**: Position 1 is the highest entry (farthest above)
The bot handles both automatically.

### Q: Can I disable the runner strategy?
**A:** Yes, set `POSITION_3_RUNNER_ENABLED=false` in `config.env`. Position 3 will then close at TP2 like normal.

### Q: How often does this capture big moves?
**A:** Depends on market conditions. In strong trends: often. In ranging markets: rarely. But when it works, it's very profitable!

---

## Tips for Success

1. **Use in trending markets**
   - Gold during news
   - Major forex pairs in strong trends
   - Avoid in choppy/ranging conditions

2. **Adjust trailing distance**
   - Tight markets: 15 pips
   - Normal: 20 pips (default)
   - Volatile: 25-30 pips

3. **Monitor results**
   - Track how often runner captures extended moves
   - Adjust settings based on performance
   - Disable if market conditions aren't favorable

4. **Trust the system**
   - Let the runner run!
   - Don't close manually
   - Trailing stop will protect profits

---

## Summary

✅ **Position 3 Runner Strategy**:
- Position 1 → Closes at TP1 (quick profit)
- Position 2 → Closes at TP2 (main target)
- Position 3 → Stays open with trailing stop after TP2 (captures runners!)

✅ **Activation**:
- Fixed SL before TP2 is reached
- Switches to trailing stop when TP2 is hit
- Follows price with 20 pips distance

✅ **Benefits**:
- Captures extended moves beyond TP2
- Maximizes profit on strong trends
- Automatic, hands-free management

✅ **Already Active**:
```env
POSITION_3_RUNNER_ENABLED=true
POSITION_3_TRAILING_AFTER_TP2=true
```

**Let your winners run!** 🏃💨💰

