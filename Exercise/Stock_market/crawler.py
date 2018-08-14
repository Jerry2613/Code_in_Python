import requests
from io import StringIO
import pandas as pd
import numpy as np
import time
import matplotlib
import matplotlib.pyplot as plt


class StockMarket(object):
    
    def __init__(self):
        self.fields = ('證券代號', '證券名稱', '成交股數', '成交筆數', '成交金額',
                       '開盤價', '最高價', '最低價', '收盤價', '漲跌(+ / -)',
                       '漲跌價差', '最後揭示買價', '最後揭示買量', '最後揭示賣價', '最後揭示賣量',
                       '本益比')
        # 偽瀏覽器
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit \
                          /537.36 (KHTML, like Gecko) Chrome/ 39.0.2171.95 Safari / 537.36'}
        self.day_filter = []

    def day_stock(self, target_date):
        r = requests.post('http://www.twse.com.tw/exchangeReport/MI_INDEX?response=csv&date=' + str(target_date)
                          + '&type=ALL')
        df = pd.read_csv(StringIO("\n".join([i.translate({ord(c): None for c in ' '})
                                             for i in r.text.split('\n')
                                             if len(i.split('",')) == 17 and i[0] != '='])), header=0)
        return df

    def month_stock(self, year, month):
        # 假如是西元，轉成民國
        if year > 1990:
            year -= 1911
        # 上櫃: sii change to otc
        url = 'http://mops.twse.com.tw/nas/t21/sii/t21sc03_' + str(year) + '_' + str(month) + '_0.html'
        if year <= 98:
            url = 'http://mops.twse.com.tw/nas/t21/sii/t21sc03_' + str(year) + '_' + str(month) + '.html'

        # 下載該年月的網站，並用pandas轉換成 dataframe
        r = requests.get(url, self.headers)
        r.encoding = 'big5'
        return pd.read_html(StringIO(r.text))

    @staticmethod
    def filter_df(input_df, field, operator, value):
        selected_df = input_df
        if operator == '==':
            selected_df = input_df[pd.to_numeric(input_df[field], errors='coerce') == value]
        elif operator == '!=':
            selected_df = input_df[pd.to_numeric(input_df[field], errors='coerce') != value]
        elif operator == '>':
            selected_df = input_df[pd.to_numeric(input_df[field], errors='coerce') > value]
        elif operator == '<':
            selected_df = input_df[pd.to_numeric(input_df[field], errors='coerce') < value]
        elif operator == '<=':
            selected_df = input_df[pd.to_numeric(input_df[field], errors='coerce') <= value]
        elif operator == '>=':
            selected_df = input_df[pd.to_numeric(input_df[field], errors='coerce') >= value]
        else:
            print('filter_df: wrong parameter !!!')
        return selected_df

    @staticmethod
    def save_excel_file(data_frame, file_name):
        # data_frame.to_csv(file_name + '.csv', encoding='utf-8', index=False)
        data_frame.to_excel(file_name + '.xls', encoding='utf-8', index=False)

    def day_report(self, day, day_filter):
        print(day_filter)
        df = self.day_stock(day)
        if day_filter is not []:
            for i in range(0, len(day_filter), 3):
                df = StockMarket.filter_df(df, self.fields[day_filter[i]], day_filter[i+1], day_filter[i+2])
                print(df.shape)
        StockMarket.save_excel_file(df, str(day) + '_day_report')
        return df

    def monthly_report(self, year, month):
        html_df = self.month_stock(year, month)
     #   StockMarket.save_excel_file(html_df, 'First')
     #   StockMarket.save_excel_file(html_df[0], 'Second')

        # 處理一下資料
        if html_df[0].shape[0] > 500:
            df = html_df[0].copy()
            print('E')
        else:
            df = pd.concat([df for df in html_df if df.shape[1] <= 11])
            print('F')
        # use a list to contain multiple columns
        df = df[list(range(0, 10))]
        column_index = df.index[(df[0] == '公司代號')][0]
        df.columns = df.iloc[column_index]
        df['當月營收'] = pd.to_numeric(df['當月營收'], 'coerce')
        df = df[~df['當月營收'].isnull()]
        df = df[df['公司代號'] != '合計']
        StockMarket.save_excel_file(df, str(year) + '_' + str(month) + '_month_report')
        # 偽停頓
        time.sleep(5)
        return df

    def financial_statement(self, year, season, type='綜合損益彙總表'):
        if year >= 1000:
            year -= 1911

        if type == '綜合損益彙總表':
            url = 'http://mops.twse.com.tw/mops/web/ajax_t163sb04'
        elif type == '資產負債彙總表':
            url = 'http://mops.twse.com.tw/mops/web/ajax_t163sb05'
        elif type == '營益分析彙總表':
            url = 'http://mops.twse.com.tw/mops/web/ajax_t163sb06'
        else:
            print('type does not match')

        r = requests.post(url, {
            'encodeURIComponent': 1,
            'step': 1,
            'firstin': 1,
            'off': 1,
            'TYPEK': 'sii',
            'year': str(year),
            'season': str(season),
        })

        r.encoding = 'utf8'
        dfs = pd.read_html(r.text)

        for i, df in enumerate(dfs):
            df.columns = df.iloc[0]
            dfs[i] = df.iloc[1:]

        df = pd.concat(dfs).applymap(lambda x: x if x != '--' else np.nan)
        df = df[df['公司代號'] != '公司代號']
        df = df[~df['公司代號'].isnull()]
        return df


if __name__ == '__main__':
    s = StockMarket()
    s.day_filter = [15, '<', 15, 15, '!=', 0, 5, '<', 15]
    s.day_report(20180322, s.day_filter)
    s.monthly_report(2018, 1)

#    df = s.financial_statement(2018, 1, '營益分析彙總表')
    # delete one column
#    df = df.drop(['合計：共 884 家'], axis=1)
    # index change to company name
#    df = df.set_index(['公司名稱'])
#    print(df)
#    s.save_excel_file(df, 'Quarter_report')
    # 轉換成數值
#    df = df.astype(float)
    # 三件事情寫成一行
    #df = df.drop(['合計：共 808 家'], axis=1).set_index(['公司名稱']).astype(float)
    # 單選出毛利率
#    df['毛利率(%)(營業毛利)/(營業收入)']
    # 取得台積電資料
#    df.loc['台積電']
    # 取得TSMC跟MTK的資料
#    df.loc[['台積電', '聯發科']]
    # 數值分析
#    df.describe()
    # 毛利率分佈圖
    # 注意：既然是IPython的内置magic函数，那么在Pycharm中是不会支持的。
    # ％matplotlib inline
#    plt.plot([1, 2, 3])
#    plt.ylabel('some numbers')
#    plt.show()
   # df['毛利率(%)(營業毛利)/(營業收入)'].hist(bins=range(-100, 100))
    # 選股
#    cond1 = df['毛利率(%)(營業毛利)/(營業收入)'].astype(float) > 20
#    cond2 = df['營業利益率(%)(營業利益)/(營業收入)'].astype(float) > 5
#    df[cond1 & cond2]