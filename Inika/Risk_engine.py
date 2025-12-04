import pandas as pd

claims=pd.read_csv('dealer_claims.csv')       #Dealers data of farmers
farmers=pd.read_csv('Gov_farmers.csv')        #Government data of farmers
dealers=pd.read_csv('Gov_dealers.csv')        #Government data of dealers

df=claims.merge(farmers, how='left', on='farmer_id')
df=df.merge(dealers, how='left', on='dealer_id')
velocity = df.groupby(['Dealer_ID','Date']).size() 

score=0 #Initialise risk score to zero

def identity_risk(farmer_name, dealer_name):  #identity risk detection
    if pd.isna(farmer_name): #if farmer name not present in govt records
        score+=60
    if pd.isna(dealer_name): #if dealer name not present in govt records
        score+=40
    return score

def quantity_risk(fertiliser,land): #quantity risk detection

def location_risk(farmer_location, dealer_location): #location risk detection
    if farmer_location != dealer_location: #if farmer and dealer locations do not match
        score+=20
    return score

def velocity_risk(dealer_id, date): #velocity risk detection
    if velocity[(dealer_id, date)] > 50: #if more than 50 claims from same dealer on same date
        score+=30
    elif velocity[(dealer_id, date)] > 20:  
        score+=10
    return score



