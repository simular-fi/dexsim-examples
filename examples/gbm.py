import numpy as np
import matplotlib.pyplot as plt


def gbm(mu: float, sigma: float, num_steps: int, rng: np.random.Generator) -> float:
    """
    Generate a Geometric Brownian Motion price

    Note: we automatically calculate dt as a
    fraction of the number steps 'N':  dt = 1/N

    Parameters:
        mu   : drift
        sigma: volatility
        rng  : random number generator
    Returns:
        the value as a float
    """
    # time as a factor of the total steps
    dt = 1.0 / num_steps
    return np.exp((mu - 0.5 * sigma**2) * dt + sigma * np.sqrt(dt) * rng.normal())


if __name__ == "__main__":
    # Example
    rng = np.random.default_rng(1234)
    volatility = 0.09
    mu = 0
    steps = 100

    y = [gbm(mu, volatility, steps, rng) for _ in range(steps)]
    x = [i for i in range(steps)]

    # plot
    plt.style.use("_mpl-gallery")
    fig, ax = plt.subplots(figsize=(7, 7), layout="constrained")
    ax.set_xlabel("steps")
    ax.set_ylabel("price")
    ax.plot(x, y, linewidth=1.0)

    plt.show()
