"""
Graph the model in realtime...
"""

import streamlit as st
import matplotlib.pyplot as plt

from model import BasicModel, TradingData


def chart(td):
    fig, ax = plt.subplots(1, layout="tight")
    ax.set_title("DIA/USDC")
    ax.set_ylabel("price")
    ax.plot(td["time"], td["open_dia_price"], label="DIA")
    ax.plot(td["time"], td["open_usdc_price"], label="USDC")
    ax.legend(ncols=2, loc="upper left")
    ax.grid()
    st.pyplot(fig)
    plt.close()


def ui(model):
    st.write("# Basic Model Example")
    st.text("this is an example...")

    start = st.button("Start", type="primary", help="Run the model")
    st.session_state.td = TradingData().to_dataframe()
    placeholder = st.empty()

    if start:
        for i in range(model.dex.config.model.steps):
            with placeholder.container():
                st.session_state.td = model.run_interactive()
                chart(st.session_state.td)
    else:
        with placeholder.container():
            chart(st.session_state.td)


if __name__ == "__main__":
    ui(BasicModel())
