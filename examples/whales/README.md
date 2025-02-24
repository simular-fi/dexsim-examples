
# Scenario

Whales, Minnows, and LPs.

# TODO Document what this means: Reverted: "revert: SPL".
See: https://support.uniswap.org/hc/en-us/articles/7421987762829-Swap-errors-Advanced

What if Whales that control alot of a given token use perceived news (sentiment) as a cover for market manipulation?

## Agents
- **Whale:**  large quantity of tokens. Use sentiment as a way to mask manipulation.  When they sense news can lead to bearish sentiment, they preemptively dump large quanities to fuel sentiment. When prices drop they accumulate. Whales ignore noisy market sentiment. Whales coordinate amongst themselves...
- **Lp:** Track market movement. May dhange positions based on price to capture fees.
- **Minnows:** Move on momentum signals, following the herd, dumping and buying based on what they see the others (whales) doing, but they're always step or 2 behind the curve...

## Data
- Show exchange price over time
- Show liquidity balances and active tick over time

## Agent Behavior
- Whale: 2 big dumps during run.  Make sure both whales and LPs have enough money...
- LP: Check if current price is in position.  
  - If not:
    - remove and move to new position
    - hodl
  - else:
    - increase
    - hodl
- Minnow: check price
  - IF price is going down: sell
  - IF price is going up: buy
  - else hodl

## Exognenous Shock via market sentiment

How to construct a utility function for this?

Use simple momentum signal as bullish/bearish/neutral. The includes a count based on different risk aversion weights?


Flow: 

This can give us OHLCV data...
for _ in range(days):
    open = prevous close
    for _in range(hours)
        track HLV
        model.step()
    close data

how to preset data for rolling numbers...