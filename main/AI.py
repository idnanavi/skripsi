import pandas as pd
import numpy as np
from scipy.sparse import csr_matrix
from sklearn.neighbors import NearestNeighbors

def getRecommendation(productId, ratings):
    ratings = ratings.sub(ratings.mean(axis=1), axis=0)
    df_matrix = csr_matrix(ratings.values)

    model_knn = NearestNeighbors(metric = 'cosine', algorithm = 'brute')
    model_knn.fit(df_matrix)


    recommend_list = list()

    try:
        distances, indices = model_knn.kneighbors(ratings.loc[float(productId),:].values.reshape(1, -1), n_neighbors = 9)
        for i in range(0, len(distances.flatten())):
            if len(recommend_list) == 5 :
                return recommend_list
            if ratings.index[indices.flatten()[i]] == int(productId):
                pass
            else:
                # print('{0}: {1}, with distance of {2}:'.format(i, ratings.index[indices.flatten()[i]], distances.flatten()[i]))
                recommend_list.append(ratings.index[indices.flatten()[i]])
        return recommend_list
    except:
        return recommend_list
