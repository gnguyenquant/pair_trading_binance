import pandas as pd
a=[1,2,3,4]
b=[5,6,7,8]
c=[9,10,11,12]
df=pd.DataFrame([a,b,c])
df_2=df.transpose()
df_2.to_csv('asd.csv',header=False,index=False)
print(df_2)