import asyncio
from time import sleep
from datetime import datetime, timedelta

import aiohttp


class AllertApp:
    '''
    God-object app.
    It get real-time quotes
    Calculates own-Etherium price (without correlation with BTC)
    Allert if given condition satisfied
    '''

    def __init__(self, api_url: str, payload_btc: dict, payload_eth: dict,
                 api_request_frequency: int=1):
        self.api_url = api_url
        self.payload_btc = payload_btc
        self.payload_eth = payload_eth
        self.api_request_frequency = api_request_frequency
        self.quote_table = list()
        self.max_eth_adjusted_quote = dict()
        self.min_eth_adjusted_quote = dict()

    async def request_quote(self, payload: dict) -> list | int:
        '''
        Getting quotes as response from request through API,
        HTTP-method == GET
        '''
        async with aiohttp.ClientSession() as session:
            async with session.get(url=self.api_url, params=payload) as response:
                if response.status == 200:
                    response_text = await response.text()
                    currency = payload['fsym'] + 'USDT'
                    value = float(response_text[8:-1])
                    return {currency: value}
                else:
                    return response.status

    def fill_quote_table(self, quotes: list) -> None:
        '''
        Because of async request to the api,
        (response sequence) could differs of the (request sequnece)
        but we have no any problems due to that as we use dictionary for storing response
        with outer list which indexing feature we utilize in other functions
        '''
        try:
            self.quote_table.append({'time': datetime.now(), **quotes[0], **quotes[1], })
        except TypeError:
            print(f'API server error codes: {set(quotes)}')

    def adjust_eth_price(self) -> None:
        '''
        1) Reads last entry in self.quote_table which looks like
        {
            'time': datetime.datetime(2023, 2, 20, 12, 21, 8, 858646),
            'BTCUSDT': 24436.9,
            'ETHUSDT': 1698.61,
            }
        2) Calculates adjusted price subtracting BTC influence with
        correlation coefficient from the article
        https://fsr-develop.ru/korrelyaciya-kriptovaljut
        equal to 0.5
        3) Modify that last entry, adding adjusted ETH price
        '''
        # 1)
        quotes = self.quote_table[-1]
        btc_price = quotes['BTCUSDT']
        eth_price = quotes['ETHUSDT']
        try:
            previous_quotes = self.quote_table[-1]
            previous_btc_price = quotes['BTCUSDT']
            previous_eth_price = quotes['ETHUSDT']
        except IndexError:
            previous_quotes = quotes
            previous_btc_price = btc_price
            previous_eth_price = eth_price

        # 2)
        correlation_coef = .5
        price_movement_delta = btc_price - previous_btc_price
        price_ratio = eth_price / btc_price
        price_correction = price_movement_delta * price_ratio * correlation_coef

        adjusted_eth_price = eth_price - price_correction

        # 3)
        self.quote_table[-1]['ETH_adjusted'] = adjusted_eth_price

    def get_last_hour_max_quotes(self) -> None:
        '''
        max quote for last 60 minutes
        1) for very first call of this function
        2) when self.max_eth_adjusted_quote is not expired (were less than 60 minutes ago)
        3) when self.max_eth_adjusted_quote is     expired (were more than 60 minutes ago)
        '''
        # 1)
        if len(self.max_eth_adjusted_quote) == 0:
            self.max_eth_adjusted_quote['time'] = self.quote_table[-1]['time']
            self.max_eth_adjusted_quote['price'] = self.quote_table[-1]['ETH_adjusted']

        # 2)
        elif ((datetime.now() - self.max_eth_adjusted_quote['time']) <= timedelta(minutes=60)):
            max_quote = max(self.max_eth_adjusted_quote['price'],
                            self.quote_table[-1]['ETH_adjusted'])
            if max_quote != self.max_eth_adjusted_quote['price']:
                self.max_eth_adjusted_quote['time'] = self.quote_table[-1]['time']
                self.max_eth_adjusted_quote['price'] = max_quote
        # 3)
        else:
            # creating list of quotes gained no more than 60 minutes ago
            quotes = []
            for quote in reversed(self.quote_table):
                if (datetime.now() - quote['time']) <= timedelta(minutes=60):
                    quotes.append(quote)
                else:
                    break
            max_quote = max(quotes, key=lambda quote: quote['ETH_adjusted'])
            if max_quote != self.max_eth_adjusted_quote['price']:
                self.max_eth_adjusted_quote['time'] = self.quote_table[-1]['time']
                self.max_eth_adjusted_quote['price'] = max_quote

    def get_last_hour_min_quotes(self) -> None:
        '''
        min quote for last 60 minutes
        1) for very first call of this function
        2) when self.min_eth_adjusted_quote is not expired (were less than 60 minutes ago)
        3) when self.min_eth_adjusted_quote is     expired (were more than 60 minutes ago)
        '''
        # 1)
        if len(self.min_eth_adjusted_quote) == 0:
            self.min_eth_adjusted_quote['time'] = self.quote_table[-1]['time']
            self.min_eth_adjusted_quote['price'] = self.quote_table[-1]['ETH_adjusted']

        # 2)
        elif ((datetime.now() - self.min_eth_adjusted_quote['time']) <= timedelta(minutes=60)):
            min_quote = min(self.min_eth_adjusted_quote['price'],
                            self.quote_table[-1]['ETH_adjusted'])
            if min_quote != self.min_eth_adjusted_quote['price']:
                self.min_eth_adjusted_quote['time'] = self.quote_table[-1]['time']
                self.min_eth_adjusted_quote['price'] = min_quote
        # 3)
        else:
            # creating list of quotes gained no more than 60 minutes ago
            quotes = []
            for quote in reversed(self.quote_table):
                if (datetime.now() - quote['time']) <= timedelta(minutes=60):
                    quotes.append(quote)
                else:
                    break
            min_quote = min(quotes, key=lambda quote: quote['ETH_adjusted'])
            if min_quote != self.min_eth_adjusted_quote['price']:
                self.min_eth_adjusted_quote['time'] = self.quote_table[-1]['time']
                self.min_eth_adjusted_quote['price'] = min_quote

    def alert(self, alert_ratio: float=1.01) -> str:
        '''
        retutn a warning message or an empty string, depending on
        whether or not the conditions have satisfied
        '''
        ratio = self.max_eth_adjusted_quote['price'] / self.min_eth_adjusted_quote['price']
        if ratio >= alert_ratio:
            percent_change = 100 * (ratio - 1)
            return f'Alert! price have changed by {percent_change:.2f}% '
        else:
            return ''

    async def run(self) -> None:
        '''
        main-loop process "procedure"
        '''
        while True:
            tasks = [asyncio.create_task(self.request_quote(self.payload_btc)),
                     asyncio.create_task(self.request_quote(self.payload_eth)), ]
            quotes = await asyncio.gather(*tasks)
            self.fill_quote_table(quotes)
            self.adjust_eth_price()
            self.get_last_hour_max_quotes()
            self.get_last_hour_min_quotes()
            alert_msg = self.alert()
            print(f"{alert_msg}"
                  f"ETH_adjusted_price={self.quote_table[-1]['ETH_adjusted']}, "
                  f"min={self.min_eth_adjusted_quote['price']}, "
                  f"max={self.max_eth_adjusted_quote['price']}", end='\r')
            sleep(self.api_request_frequency)


if __name__ == '__main__':

    API_URL = 'https://min-api.cryptocompare.com/data/price'
    payload_BTC = {'fsym': 'BTC', 'tsyms': 'USDT'}
    payload_ETH = {'fsym': 'ETH', 'tsyms': 'USDT'}

    app = AllertApp(API_URL, payload_BTC, payload_ETH)

    asyncio.run(app.run())
