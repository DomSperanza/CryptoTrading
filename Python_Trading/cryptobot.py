import os
from dotenv import load_dotenv


def cryptobot(symbol: str, strategy: str, paper: bool = True) -> None:
    '''
    Activates the cryptobot to begin trading based on a given strategy.

    Parameters:
        symbol : str
            The symbol of the crypto to be traded
        strategy : str
            The strategy to be implemented
        paper : bool, default True
            Paper (simulated) or real trading

    Returns:
        None

    '''

    # loads in environment variables from .env file
    load_dotenv()
    if paper:
        # test/paper enviro
        key_var = 'BINANCE_PAPER_API'
        secret_var = 'BINANCE_PAPER_SECRET'
    else:
        pass
        # # real trading
        key_var = 'BINANCE_API'
        secret_var = 'BINANCE_SECRET'

    # assign desired API keys
    api_key = os.getenv(key_var)
    api_secret = os.getenv(secret_var)

    # print(api_key, api_secret)
    # client = Client(api_key, api_secret, testnet=paper)


if __name__ == '__main__':

    # input restrictions
    allowed_symbols = ['BTCUSDT']
    allowed_strategies = ['heikenashi']
    bools = {'true': True, 'false': False, }

    # user input + restriction checks
    while True:
        symbol = input('Enter Symbol: ').upper()

        if symbol in allowed_symbols:
            break

        print("-- Enter a valid symbol --")

    while True:
        strategy = input('Enter Strategy: ').lower()

        if strategy in allowed_strategies:
            break

        print("-- Enter a valid strategy --")

    while True:
        paper = input('Paper trading? (True or False):').lower()

        try:
            paper = bools[paper]
            break
        except:
            print("-- Enter a valid boolean --")

    # run bot with user inputs
    cryptobot(symbol, strategy, paper)
