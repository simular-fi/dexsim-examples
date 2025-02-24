import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

TD = "./data/trading.parquet"
LD = "./data/liquidity.parquet"


def trading_prices_over_time(td, ld):
    fig, ax = plt.subplots(4, layout="tight")

    # prices
    ax[0].set_title("DIA/USDC")
    ax[0].set_ylabel("price")
    ax[0].plot(td["time"], td["open_usdc_price"], label="DIA")
    ax[0].plot(td["time"], td["open_dia_price"], label="USDC")
    ax[0].legend(ncols=2, loc="upper left")

    # volume
    ax[1].set_ylabel("volume")
    ax[1].fill_between(td["time"], td["volume"], color="#444")

    # liquidity
    vol = ld.groupby("time", as_index=False)[["dia", "usdc"]].sum()
    ax[2].set_ylabel("liquidity")
    ax[2].fill_between(vol["time"], vol["dia"], label="DIA")
    ax[2].fill_between(vol["time"], vol["usdc"], label="USDC", alpha=0.85)
    ax[2].legend(ncols=2, loc="upper left")

    # Ticks
    ax[3].set_ylabel("tick range")
    ax[3].plot(td["time"], td["active_tick"], color="red")
    ax[3].grid()

    st.pyplot(fig)


def load_data():
    td = pd.read_parquet(TD)
    ld = pd.read_parquet(LD)
    return (td, ld)


def ui(info, td, ld):
    st.set_page_config(page_title=f"DIA/USDC Model")
    st.write(info)
    st.write(
        """
        ## Data Collection
        Both trading and liquidity data are collected and saved into separate files in parquet format.
        """
    )
    st.write("#### Trading Data format")
    st.dataframe(td.head(3), hide_index=True)
    st.write(
        """
        'active_tick' reflects the current position in the liquidity pool, and can translate to 
        the price. When the 'active_tick' is in the range of a LPs position, they earn fees.
        """
    )
    st.write("#### Liquidity Data format")
    st.dataframe(ld.head(3), hide_index=True)
    st.write(
        """The upper and lower ticks describe the position range in price, not tick number. 'dia' and 'usdc'
        are the quantity of tokens in each position, at each step (time). 'tokenid' is the NFT id for the position. 
        """
    )

    st.write(
        """
        ## Results
        Data is plotted in the following 4 graphs:
        * Prices
        * Volume
        * Liquidity
        * Active tick.  *Ticks are units of measurement that are used to define specific price ranges*

        Notice how prices respond to whale activity. Whale activity is highlighted in the
        volume graph (3 spikes in volume). USDC liquidity becomes depleted over time as the
        drop in DIA price creates swap signals for minnows. Tick movement represents potential
        changes in active LP positions which effects liquidity as it's shifted when the position 
        become inactive.

        In this model, LPs don't act to change positions in response to price change. This further 
        impacts liquidity and by extension the price.   
        
        In Uniswap v3, LPs provide liquidity within a specific price (tick) range rather than across the 
        entire curve. If the price moves outside the selected range, their liquidity is converted 
        entirely into one of the assets, effectively removing them from earning fees. This amplifies 
        impermanent loss because the LP is exposed to larger price fluctuations within a narrow range. 
        """
    )
    trading_prices_over_time(td, ld)


if __name__ == "__main__":
    with open("./model-info.md") as f:
        info = f.read()
    td, ld = load_data()
    ui(info, td, ld)
