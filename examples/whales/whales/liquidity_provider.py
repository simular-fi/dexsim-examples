import mesa
from dexsim.utils import tick_to_price, calculate_liquidity_balance


def active_tick_in_range(at, lt, up):
    return lt <= at <= up


class LiquidityProviderAgent(mesa.Agent):
    """
    The LP'er.  Without me, there's nothing to trade...

    Add / Remove pool liquidity
    Each agent starts with a single, random position.
    On step, the agent may increase or decrease their position.
    """

    def __init__(self, address, model):
        super().__init__(model)
        self.model = model
        self.address = address

        dia = self.model.dex.config.agents.lp.fund.dia
        usdc = self.model.dex.config.agents.lp.fund.usdc

        # mint tokens needed to trade. This mints tokens to the ERC20 pair
        self.model.dex.pools.dia_usdc.mint_tokens(dia, usdc, self.address)

        initial_position = self.model.dex.config.agents.lp.initial_position
        lp_position = self.model.random.choice(initial_position.range)

        self.increase_range = self.model.dex.config.agents.lp.increase_range
        self.decrease_range = self.model.dex.config.agents.lp.decrease_range

        # mint a position
        _, _, self.tokenid = self.model.dex.pools.dia_usdc.mint_liquidity_position(
            initial_position.dia,
            initial_position.usdc,
            lp_position[0],
            lp_position[1],
            self.address,
        )

    def step(self):
        """
        increase, decrease liquidity or do nothing
        """

        # collect data on liquidity
        self.track_liquidity()

        # random choice:
        # 0 = do nothing
        # 1 = increase
        # 2 = decrese
        choice = self.model.random.choice([0, 1, 2])
        if choice == 0:
            return
        if choice == 1:
            # increase
            self.increase_liquidity()
        else:
            # decrease
            self.decrease_liquidity()

    def increase_liquidity(self):
        # select amount to add
        amount = self.model.random.randrange(
            self.increase_range[0], self.increase_range[1]
        )
        # check balance to make sure we have enough
        x, y = self.model.dex.pools.dia_usdc.token_pair_balance(self.address)
        if amount <= x and amount <= y:
            # add liquidity
            self.model.dex.pools.dia_usdc.increase_liquidity(
                self.tokenid, amount, amount, self.address
            )

    def decrease_liquidity(self):
        # randomly remove a percentage of an agents position
        _, _, _, liquidity = self.model.dex.pools.dia_usdc.get_liquidity_position(
            self.tokenid
        )
        if liquidity == 0:
            # nothing to remove...
            return
        # select from 5-20%
        percentage = (
            self.model.random.randrange(self.decrease_range[0], self.decrease_range[1])
            / 100
        )
        self.model.dex.pools.dia_usdc.remove_liquidity(
            self.tokenid, percentage, self.address
        )

    def track_liquidity(self):
        """
        Data collection
        """
        pool = self.model.dex.pools.dia_usdc

        _, lt, ut, liq = pool.get_liquidity_position(self.tokenid)
        lower_price = tick_to_price(lt)
        upper_price = tick_to_price(ut)
        _, p1 = pool.exchange_prices()
        r0, r1 = calculate_liquidity_balance(liq, lower_price, upper_price, p1)

        self.model.liquidity_data.time.append(self.model.steps)
        self.model.liquidity_data.tokenid.append(self.tokenid)
        self.model.liquidity_data.dia.append(r0)
        self.model.liquidity_data.usdc.append(r1)
        self.model.liquidity_data.lower_tick.append(lower_price)
        self.model.liquidity_data.upper_tick.append(upper_price)
