import requests
from io import StringIO
import pandas as pd
import numpy as np
import time
import matplotlib
import matplotlib.pyplot as plt


class StockMarket(object):
    
    def __init__(self):
        self.day_fields = ('證券代號', '證券名稱', '成交股數', '成交筆數', '成交金額',
                           '開盤價', '最高價', '最低價', '收盤價', '漲跌(+ / -)',
                           '漲跌價差', '最後揭示買價', '最後揭示買量', '最後揭示賣價', '最後揭示賣量',
                           '本益比')
        self.month_fields = ('公司代號', '公司名稱', '當月營收', '上月營收', '去年當月營收',
                             '上月比較增減(%)', '去年同月增減(%)', '當月累計營收', '去年累計營收', '前期比較增減(%)')

        # 偽瀏覽器
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit \
                          /537.36 (KHTML, like Gecko) Chrome/ 39.0.2171.95 Safari / 537.36'}
        self.day_filter = []
        self.month_filter = []

    def day_stock(self, day):
        url = 'http://www.twse.com.tw/exchangeReport/MI_INDEX?response=csv&date=' + str(day) + '&type=ALL'
        r = requests.post(url, self.headers)
        df = pd.read_csv(StringIO("\n".join([i.translate({ord(c): None for c in ' '})
                                             for i in r.text.split('\n')
                                             if len(i.split('",')) == 17 and i[0] != '='])), header=0)
        return df

    def month_stock_steam(self, t_month):
        year = t_month[0]
        month = t_month[1]
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
        html_df = pd.read_html(StringIO(r.text))
        # 處理一下資料
        if html_df[0].shape[0] > 500:
            df = html_df[0].copy()
        else:
            df = pd.concat([df for df in html_df if df.shape[1] <= 11])
        return df

    def month_stock(self, t_month):
        month_df = self.month_stock_steam(t_month)

        m_df = month_df.copy()
        m_df = m_df[list(range(10))]

        column_index = m_df.index[(m_df[0] == '公司代號')][0]
        # print('column_index', column_index, m_df.index[(m_df[0] == '公司代號')])
        m_df.columns = m_df.iloc[column_index]
        # print(m_df.columns)
        m_df['當月營收'] = pd.to_numeric(m_df['當月營收'], 'coerce')
        # print(m_df['當月營收'])
        # remove dummy data
        m_df = m_df[~m_df['當月營收'].isnull()]
        # print(m_df.head())
        m_df = m_df[m_df['公司代號'] != '合計']
        # 偽停頓
        time.sleep(5)
        return m_df

    @staticmethod
    def filter_df(i_df, c_filter):
        # print('c_filter', c_filter)
        field = c_filter[0]
        operator = c_filter[1]
        value = c_filter[2]
        if operator == '==':
            selected_df = i_df[pd.to_numeric(i_df[field], errors='coerce') == value]
        elif operator == '!=':
            selected_df = i_df[pd.to_numeric(i_df[field], errors='coerce') != value]
        elif operator == '>':
            selected_df = i_df[pd.to_numeric(i_df[field], errors='coerce') > value]
        elif operator == '<':
            selected_df = i_df[pd.to_numeric(i_df[field], errors='coerce') < value]
        elif operator == '<=':
            selected_df = i_df[pd.to_numeric(i_df[field], errors='coerce') <= value]
        elif operator == '>=':
            selected_df = i_df[pd.to_numeric(i_df[field], errors='coerce') >= value]
        else:
            selected_df = i_df
            print('filter_df: wrong parameter !!!')
        return selected_df

    def day_stock_filter_report(self, day):
        day_df = self.day_stock(day)
        s_df = day_df.copy()
        if self.day_filter:
            for i in range(0, len(self.day_filter), 3):
                s_df = StockMarket.filter_df(s_df, self.day_filter[i:i+3])
        s_df.to_excel(str(day) + '_day_stock_filter_report.xls', encoding='utf-8', index=False)
        return s_df

    def month_stock_filter_report(self, t_month):
        month_df = self.month_stock(t_month)
        s_df = month_df.copy()
        if self.month_filter:
            for i in range(0, len(self.month_filter), 3):
                s_df = StockMarket.filter_df(s_df, self.month_filter[i:i+3])
        s_df.to_excel(str(t_month[0]) + '_' + str(t_month[1]) + '_month_stock_filter_report.xls', encoding='utf-8',
                      index=False)
        return s_df

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
    target_day = 20130201
    target_month = [2013, 2]

    # Deal with daily stock
    d_stock = s.day_stock(target_day)
    d_stock.to_excel(str(target_day) + '_day_stock.xls', encoding='utf-8', index=False)

    s.day_filter = ['本益比', '<', 15, '本益比', '!=', 0, '開盤價', '<', 15]
    print('day_filter:', s.day_filter)
    s.day_stock_filter_report(target_day)

    # Deal with monthly stock
    m_stock = s.month_stock(target_month)
    m_stock.to_excel(str(target_month[0]) + '_' + str(target_month[1]) + '_month_stock.xls', encoding='utf-8',
                     index=False)

    s.month_filter = ['上月比較增減(%)', '>', 0, '前期比較增減(%)', '>', 0]
    print('month_filter:', s.month_filter)
    s.month_stock_filter_report(target_month)

#    df = s.financial_statement(2018, 1, '營益分析彙總表')
    # delete one column
#    df = df.drop(['合計：共 884 家'], axis=1)
    # index change to company name
#    df = df.set_index(['公司名稱'])
#    print(df)
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
