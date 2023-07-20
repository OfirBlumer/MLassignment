# Imports

import pandas as pd

# Read original data

bouts = pd.read_csv("all_womens_foil_bout_data_May_13_2021_cleaned.csv")
bio = pd.read_csv("all_womens_foil_fencer_bio_data_May_13_2021_cleaned.csv")
rank = pd.read_csv("all_womens_foil_fencer_rankings_data_May_13_2021_cleaned.csv")

# Find the year of ranking data and country of origin for every fencer

year = []
for i in range(len(rank)):
    year.append(rank.loc[i].season[:4])
rank["year"] = year

# Find fencers ranks, countries of origin and fencing hances for each bout

fencer_age = []
opp_age = []
fencer_hand = []
opp_hand = []
score = []
fencer_rank = []
opp_rank = []
won = []
fencer_country = {}
opp_country = {}
for country in bio.country_code.drop_duplicates():
    fencer_country[country] = []
    opp_country[country] = []

print(len(bouts))
for i in range(len(bouts)):
    one = 0
    two = 0
    three = 0
    four = 0
    try:
        one = rank.loc[rank.id == bouts.loc[i].fencer_ID].loc[rank.year==bouts.loc[i].date[:4]]["rank"].values[0]
        two = rank.loc[rank.id == bouts.loc[i].opp_ID].loc[rank.year==bouts.loc[i].date[:4]]["rank"].values[0]
        three = rank.loc[rank.id == bouts.loc[i].opp_ID].loc[rank.year==bouts.loc[i].date[:4]]["rank"].values[0]
        four = rank.loc[rank.id == bouts.loc[i].fencer_ID].loc[rank.year==bouts.loc[i].date[:4]]["rank"].values[0]
    except:
        pass
    if one != 0 and two != 0 and three !=0 and four!=0:
        for country in bio.country_code.drop_duplicates():
            fencer_country[country].append((bio.loc[bio.id == bouts.loc[i].fencer_ID].country_code == country).values[0])
            fencer_country[country].append((bio.loc[bio.id == bouts.loc[i].opp_ID].country_code == country).values[0])
            opp_country[country].append((bio.loc[bio.id == bouts.loc[i].opp_ID].country_code == country).values[0])
            opp_country[country].append((bio.loc[bio.id == bouts.loc[i].fencer_ID].country_code == country).values[0])
            
        fencer_age.append(bouts.loc[i].fencer_age)
        fencer_age.append(bouts.loc[i].opp_age)
        opp_age.append(bouts.loc[i].opp_age)
        opp_age.append(bouts.loc[i].fencer_age)

        score.append(bouts.loc[i].fencer_score)
        score.append(bouts.loc[i].opp_score)
        
        won.append(bouts.loc[i].fencer_score>bouts.loc[i].opp_score)
        won.append(bouts.loc[i].opp_score>bouts.loc[i].fencer_score)    

        fencer_rank.append(one)
        fencer_rank.append(two)
        opp_rank.append(three)
        opp_rank.append(four)
        
        f_hand = -1 if bio.loc[bio.id == bouts.loc[i].fencer_ID].hand.values[0] == "Left" else 1
        o_hand = -1 if bio.loc[bio.id == bouts.loc[i].opp_ID].hand.values[0] == "Left" else 1
        fencer_hand.append(f_hand)
        fencer_hand.append(o_hand)
        opp_hand.append(o_hand)
        opp_hand.append(f_hand)
        
    if i%1000==0 and i>999:
        print(i)

# Save data

dataDict = {"fencer_age":fencer_age,"opp_age":opp_age,"fencer_hand":fencer_hand,"opp_hand":opp_hand,
                     "fencer_rank":fencer_rank,"opp_rank":opp_rank,"score":score,"won":won}
for country in bio.country_code.drop_duplicates():
    dataDict["fencer_" + country] = fencer_country[country]
    dataDict["opp_" + country] = opp_country[country]
data =  pd.DataFrame(dataDict)
data.to_csv("organizedFencingData.csv")
