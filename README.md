# Algorithmic Trading
This is the start of a project where we make a bot that will automatically buy and sell crypto for us. 

---

For updating requirements.txt, use:
```
pip install pipreqs
pipreqs . --force --ignore **/Archive
```
More info: https://github.com/bndr/pipreqs

<!-- To start the flask app (dashboard)
```
flask run
``` -->

To run the app in a docker container:
```
docker build .
```


---

Below is a flowchart for describing the *(desired)* structure of the program.

Uses Mermaid Markdown https://mermaid.live/

```mermaid
    flowchart TD
    subgraph Overview
        subgraph Docker Container 
        Env[Env Variables]
        
        CLI["CLI (Inputs)"] --> Symbol[Symbol]
        CLI --> InputStrat[Strategy]
        CLI --> Type[Paper or Real]

        Symbol -- parameter --> CryptoBot((CryptoBot))
        InputStrat -- parameter --> CryptoBot
        Type -- parameter --> CryptoBot
        Env --> CryptoBot

        CryptoBot -- run --> Strategy
        Strategy -- open/close signal --> Trade

        end
        subgraph Brokerage

            Portfolio[(Portfolio)] -- current positions --> Strategy
            RealtimeData[(RealtimeData)] --> Strategy
            API
        end
            Trade --> API
    end
```

## General Practice
Currently, we are working on developing a bot that will run on your local machine. 
The hope is to easily add complicated or simple trading strategies with code to mimic all of the ones youtubers use as clickbait.
With this software, we are able to backtest their strats for years at a time across several different cryptos and implement the strategy on a live Crypto Bot. 
