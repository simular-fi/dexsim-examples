from enum import Enum

import mesa
from dexsim.utils import from_18


class Signal(Enum):
    SELL_DIA = 1
    SELL_USDC = 2
    HODL = 3


def momentum_decision(factor, dia_diff, usdc_diff):
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

        self.model.dex.pools.dia_usdc.mint_tokens(
            self.model.dex.config.agents.minnow.fund.dia,
            self.model.dex.config.agents.minnow.fund.usdc,
            address,
        )

    def step(self):
        open_dia = self.model.dia_open_price
        open_usdc = self.model.usdc_open_price
        current_dia, current_usdc = self.model.dex.pools.dia_usdc.exchange_prices()

        dia_diff = current_dia - open_dia
        usdc_diff = current_usdc - open_usdc

        signal = momentum_decision(self.trade_factor, dia_diff, usdc_diff)

        # Either sell dia (for USDC), sell USDC (for DIA),HODL, or randomly pick one...
        if signal == Signal.HODL:
            # need this to get the price moving
            if self.model.random.random() < self.swap_probability:
                signal = self.model.random.choice([Signal.SELL_DIA, Signal.SELL_USDC])

        if signal == Signal.SELL_DIA:
            # 0 fo 1
            sold, bought = self.model.dex.pools.dia_usdc.swap_0_for_1(
                self.trade_amount, self.address
            )
            self.model.temp_volume.append(from_18(sold) + from_18(bought))

        if signal == Signal.SELL_USDC:
            # 1 for 0
            sold, bought = self.model.dex.pools.dia_usdc.swap_1_for_0(
                self.trade_amount, self.address
            )
            self.model.temp_volume.append(from_18(sold) + from_18(bought))
