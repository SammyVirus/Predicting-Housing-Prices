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
        df = quandl.get(query, authtoken=api_key)

        df.rename(columns={'NSA Value' : str(abbv)}, inplace=True) #similarly extracting SA data
        df[str(abbv)] = ((df[str(abbv)] - df[str(abbv)][0])/df[str(abbv)][0])*100.0
        if main_df.empty:
            main_df = df[[str(abbv)]]
        else:
            main_df = main_df.join(df[[str(abbv)]])
    print(main_df.head())

    pickle_out = open('NSA_pct_change.pickle', 'wb')
    pickle.dump(main_df, pickle_out)
    pickle_out.close()

def HPI_Benchmark():
    df = quandl.get("FMAC/HPI_USA", authtoken=api_key)
    df.rename(columns={'SA Value': 'USA'}, inplace=True)
    df['USA'] = ((df['USA'] - df['USA'][0])/df['USA'][0])*100.0
    out = open('benchmark_NSA.pickle', 'wb')
    pickle.dump(df[['USA']], out)
    out.close()
#grab_initial_data()
#HPI_Benchmark()

fig = plt.figure()
ax1 = plt.subplot2grid((1, 1), (0, 0))

HPI_data = pd.read_pickle('NSA_pct_change.pickle')
#benchmark = pd.read_pickle('benchmark_NSA.pickle')
HPI_data['TX1yr'] = HPI_data['TX'].resample('A').mean()
print(HPI_data[['TX', 'TX1yr']].head())
#HPI_data.dropna(inplace=True, how='all')
HPI_data.fillna(method='ffill', inplace=True)
print(HPI_data[['TX', 'TX1yr']].head())
print(HPI_data.isnull().values.sum())

HPI_data[['TX', 'TX1yr']].plot(ax=ax1, label='Monthly TX HPI')
#benchmark.plot(ax=ax1,color='k', linewidth=10)
plt.legend(loc=4)
plt.show()

#HPI_state_Correlation = HPI_data.corr()
#print(HPI_state_Correlation)
#print(HPI_state_Correlation.describe())
