import mesa
from enum import Enum


class Signal(Enum):
    SELL_DIA = 1
    SELL_USDC = 2
    HODL = 3


def momentum_decision(factor, usdc_diff, dia_diff):
    """
    Track prices changes.  Look for the biggest price diff between the
    2 tokens and trade in that direction.
    """
    # find the one with the biggest change. Using the absolute value
    # to keep things simple...
    ad = abs(dia_diff)
    au = abs(usdc_diff)
    top_value = max(factor, max(ad, au))

    if top_value == factor:
        return Signal.HODL

    if top_value == ad:
        if dia_diff < 0:
            return Signal.SELL_DIA
        else:
            # buy dia
            return Signal.SELL_USDC

    if top_value == au:
        if usdc_diff < 0:
            return Signal.SELL_USDC
        else:
            # buy usdc
            return Signal.SELL_DIA


class MinnowAgent(mesa.Agent):
    def __init__(self, address, model):
        super().__init__(model)
        self.address = address
        self.model = model

        self.trade_factor = self.model.dex.config.agents.minnow.diff_factor
        self.trade_amount = self.model.dex.config.agents.minnow.swap_amount
        self.swap_probability = (
            self.model.dex.config.agents.minnow.hodl_swap_probability
        )

        self.model.dex.pools.usdc_dai_100.mint_tokens(
            self.model.dex.config.agents.minnow.fund.usdc,
            self.model.dex.config.agents.minnow.fund.dai,
            address,
        )

    def step(self):
        open_dia = self.model.dia_open_price
        open_usdc = self.model.usdc_open_price
        current_dia, current_usdc = self.model.dex.pools.usdc_dai_100.exchange_rates()
        dia_diff = current_dia - open_dia
        usdc_diff = current_usdc - open_usdc

        signal = momentum_decision(self.trade_factor, dia_diff, usdc_diff)

        # Either sell dia (for USDC), sell USDC (for DIA),HODL, or randomly pick one...
        if signal == Signal.HODL:
            # need this to get the price moving
            if self.model.random.random() < self.swap_probability:
                signal = self.model.random.choice([Signal.SELL_DIA, Signal.SELL_USDC])

        try:
            if signal == Signal.SELL_DIA:
                sold, bought = self.model.dex.pools.usdc_dai_100.swap_1_for_0(
                    self.trade_amount, self.address
                )
                self.model.temp_volume.append(sold + bought)

            if signal == Signal.SELL_USDC:
                sold, bought = self.model.dex.pools.usdc_dai_100.swap_0_for_1(
                    self.trade_amount, self.address
                )
                self.model.temp_volume.append(sold + bought)
        except RuntimeError as e:
            # may get sqrt price limit error from pushing prices around. We ignore here
            pass


class WhaleAgent(mesa.Agent):
    """
    The great manipulator.
    At certain intervals all whales will dump a bunch of DAI.
    """

    def __init__(self, address, model):
        super().__init__(model)
        self.address = address
        self.model = model

        dai = model.dex.config.agents.whale.fund.dai
        usdc = model.dex.config.agents.whale.fund.usdc
        self.model.dex.pools.usdc_dai_100.mint_tokens(usdc, dai, address)

    def step(self):
        if self.model.steps in self.model.whale_dump_steps:
            sold, bought = self.model.dex.pools.usdc_dai_100.swap_0_for_1(
                self.model.dex.config.agents.whale.dump, self.address
            )
            self.model.temp_volume.append(sold + bought)


class LiquidityProviderAgent(mesa.Agent):
    """
    Add / Remove pool liquidity
    Each agent starts with a single, random position.
    On step, the agent may increase or decrease their position.
    """

    def __init__(self, address, model):
        super().__init__(model)
        self.model = model
        self.address = address

        # info from configuration file
        initial_position = self.model.dex.config.agents.lp.initial_position
        lp_position = self.model.random.choice(initial_position.range)
        dai = self.model.dex.config.agents.lp.fund.dai
        usdc = self.model.dex.config.agents.lp.fund.usdc

        # mints tokens to the ERC20 pair
        self.model.dex.pools.usdc_dai_100.mint_tokens(usdc, dai, self.address)

        # mint a position
        _, _, _, self.tokenid = (
            self.model.dex.pools.usdc_dai_100.mint_liquidity_position(
                initial_position.usdc,
                initial_position.dai,
                lp_position[0],
                lp_position[1],
                self.address,
            )
        )

    def step(self):
        pass
