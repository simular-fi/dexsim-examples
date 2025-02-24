import mesa
import pandas as pd
from tqdm import tqdm
from dexsim.dex import DEX

from typing import List
from dataclasses import dataclass, asdict, field


"""
Need: ZIAgent and LPer.  Just have single LPer with 2-3 positions
"""

CONFIG = "./config.yaml"


## Agents ##


class LazyLpAgent(mesa.Agent):
    """
    Liquidity agent.  Creates 1 or more positions on startup and then just HODLs
    """

    def __init__(self, address, model):
        super().__init__(model)

        # agent's wallet address
        self.address = address

        # Get info for config, etc...
        pool = model.dex.pools.dia_usdc
        dia_to_mint = model.dex.config.agents.lp.fund.dia
        usdc_to_mint = model.dex.config.agents.lp.fund.usdc

        # Mint tokens on the respective ERC20 contracts
        pool.mint_tokens(dia_to_mint, usdc_to_mint, self.address)

        # mint liquidity position(s)
        for pos in model.dex.config.agents.lp.positions.ranges:
            _, _, self.tokenid = pool.mint_liquidity_position(
                model.dex.config.agents.lp.positions.amounts,
                model.dex.config.agents.lp.positions.amounts,
                pos[0],
                pos[1],
                self.address,
            )

    def step(self):
        """Doesn't do anything on step"""
        pass


class ZIAgent(mesa.Agent):
    """
    Random Trader with configurable probability of swap
    """

    def __init__(self, address, model):
        super().__init__(model)
        self.address = address

        # Get info for config, etc...
        self.pool = model.dex.pools.dia_usdc
        dia_to_mint = model.dex.config.agents.zi.fund.dia
        usdc_to_mint = model.dex.config.agents.zi.fund.usdc

        self.swap_probability = model.dex.config.agents.zi.swap_probability
        self.swap_amount = model.dex.config.agents.zi.swap_amount

        # mint tokens for the agent
        self.pool.mint_tokens(dia_to_mint, usdc_to_mint, address)

    def step(self):
        if self.model.random.random() < self.swap_probability:
            token_to_buy = self.model.random.choice(["dia", "usdc"])
            if token_to_buy == "dia":
                # swap usdc for dia
                self.pool.swap_1_for_0(self.swap_amount, self.address)
            else:
                # swap dia for usdc
                self.pool.swap_0_for_1(self.swap_amount, self.address)


## Data Collection ##
@dataclass
class TradingData:
    """
    Container to collect trading data
    """

    time: List[int] = field(default_factory=list)
    open_dia_price: List[float] = field(default_factory=list)
    close_dia_price: List[float] = field(default_factory=list)
    open_usdc_price: List[float] = field(default_factory=list)
    close_usdc_price: List[float] = field(default_factory=list)

    def to_dataframe(self):
        d = asdict(self)
        return pd.DataFrame(d)


## Model ##


class BasicModel(mesa.Model):
    def __init__(self):
        super().__init__()

        self.trading_data = TradingData()

        # setup dex and pool(s) from config
        self.dex = DEX(CONFIG)

        # 1. Create wallets in the EVM for agents. Defaults to funding the wallet with 1 ETH
        # 2. Add agents to the model
        ziagents_wallets = self.dex.create_many_wallets(
            num=self.dex.config.agents.zi.num
        )
        for w in ziagents_wallets:
            self.agents.add(ZIAgent(w, self))

        lpagents_wallets = self.dex.create_many_wallets(
            num=self.dex.config.agents.lp.num
        )
        for w in lpagents_wallets:
            self.agents.add(LazyLpAgent(w, self))

    def step(self):
        # collect time (step), and open prices
        self.trading_data.time.append(self.steps)

        # fetch prices from the pool
        open_dia, open_usdc = self.dex.pools.dia_usdc.exchange_prices()
        self.trading_data.open_dia_price.append(open_dia)
        self.trading_data.open_usdc_price.append(open_usdc)

        # activate the agents
        self.agents.shuffle_do("step")

        # collect close prices
        close_dia, close_usdc = self.dex.pools.dia_usdc.exchange_prices()
        self.trading_data.close_dia_price.append(close_dia)
        self.trading_data.close_usdc_price.append(close_usdc)

    def run_model(self):
        for _ in tqdm(range(self.dex.config.model.steps)):
            self.step()
        return self.trading_data.to_dataframe()

    def run_interactive(self):
        self.step()
        return self.trading_data.to_dataframe()


if __name__ == "__main__":

    # Initiate and run the model
    model = BasicModel()

    # print the dataframe results
    df = model.run_model()
    print(df)
