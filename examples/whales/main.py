from whales.model import StablecoinModel

if __name__ == "__main__":

    model = StablecoinModel("./config.yaml")
    nsteps = model.dex.config.model.steps
    nminnows = model.dex.config.agents.minnow.num
    saveit = model.dex.config.model.output.get("save", False)
    tradingfn = model.dex.config.model.output.trading
    liqfn = model.dex.config.model.output.liquidity

    print(f"... running the model with {nminnows} agents for {nsteps} steps ...")
    trading_data, liquidity_data = model.run_model()

    print(trading_data)
    print("----")
    print(liquidity_data)

    if saveit:
        trading_data.to_parquet(tradingfn)
        liquidity_data.to_parquet(liqfn)
