# -*- coding: utf-8 -*-
"""
Created on Sat Dec 19 19:41:27 2015

@author: zhihuixie
"""

import pandas as pd
import numpy as np
import math

class UCF():
    """
    define user-user based recommendation system
    """
    def __init__(self, df):
        """
        one parameter: pandas data frame
        """
        self.df = df
        self.data = np.array(df.values)
        self.rows = df.index.values
        
    def p_corr(self):
        """
        calculate pearson correlation between users
        """
        data = self.data
        rows = self.rows
        (nrows, ncols) = data.shape
        p_corr_dict = {}

        for row_i in range(nrows):
            for row_j in range(nrows):
                valide_data_i = [data[row_i, :][n] \
                            for n in range(ncols) if \
                            data[row_i, n] != 0 and data[row_j, n] != 0]
                valide_data_j = [data[row_j, :][n] \
                                for n in range(ncols) if \
                                data[row_i, n] != 0 and data[row_j, n] != 0] 
                valide_data_i = np.array(valide_data_i) - np.mean(valide_data_i)
                valide_data_j = np.array(valide_data_j) - np.mean(valide_data_j)
                #print np.dot(data[row_i, :], data[row_j, :])
                p_corr = np.dot(valide_data_i, valide_data_j)*1.0/\
                         np.sqrt(sum(np.power(valide_data_i,2))*\
                                 sum(np.power(valide_data_j,2)))
                p_corr_dict[(rows[row_i], rows[row_j])] = p_corr  
        return p_corr_dict
        
    def p_corr_rank(self, user_id, n):
        """
        rank correlations between users and choose top n correlated users
        """
        p_corrs = self.p_corr()
        p_corrs_row = {}
        ranked_p_corrs = {}
        for (a, b) in p_corrs:
            if user_id == a:
                p_corrs_row[(a, b)] = p_corrs[(a, b)] 
        sorted_p_corrs = sorted(p_corrs_row, reverse = True, \
                         key = lambda x: p_corrs_row[x])[1:n + 1]
        for (i, j) in sorted_p_corrs:
            ranked_p_corrs[(i, j)] = p_corrs_row[(i, j)] 
        return ranked_p_corrs
        
    def prediction (self, user_id, n):
        """
        predict score without normalization
        """
        ranked_p_corrs = self.p_corr_rank(user_id, n)
        neighbors = [b for (a, b) in ranked_p_corrs.keys()]
        weights = ranked_p_corrs.values()
        df = self.df
        preds = []
        
        # Loop through all movies in the database
        for col in df.columns:
            values = 0
            weights = 0
            # Loop through the top n most similar users to the specified user (user_id)
            for neighbor in neighbors:
                # Value is equal to the rating that the neighbor gave to the movie in coloumn col
                value = df.loc[neighbor, col]
                if value == 0:
                    weight = 0
                else:
                    # Weight is equal to the pearson correlation value between the specified user and neighbor
                    weight = ranked_p_corrs[(user_id, neighbor)]
                # Sum all of the values and weights of all n neighbors for the current movie
                values += value*weight
                weights += weight
            # The predicted rating for a movie equals:
            # = sum of n closest neighbor's (rating for movie * p_corr value with specified user) / 
            #   sum of p_corr values of n neighbors with specified user
            if weights == 0:
                preds.append(0)
            else:
                preds.append(values*1.0/weights)
        return preds
        
    def prediction_with_nor(self, user_id, n):
        """
        predict score with normalization
        """
        ranked_p_corrs = self.p_corr_rank(user_id, n)
        neighbors = [b for (a, b) in ranked_p_corrs.keys()]
        weights = ranked_p_corrs.values()
        df = self.df
        preds = []
        user_mean = np.mean([num for num in df.loc[user_id, :] if num != 0 ])
        n_mean = {}
        for neighbor in neighbors:
            n_mean[neighbor] = np.mean([num for num in df.loc[neighbor, :] \
                                       if num != 0 ]) 
        for col in df.columns:
            values = 0
            weights = 0
            for neighbor in neighbors:
                value = df.loc[neighbor, col]
                if value == 0:
                    weight = 0
                else:
                    weight = ranked_p_corrs[(user_id, neighbor)]
                values += (value - n_mean[neighbor])*weight
                weights += weight
            if weights == 0:
                preds.append(user_mean)
            else:
                if user_mean + values*1.0/weights > 5:
                    preds.append(5.0)
                else:
                    preds.append(user_mean + values*1.0/weights)
        return preds 
    
    def recom(self, user_id, n, num_recoms, repeat_recoms, nor = False):
        """
        recommend top num_recoms items
        """
        cols = self.df.columns.values
        if not nor:
            pred = self.prediction(user_id, n)
        else:
            pred = self.prediction_with_nor(user_id, n)

        pred_dict = {}
        for i in range(len(cols)):
            pred_dict[cols[i]] = pred[i]

        # If flag is set to remove recommendations the user has already rated
        if not repeat_recoms:
            # list of all movies the user has previously rated
            user_rated_items = [key for (key, value) in self.df.T.to_dict()[user_id].items() \
                        if not value == 0]

            # delete all movies the user has rated from recommendation list
            for item in user_rated_items:
                del pred_dict[item]

        top_items = sorted(pred_dict, key = lambda x: pred_dict[x], reverse = True)[:num_recoms]
        print("Top " + str(num_recoms) + " movies \t", "\t Prediction")
        for item in top_items:
            print(item, "%.3f"%pred_dict[item])
        
        
if __name__ == "__main__":
    df = pd.read_excel("user-data.xls", sheet_name = 1)
    df = df.fillna(0)
    ucf = UCF(df)

    user1 = 3712
    user2 = 89
    n = 5
    num_recoms = 10
    repeat_recoms = False

    #Print top movies for user1 without normalization
    print("Top movies for " + str(user1) + ": ")
    ucf.recom(user1, n, num_recoms, repeat_recoms)
    print("\n")
    
    #Print top movies for user2 without normalization
    print("Top movies for " + str(user2) + ": ")
    ucf.recom(user2, n, num_recoms, repeat_recoms)
    print("\n")

    #Print top movies for user1 with normalization
    print("Top movies for " + str(user1) + " with normalization")
    ucf.recom(user1, n, num_recoms, repeat_recoms, nor = True)
    print("\n")
    
    #Print top movies for user2 with normalization
    print("Top movies for " + str(user2) + " with normalization")
    ucf.recom(user2, n, num_recoms, repeat_recoms, nor = True)
    print("\n")