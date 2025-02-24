import mesa
from dexsim.utils import from_18


class WhaleAgent(mesa.Agent):
    """
    The great manipulator.
    At certain intervals all whales will dump a bunch of DAI.
    """

    def __init__(self, address, model):
        super().__init__(model)
        self.address = address
        self.model = model

        dia = model.dex.config.agents.whale.fund.dia
        usdc = model.dex.config.agents.whale.fund.usdc
        self.model.dex.pools.dia_usdc.mint_tokens(dia, usdc, address)

    def step(self):
        if self.model.steps in self.model.whale_dump_steps:
            sold, bought = self.model.dex.pools.dia_usdc.swap_0_for_1(
                self.model.dex.config.agents.whale.dump, self.address
            )
            self.model.temp_volume.append(from_18(sold) + from_18(bought))
