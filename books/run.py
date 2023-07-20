# Imports

from multiprocessing import Pool
import numpy as np
from sklearn import tree, linear_model, ensemble
import pandas as pd
from itertools import product
from sklearn.metrics import r2_score

# Functions

def getAlpha(clf): # Calculates alpha for a random forest clf

    # Calculate wavelets for all leaves
  
    allWavelets = []
    for i in range(len(clf.estimators_)):
        tr = clf.estimators_[i].tree_
        n_nodes = tr.node_count
        children_left = tr.children_left
        children_right = tr.children_right
        values = tr.value
        nsamples = tr.n_node_samples
        wavelets = np.zeros(shape=n_nodes)
        wavelets[0] = np.sqrt(nsamples[0])
        for parent in range(n_nodes):
            if -1 != children_left[parent]:
                for child in [children_left[parent],children_right[parent]]:
                    wavelets[child] = abs(values[parent][0] - values[child][0])*np.sqrt(nsamples[child])
        allWavelets += list(wavelets)
    allWavelets = np.array(allWavelets)

    # Evaluate the derivative of N against tau
  
    taus = np.linspace(0,2,10000)
    N = np.array([sum(allWavelets**tau)**(-tau) for tau in taus])
    tau = 0.5*(taus[1:]+taus[:-1])
    dNdTau = (N[1:]-N[:-1])/taus[1]
    test = pd.DataFrame({"tau":tau,"derivative":dNdTau})

    # Define tau* as the minimal tau with derivative > -1
  
    tauStar = test.loc[test.derivative>-1].tau.min()
    alpha = 1/tauStar - 0.5
  
    return alpha

def simulate(params): # Trains a random forest using a set of hyper-parameters params

    # Sort data
  
    ntest,nFeatures, ntrees,max_depth,min_samples_leaf = params
    training = pd.concat(df_splits[:ntest]+df_splits[ntest+1:])
    test = df_splits[ntest]
    X = np.array(list(training.drop(columns="rate").itertuples(index=False, name=None)))
    Y = np.array(training["rate"])

    # Train model
  
    clf = ensemble.RandomForestClassifier(n_estimators=ntrees,max_features=nFeatures,max_depth=max_depth,min_samples_leaf=min_samples_leaf)
    clf = clf.fit(X, Y)

    # Compare with test
  
    predictions = clf.predict(np.array(list(test.drop(columns="rate").itertuples(index=False, name=None))))
    realScores = test["rate"]
    performance = pd.DataFrame({"pre":predictions,"score":realScores})

    # Save to file
  
    data = pd.DataFrame({"ntrees":ntrees,"nFeatures":[nFeatures],"max_depth":max_depth,"min_samples_leaf":min_samples_leaf,
                                      "accuracy":r2_score(performance.score,performance.pre),
                                      "alpha":getAlpha(clf)})
    data.to_csv(f"newResults/{round(nFeatures*10)}_{ntrees}_{max_depth}_{min_samples_leaf}_{ntest}.csv")
  
if __name__ == '__main__':

    # Get data and split to batches
  
    df = pd.read_csv("booksOrganized.csv")
    df_shuffled = df.sample(frac=1)
    df_splits = np.array_split(df_shuffled, 5)

    # Define hyper-parameters
  
    nFeaturesList = [0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,0.99]
    ntreesList = [1,2,5,10,20,50,100,200,500,1000]
    max_depthList = [1,2,5,10,20,50,100]
    min_samples_leafList = [1,2,5,10,20,50,100]

    # Train models with different sets of hyper-parameters simultaneously
  
    simulations_to_run = []
    for ntest,nFeatures, ntrees,max_depth,min_samples_leaf in product(range(5),nFeaturesList,ntreesList,max_depthList,min_samples_leafList):
        simulations_to_run.append([ntest,nFeatures, ntrees,max_depth,min_samples_leaf])
    with Pool(64) as pool:
        pool.map(simulate, simulations_to_run)
