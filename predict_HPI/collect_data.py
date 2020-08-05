import quandl
import pandas as pd
import pickle
from matplotlib import pyplot as plt
from matplotlib import style
style.use('fivethirtyeight')

api_key = open('quandlapikey.txt', 'r').readline().rstrip('\n')
def state_list():
    fiddy_states = pd.read_html('https://simple.wikipedia.org/wiki/List_of_U.S._states')
    return fiddy_states[0]['Name &postal abbreviation[1]']['Name &postal abbreviation[1].1']
    #print(fiddy_states[0]['Name &postal abbreviation[1]']['Name &postal abbreviation[1].1'][0])

def grab_initial_data():
    main_df = pd.DataFrame()
    print("Collecting states ...    ")
    states = state_list()
    print("Got the states! ")
    for abbv in states:
        query = "FMAC/HPI_"+str(abbv)
        print(query)
        df = quandl.get(query,trim_start="1990-01-31", authtoken=api_key)

        df.rename(columns={'NSA Value' : str(abbv)}, inplace=True) #similarly extracting SA data
        df[str(abbv)] = ((df[str(abbv)] - df[str(abbv)][0])/df[str(abbv)][0])*100.0
        if main_df.empty:
            main_df = df[[str(abbv)]]
        else:
            main_df = main_df.join(df[[str(abbv)]])

    pickle_out = open('NSA_pct_change.pickle', 'wb')
    pickle.dump(main_df, pickle_out)
    pickle_out.close()

def HPI_Benchmark():
    df = quandl.get("FMAC/HPI_USA",trim_start="1990-01-31", authtoken=api_key)
    df.rename(columns={'SA Value': 'USA'}, inplace=True)
    df['USA'] = ((df['USA'] - df['USA'][0])/df['USA'][0])*100.0
    out = open('benchmark_NSA.pickle', 'wb')
    pickle.dump(df[['USA']], out)
    out.close()

def mortgage_30y():
    df = quandl.get("FMAC/MORTG",trim_start="1990-01-01", authtoken=api_key)
    df["Value"] = ((df["Value"] - df["Value"][0])/df["Value"][0])*100.0
    df = df.resample('M').mean()
    df.columns = ['M30']
    pickle_out = open('mortgage_30y.pickle', 'wb')
    pickle.dump(df, pickle_out)
    pickle_out.close()

def resize_df(df, size):
    df.reset_index(inplace=True)
    for column in df.columns:
        df[column] = df[column][:size]
    df.dropna(how='all', inplace=True)
    df.set_index('Date', inplace=True)
    return df

def resize_series(series, size):
    df = pd.DataFrame(series)
    df = resize_df(df, size)
    first_col = df.columns[0]
    return df[first_col]

def sp500_data():
    df = pd.read_csv('sp500.csv')
    df['Date']=pd.to_datetime(df['Date'])
    df.set_index('Date', inplace=True)
    df["Adj Close"] = (df["Adj Close"]-df["Adj Close"][0]) / df["Adj Close"][0] * 100.0
    df=df.resample('M').mean()
    df.rename(columns={'Adj Close':'sp500'}, inplace=True)
    df = df["sp500"]
    return df

def gdp_data():
    df = quandl.get("BCB/4385", trim_start="1990-01-01", authtoken=api_key)
    df["Value"] = (df["Value"]-df["Value"][0]) / df["Value"][0] * 100.0
    df=df.resample('M').mean()
    df.rename(columns={'Value':'GDP'}, inplace=True)
    df = df['GDP']
    pickle_out = open('GDP.pickle', 'wb')
    pickle.dump(df, pickle_out)
    pickle_out.close()

def us_unemployment():
    df = quandl.get("USMISERY/INDEX", trim_start="1990-01-01", authtoken=api_key)
    df["Unemployment Rate"] = (df["Unemployment Rate"]-df["Unemployment Rate"][0]) / df["Unemployment Rate"][0] * 100.0
    df = df['Unemployment Rate']
    pickle_out = open('us_unemployment.pickle', 'wb')
    pickle.dump(df, pickle_out)
    pickle_out.close()


#mortgage_30y()
#grab_initial_data()
#HPI_Benchmark()
#gdp_data()
#us_unemployment()

sp500 = sp500_data()
unemployment = pd.read_pickle('us_unemployment.pickle')
gdp = pd.read_pickle('GDP.pickle')
m30 = pd.read_pickle('mortgage_30y.pickle')
HPI_data = pd.read_pickle('NSA_pct_change.pickle')
HPI_bench = pd.read_pickle('benchmark_NSA.pickle')

gdp = resize_series(gdp, m30.shape[0])
unemployment = resize_series(unemployment, m30.shape[0])
HPI_data = resize_df(HPI_data, m30.shape[0])
HPI_bench = resize_df(HPI_bench, m30.shape[0])

HPI = HPI_data.join([m30, unemployment, gdp, sp500, HPI_bench])
print(HPI)
print(HPI.corr())

HPI.to_pickle('HPI.pickle')
