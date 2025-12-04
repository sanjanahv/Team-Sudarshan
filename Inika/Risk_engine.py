import pandas as pd

claims=pd.read_csv('dealer_claims.csv')       #Dealers data of farmers
farmers=pd.read_csv('Gov_farmers.csv')        #Government data of farmers
dealers=pd.read_csv('Gov_dealers.csv')        #Government data of dealers

df=claims.merge(farmers, how='left', on='farmer_id')
df=df.merge(dealers, how='left', on='dealer_id')
velocity = df.groupby('dealer_id').agg({'claim_id':'count'}).reset_index()  


