from datetime import datetime
import requests
from bs4 import BeautifulSoup


def get_stock_monthly(stock_id,
                      date_month=datetime.now().strftime("%Y/%m"),
                      **kw):
    """ Get stock value from 台灣證券交易所 
        
    Args: 
        date_month: datetime, it will change to "YYYYMMDD"    
    """

    date_month = (datetime.strptime(date_month, "%Y-%m").
                  strftime("%Y%m%d"))

    url_pattern = ("http://www.twse.com.tw/exchangeReport/STOCK_DAY?"
                   "response=json&"
                   "date={}&"
                   "stockNo={}").format(date_month, stock_id)
    print(url_pattern)
    json = requests.get(url=url_pattern).json()

    # transform data format
    data = json['data']
    result = []
    for _ in data:
        _m = int(_[0][0:3]) + 1911
        date = datetime.strptime("{}{}".format(_m, _[0][3:]),
                                 "%Y/%m/%d")
        result.append([date,  # 日期
                       float(_[1].replace(",", "")),  # 成交股數
                       float(_[2].replace(",", "")),  # 成交金額
                       float(_[3].replace(",", "")),  # 開盤價
                       float(_[4].replace(",", "")),  # 最高價
                       float(_[5].replace(",", "")),  # 最低價
                       float(_[6].replace(",", "")),  # 收盤價
                       float(_[7].replace("+", "").replace("X", "")),  # 漲跌價差
                       float(_[8].replace(",", "")),  # 成交筆數
                       ])
    return result


def get_taiex(date_month=datetime.now().strftime("%Y-%m"),
              **kw):
    """ Get taiex from 台灣證券交易所 

    Args: 
        date_month: datetime, it will change to "YYYYMMDD"    
    """

    date_month = (datetime.strptime(date_month, "%Y-%m").
                  strftime("%Y%m%d"))

    url_pattern = ("http://www.twse.com.tw/exchangeReport/FMTQIK?"
                   "response=json&"
                   "date={}").format(date_month)

    json = requests.get(url=url_pattern).json()

    # transform data format
    data = json['data']
    result = []
    for _ in data:
        _m = int(_[0][0:3]) + 1911
        date = datetime.strptime("{}{}".format(_m, _[0][3:]),
                                 "%Y/%m/%d")
        result.append([date,  # 日期
                       float(_[1].replace(",", "")),  # 成交股數
                       float(_[2].replace(",", "")),  # 成交金額
                       float(_[3].replace(",", "")),  # 成交筆數
                       float(_[4].replace(",", "")),  # 發行量加權股價指數
                       float(_[5].replace(",", "")),  # 漲跌點數
                       ])
    return result


def get_institutional_investors(stock_id,
                                date_month=datetime.now().strftime("%Y/%m"),
                                **kw):
    """ Get Institutional investors from 聚財網 

    Args: 
        date_month: datetime, it will change to "YYYYMMDD"    
    """

    date_month = datetime.strptime(date_month,
                                   "%Y-%m")

    url_pattern = ("https://stock.wearn.com/netbuy.asp?"
                   "Year={}&"
                   "month={}&"
                   "kind={}").format(int(date_month.strftime("%Y")) - 1911,
                                     int(date_month.strftime("%m")),
                                     stock_id)

    page = requests.get(url_pattern)
    soup = BeautifulSoup(page.text, 'html.parser')
    data = soup.select("div.stockalllist > table > tr")

    result = []

    def _clear(st):
        st = (st.replace("\xad", "").
              replace("\xa0", "").
              replace("\r", "").
              replace(",", ""))
        return st

    for i, _ in enumerate(data, start=2):
        try:
            _ds = _.text.split("\n")
            _date = int(_clear(_ds[1][:3])) + 1911
            _d = [datetime.strptime("{}{}".format(_date,
                                                  _ds[1][3:]),
                                    "%Y/%m/%d"),  # 日期
                  float(_clear(_ds[2])),  # 投信
                  float(_clear(_ds[3])),  # 自營商
                  float(_clear(_ds[4])),  # 外資
                  ]
            result.append(_d)
        except Exception as e:
            pass
    return result


def get_foreign_investor(stock_id,
                         date_month=datetime.now().strftime("%Y-%m"),
                         **kw):
    """ Get Foreign Investor from 聚財網 

    Args: 
        date_month: datetime, it will change to "YYYYMMDD"    
    """

    date_month = datetime.strptime(date_month,
                                   "%Y-%m")

    url_pattern = ("https://stock.wearn.com/foreign.asp?"
                   "Year={}&"
                   "month={}&"
                   "kind={}").format(int(date_month.strftime("%Y")) - 1911,
                                     int(date_month.strftime("%m")),
                                     stock_id)

    page = requests.get(url_pattern)
    soup = BeautifulSoup(page.text, 'html.parser')
    data = soup.select("div.stockalllist > table > tr")
    result = []

    def _clear(st):
        st = (st.replace("\xad", "").
              replace("\xa0", "").
              replace("\r", "").
              replace(",", "").
              replace(" ", "").
              replace("%", ""))
        return st

    for i, _ in enumerate(data, start=2):
        try:
            _ds = _.text.split("\n")
            _date = int(_clear(_ds[1][:3])) + 1911
            _d = [datetime.strptime("{}{}".format(_date,
                                                  _ds[1][3:]),
                                    "%Y/%m/%d"),  # 日期
                  float(_clear(_ds[3])),  # 持股比率
                  float(_clear(_ds[4])),  # 持有張數
                  float(_clear(_ds[5])),  # 當日增減
                  ]
            result.append(_d)
        except Exception as e:
            pass
    return result
