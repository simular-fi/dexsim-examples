from typing import List
from dataclasses import dataclass, asdict, field

import mesa
import pandas as pd
from tqdm import tqdm

from dexsim import DEX
from examples.whales.agents import WhaleAgent, MinnowAgent, LiquidityProviderAgent

CONFIG_FILE = "./config.yaml"


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
    volume: List[float] = field(default_factory=list)
    active_tick: List[int] = field(default_factory=list)

    def to_dataframe(self):
        return pd.DataFrame(asdict(self))


class WhaleModel(mesa.Model):
    def __init__(self, config):
        super().__init__()

        # setup dex and pool(s) from config
        self.dex = DEX(config)
        self.random.seed(self.dex.config.model.random_seed)

        # data collection
        self.trading_data = TradingData()
        self.temp_volume = []

        self.dia_open_price = 0.0
        self.usdc_open_price = 0.0

        # pick whale steps they'll dump at
        self.whale_dump_steps = (
            int(self.dex.config.model.steps * 0.35),
            int(self.dex.config.model.steps * 0.45),
            int(self.dex.config.model.steps * 0.55),
        )

        print(f"{ self.whale_dump_steps}")

        # create the lp agents
        lpagents = self.dex.create_many_wallets(num=self.dex.config.agents.lp.num)
        for lp_address in lpagents:
            self.agents.add(LiquidityProviderAgent(lp_address, self))

        # create the trader agents
        ziagents = self.dex.create_many_wallets(num=self.dex.config.agents.minnow.num)
        for za in ziagents:
            self.agents.add(MinnowAgent(za, self))

        # create the whales
        whaleagents = self.dex.create_many_wallets(num=self.dex.config.agents.whale.num)
        for ws in whaleagents:
            self.agents.add(WhaleAgent(ws, self))

    def step(self):
        _, tick = self.dex.pools.usdc_dai_100.get_sqrtp_tick()
        open_dia, open_usdc = self.dex.pools.usdc_dai_100.exchange_rates()  # open

        # Update model open prices. This is used as a quick ref for agents
        self.dia_open_price = open_dia
        self.usdc_open_price = open_usdc

        # collect open prices
        self.trading_data.open_dia_price.append(open_dia)
        self.trading_data.open_usdc_price.append(open_usdc)
        self.trading_data.active_tick.append(tick)

        self.agents.shuffle_do("step")

        # collect close price data
        close_dia, close_usdc = self.dex.pools.usdc_dai_100.exchange_rates()  # close
        self.trading_data.close_dia_price.append(close_dia)
        self.trading_data.close_usdc_price.append(close_usdc)

        # collect step and volume data
        self.trading_data.time.append(self.steps)
        total_volume = sum(self.temp_volume)
        self.trading_data.volume.append(total_volume)
        self.temp_volume = []

    def run_model(self):
        for _ in tqdm(range(self.dex.config.model.steps)):
            self.step()

        return self.trading_data.to_dataframe()


if __name__ == "__main__":

    model = WhaleModel(CONFIG_FILE)
    nsteps = model.dex.config.model.steps
    nminnows = model.dex.config.agents.minnow.num

    print(f"... running the model with {nminnows} agents for {nsteps} steps ...")
    trading_data = model.run_model()

    print(trading_data)
    print("----")
