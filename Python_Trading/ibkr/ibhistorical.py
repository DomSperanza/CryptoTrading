from ibdataapp import IBDataApp
import time
import pandas as pd

from ibcontract import IBContract


if __name__ == "__main__":

    app = IBDataApp("localhost", 7497, 0)

    time.sleep(2)

    # contract = IBContract("SPY")
    contract = IBContract("BTC")


    # note Timezone
    dt_range = pd.date_range(start="20220328 23:59:59", end="20220328 23:59:59", freq="24H")
    # dt_range = pd.date_range(start="20220328 23:59:59", end="20220401 23:59:59", freq="24H")

    for dt in dt_range[::-1]:
        reqId = app.request_historical_data(
            reqId=1001,
            contract=contract,
            # TIMEZONE USED
            endDateTime=dt.strftime("%Y%m%d %H:%M:%S")+ " America/Los_Angeles",
            barSizeSetting="1 min",
            durationStr="1 D",
            whatToShow="AGGTRADES",
            useRTH=1,
            formatDate=1,
            keepUpToDate=False
        )

        time.sleep(2)

    app.disconnect()

    df = app.data_to_dataframe()
    df.to_csv("data/my_historical_data.csv", mode="w")