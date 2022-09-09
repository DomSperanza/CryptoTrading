# Algorithmic Trading
This is the start of a project where we make a bot that will automatically buy and sell crypto for us. 

---

For updating requirements.txt, use:
```
pip install pipreqs
pipreqs . --force --ignore **/Archive
```
More info: https://github.com/bndr/pipreqs

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
        subgraph Binance

            Portfolio[(Portfolio)] -- current positions --> Strategy
            RealtimeData[(RealtimeData)] --> Strategy
            BinanceAPI
        end
            Trade --> BinanceAPI
    end
```