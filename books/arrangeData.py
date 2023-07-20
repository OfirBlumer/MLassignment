# Imports

import pandas as pd

# Get Data

books = pd.read_csv("Best_Book_21st.csv",thousands=',').drop_duplicates("title").reset_index().drop(columns=["index","title","id","book_link","publisher","author"])

# Create dict of genres and languages for each book; find how many awards it won and whether it is part of a series

genres = []
for i in range(len(books)):
    if books.loc[i].genre is not np.nan:
        for g in books.loc[i].genre.split(","):
            genres.append(g)
            
genresData = pd.DataFrame({"g":genres})
selGeneresList = genresData.g.value_counts().index
langList = list(books.lang.drop_duplicates())
generesDict = {}
Nawards = []
partOfSeries = []

for genere in selGeneresList:
    generesDict[genere] = []
    
langDict = {}
for lang in langList:
    langDict[lang] = []
    
for i in range(len(books)):
    try:
        Nawards.append(len(books.loc[i].award.split(",")))
    except:
        Nawards.append(0)
        
    partOf = 1
    if books.loc[i].series is np.nan:
        partOf = 0
    partOfSeries.append(partOf)
    
    for genere in selGeneresList:
        exist = 0
        if books.loc[i].genre is not np.nan:
            if genere in books.loc[i].genre.split(","):
                exist = 1
        generesDict[genere].append(exist)
        
    for lang in langList:
        exist = 0
        if lang == books.loc[i].lang:
            exist = 1
        langDict[lang].append(exist)   
        
for lang in langList:
    books[lang] = langDict[lang]
  
data = books.drop(columns = ["series","award","genre","lang"]).dropna()

# Add findings to data and find publication year

for genere in selGeneresList:
    books[genere] = generesDict[genere]
  
years = []
for year in list(data.date_published):
    try:
        years.append(int(year[-4:]))
    except:
        years.append(np.nan)
      
data = data.dropna().drop(columns="date_published")
data["year"] = years
books["Nawards"] = Nawards
books["partOfSeries"] = partOfSeries

# Save data

data.to_csv("booksOrganized.csv")
