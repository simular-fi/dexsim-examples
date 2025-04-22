
# Uniswap v3 USDC/DAI Simulation

Simulate trading and liquidity activity on a USDC/DAI Uniswap v3 pool. The goal is to see if prices can be manipulated by a few traders.

## Model Information
* Uses Uniswap v3 contract bytecode from Ethereum main chain. Mirrors the exact setup of Uniswap. The pool is created from the settings in the `config.yaml` with an initial price of **$1.00**
* Token 0: USDC
* Token 1: DAI
* **500** steps of execution
*  Agent populations:
    * **100** Traders (minnows)
    * **10** Liquidity Providers
    * **3** Whale traders

## Agents
* **Minnows:** Move with the price. If there's enough (configurable) difference between the 
current and last price, they will swap in that direction.  For example, if DAI is down, they'll 
swap (sell) DAI for USDC, etc...
* **Whales:** All whales work together to manipulate the market.  At pre-determined steps, they
will dump a large amount of USDC for DAI.
* **Liquidity Provider (LP):** On initialization, each LP randomly selects a tick range to create a position and stays in that position for the duration of the simulation.

## Model Parameters
* Minnows
    * **initial funding:** 10_000
    * **swap amount:** 100 
    * **diff_factor:** 0.01 Used to determine when and what to swap. Based on the price difference calculation, the agent may decide to: sell dia, sell usdc, or HODL. 
    * **probablity of swap:** 0.5  *Only used when diff_factor calculation issues a HODL. If there
    is a HODL, a coin toss is used to determine if they should still swap.  This is needed
    to bootstrap trading.*
* Whales
    * **initial funding:** 1_000_000
    * **swap amount:** 5000 
    * **activiation steps:** 3 pre-determined step numbers when all whales will swap DIA for USDC
* Liquidity Providers
    * **initial funding:** 10_000
    * **initial position amount for each token:** 1000
    * **random liquidity increases:** 500..1000
    * **random liquidity decreases:** 5%..20%

## Configuration
It's important to note the configuration file can be used for more than just pool configuration.  In this example, we use it to configure the model and agents as well as the pool.
