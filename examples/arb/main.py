"""
Example of non-atomic arb.  The external price represents a CEX using
a synthetic price stream.
"""

from typing import List
import numpy as np
import pandas as pd
from dataclasses import dataclass, asdict, field

from dexsim import DEX
from examples.gbm import gbm


@dataclass
class Data:
    step: List[int] = field(default_factory=list)
    cex_price: List[float] = field(default_factory=list)
    usdc_price: List[float] = field(default_factory=list)
    profit: List[float] = field(default_factory=list)

    def to_dataframe(self):
        return pd.DataFrame(asdict(self))


if __name__ == "__main__":
    STEPS = 100

    # GBM setup
    rng = np.random.default_rng(1234)
    volatility = 0.09
    mu = 0

    # create the Dex from the configuration file
    dex = DEX("./config.yaml")
    assert 1 == dex.total_number_of_pools()

    cex_usdc_prices = [gbm(mu, volatility, STEPS, rng) for _ in range(STEPS)]

    # Create wallets
    bob = dex.create_wallet()
    lp = dex.create_wallet()

    # mint tokens (NOT positions) for each user
    dex.pools.usdc_dai_100.mint_tokens(100_000, 100_000, lp)
    dex.pools.usdc_dai_100.mint_tokens(10_000, 10_000, bob)

    # mint a liquidity position in the range $0.98-$1.10
    dex.pools.usdc_dai_100.mint_liquidity_position(50_000, 50_000, 0.98, 1.10, lp)

    data = Data()
    for step in range(STEPS):
        # get the prices
        cex_price = cex_usdc_prices[step]
        usdc, _ = dex.pools.usdc_dai_100.exchange_rates()

        # If theres at least a $0.01 price difference
        # between CEX and Uniswap price try an arb.
        # Note: Bob always swaps $100.00
        if (cex_price - usdc) > 0.01:
            # sell dai for USDC
            _, received = dex.pools.usdc_dai_100.swap_1_for_0(100, bob)
            # simulate bob selling on the CEX and taking the profit
            profit = (cex_price * received) - 100

            # collect data
            data.step.append(step)
            data.cex_price.append(cex_price)
            data.usdc_price.append(usdc)
            data.profit.append(profit)

    print(data.to_dataframe())
