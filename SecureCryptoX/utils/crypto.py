import random


def get_btc_price():

    base_price = 290000

    fluctuation = random.randint(
        -5000,
        5000
    )

    return base_price + fluctuation