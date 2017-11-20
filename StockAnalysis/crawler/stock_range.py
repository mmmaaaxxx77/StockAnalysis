import pickle
from datetime import (datetime, timedelta)
import sys, os
from time import sleep

import pandas as pd
from pandas.tseries.offsets import BDay
from sklearn.ensemble import RandomForestClassifier
from sklearn.grid_search import GridSearchCV
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

sys.path.insert(1, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from crawler import stock_value as st


class StockValue:
    def __init__(self, **kw):
        self.date = kw.pop("date")

        self.business_day_num = 0

        self.val1 = 0  # 成交股數
        self.val2 = 0  # 成交金額
        self.val3 = 0  # 開盤價
        self.val4 = 0  # 最高價
        self.val5 = 0  # 最低價
        self.val6 = 0  # 收盤價
        self.val7 = 0  # 漲跌價差
        self.val8 = 0  # 成交筆數

        # 大盤加權指數
        self.taiex1 = 0  # 成交股數
        self.taiex2 = 0  # 成交金額
        self.taiex3 = 0  # 成交筆數
        self.taiex4 = 0  # 發行量加權股價指數
        self.taiex5 = 0  # 漲跌點數

        # 三大法人
        self.ii1 = 0  # 投信
        self.ii2 = 0  # 自營商
        self.ii3 = 0  # 外資

        # 外資
        self.fi1 = 0  # 持股比率
        self.fi2 = 0  # 持有張數
        self.fi3 = 0  # 當日增減

    def set_value(self, *args):
        self.val1 = args[0]  # 成交股數
        self.val2 = args[1]  # 成交金額
        self.val3 = args[2]  # 開盤價
        self.val4 = args[3]  # 最高價
        self.val5 = args[4]  # 最低價
        self.val6 = args[5]  # 收盤價
        self.val7 = args[6]  # 漲跌價差
        self.val8 = args[7]  # 成交筆數

    def set_taiex(self, *args):
        self.taiex1 = args[0]  # 成交股數
        self.taiex2 = args[1]  # 成交金額
        self.taiex3 = args[2]  # 成交筆數
        self.taiex4 = args[3]  # 發行量加權股價指數
        self.taiex5 = args[4]  # 漲跌點數

    def set_institutional_investors(self, *args):
        self.ii1 = args[0]  # 投信
        self.ii2 = args[1]  # 自營商
        self.ii3 = args[2]  # 外資

    def set_foreign_investor(self, *args):
        self.fi1 = args[0]  # 持股比率
        self.fi2 = args[1]  # 持有張數
        self.fi3 = args[2]  # 當日增減

    def is_same_date(self, date):
        return self.date.strftime("%Y-%m-%d") == date.strftime("%Y-%m-%d")

    def __str__(self):
        return ("({}, {}, "
                "{}, {}, {}, {}, {}, {}, {}, {}, "
                "{}, {}, {}, {}, {}, "
                "{}, {}, {}, "
                "{}, {}, {})".
                format(self.date,
                       self.business_day_num,
                       self.val1,
                       self.val2,
                       self.val3,
                       self.val4,
                       self.val5,
                       self.val6,
                       self.val7,
                       self.val8,
                       self.taiex1,
                       self.taiex2,
                       self.taiex3,
                       self.taiex4,
                       self.taiex5,
                       self.ii1,
                       self.ii2,
                       self.ii3,
                       self.fi1,
                       self.fi2,
                       self.fi3, )
                )

    def __repr__(self):
        return self.__str__()


def get_data(stock_id,
             start=(datetime.now() - timedelta(days=100)).strftime("%Y-%m-%d"),
             end=datetime.now().strftime("%Y-%m-%d")):
    """ Getting stock data from start to end """

    print("{} to {}".format(start, end))

    # Business day
    range_dates = pd.date_range(start,
                                end, )
    # freq=BDay())
    range_dates_s = ([_.strftime("%Y-%m-%d")
                      for _ in
                      range_dates
                      ])
    # months
    range_months = []
    for _d in range_dates:
        if _d.strftime("%Y-%m") not in range_months:
            range_months.append(_d.strftime("%Y-%m"))

    # stock value
    stock_value = []
    stock_value_day = []
    for _m in range_months:
        _value = st.get_stock_monthly(stock_id=stock_id,
                                      date_month=_m)
        for i, _v in enumerate(_value):
            if _v[0].strftime("%Y-%m-%d") not in stock_value_day:
                try:
                    stock = StockValue(date=_v[0])
                    # business day
                    stock.business_day_num = range_dates_s.index(_v[0].strftime("%Y-%m-%d"))
                    stock.set_value(*_v[1:])
                    stock_value.append(stock)
                    stock_value_day.append(_v[0].strftime("%Y-%m-%d"))
                except Exception as e:
                    print(e)
                    continue
        sleep(5)
        _taiex = st.get_taiex(date_month=_m)
        for _ta in _taiex:
            for _stv in stock_value:
                if _stv.is_same_date(_ta[0]):
                    _stv.set_taiex(*_ta[1:])

        sleep(3)
        _iis = st.get_institutional_investors(stock_id=stock_id,
                                              date_month=_m)
        for _ta in _iis:
            for _stv in stock_value:
                if _stv.is_same_date(_ta[0]):
                    _stv.set_institutional_investors(*_ta[1:])

        sleep(3)
        _iis = st.get_foreign_investor(stock_id=stock_id,
                                       date_month=_m)
        for _ta in _iis:
            for _stv in stock_value:
                if _stv.is_same_date(_ta[0]):
                    _stv.set_foreign_investor(*_ta[1:])

    return stock_value


def generator_train_data(data):
    _y = []
    _x = []

    NUM_DAY = 5

    for i, _ in enumerate(data):

        if i + NUM_DAY >= len(data):
            break

        # 後7天收盤價大於當天收盤價=1, or =0
        _first = _
        next_three = data[i + NUM_DAY]
        if _.val6 < next_three.val6:
            _y.append(1)
        elif _.val6 >= next_three.val6:
            _y.append(0)

        _x.append([
            _.business_day_num,
            _.val2,
            _.val6,
            _.taiex4,
            _.ii1,
            _.ii2,
            _.ii3,
            _.fi2,
        ])

    return _x, _y


def analysis():
    if not os.path.exists("data.pickle"):

        print("抓取訓練資料 2015")
        data2015 = get_data("2915", start="2015-01-01", end="2015-12-30")
        print("抓取訓練資料 2016")
        data2016 = get_data("2915", start="2016-01-01", end="2016-12-30")
        print("抓取訓練資料 2017")
        data2017 = get_data("2915", start="2017-01-01", end="2016-11-20")

        data = (data2015, data2016, data2017)

        fh = open("data.pickle", 'wb')
        pickle.dump(data, fh)
    else:
        fh = open("data.pickle", 'rb')
        data = pickle.load(fh)
        (data2015, data2016, data2017) = data
    x_train, y_train = generator_train_data(data2016 + data2017)
    x_test, y_test = generator_train_data(data2015)

    print("開始訓練")
    pipe = Pipeline([
        ('scl', StandardScaler()),
        # 隨機森林
        # ('forest', RandomForestClassifier(criterion='entropy', n_estimators=500, random_state=1, n_jobs=2))
        # SVM
        ('svm', SVC(random_state=0))
    ])

    pipe.fit(x_train, y_train)

    # GridSearchCV
    param_range = [0.0001, 0.001, 0.01, 0.1, 1.0, 10.0, 100.0]
    param_trees = [10, 50, 100, 300, 500, 700, 1000]
    """
    param_grid = [{
        'forest__criterion': ['entropy'],
        'forest__n_estimators': param_trees
    },
        {
            'forest__criterion': ['gini'],
            'forest__n_estimators': param_trees,
        }
    ]
    """
    param_grid = [{
        'svm__kernel': ['rbf', 'linear', 'sigmoid'],
        'svm__C': param_range,
        'svm__gamma': param_range
    }]
    gs = GridSearchCV(estimator=pipe,
                      param_grid=param_grid,
                      scoring='accuracy',
                      cv=10,
                      n_jobs=4)
    gs.fit(x_test, y_test)
    print(gs.best_score_)
    print(gs.best_params_)

    # 驗證 Model
    """
    scores = cross_val_score(estimator=pipe, X=x_test, y=y_test, cv=10, n_jobs=1)

    print("{:.2f} +/- {:.2f}".format(np.mean(scores), np.std(scores)))

    #score = pipe.score(x_test, y_test)

    #print("{:.2f}".format(score))
    """


analysis()
