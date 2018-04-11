# -*- coding: utf-8 -*-
"""
Created on Sat Jan  2 14:51:43 2016

@author: zhihuixie
"""

import pandas as pd
import math

class Icf():
    """
    define item-item based recommendation system
    """
    def __init__(self, df):
        """
        initiate one parameter:
        df- pandas dataframe
        """
        self.df = df
        self.cols = self.df.columns.values[1:]
        
    def norm(self):
        """
        mean centered normalization
        """
        df = self.df.iloc[:,1:]
        df_norm = df.T - df.T.mean(axis = 0) 
        return df_norm.T
    
    def sim_func(self, df, item1, item2):
        """
        cosine similirity function: sum(A.B)/(sqrt(sum(A^2))*sqrt(sum(B^2)))
        """
        nom = float((df[item1]*df[item2]).sum())
        denom = math.sqrt(df[item1].pow(2).sum())*math.sqrt(df[item2].pow(2).sum())
        cos = nom/denom
        return cos
        """
        if cos > 0:
           return cos
        else:
            return 0
        """
    
    def sim_matrix(self, target, is_norm = False):
        """
        cosine similirity dict
        """
        dict_sim = {}
        if not is_norm:
            df = self.df
        else:
            df = self.norm()
        for col in self.cols:
            dict_sim[(target, col)] = self.sim_func(df, target, col)
        return dict_sim
    
    def prediction (self, user, user_list, is_norm = False):
        """
        predict items for user
        """
        preds = {}
        df = self.df
        df.index = df.User
        user_rated_items = [(key, value) for (key, value) in self.df.T.to_dict()[user].items() \
                            if not math.isnan(value)]

        # Create list of movies user has previously rated
        for item in user_rated_items:
            user_list.append(item)

        # Loop through all movies
        for item in self.cols:
            values = 0
            scores = 0
            # Create a similarity matrix for the current movie (comparing the current movie to all other movies in data set)
            dict_sim = self.sim_matrix(item, is_norm = is_norm)
            # Loop through all movies the user has previously rated
            for (key, value) in  user_rated_items:
                if key == "User":
                    pass
                else:
                    # Score is equal to the cosine similarity between the two movies being compared
                    score = dict_sim[(item, str(key))]
                    if score < 0:
                        score = 0
                    # Sum all of the similarity scores for the current movie and all movies the user has rated
                    scores += score
                    # Sum the values for the current movie and all the movies the user has rated (Similarity * User's rating)
                    values += value*score
            # Predicted user rating for each movie is the sum of all (User rating * Similarity(user rated movie, current movie)) 
            # for all possible (User rated movie, movie) pairs 
            preds[item] = float(values)/scores     
        return preds
    
    def recom (self, n, dicts, user_list = []):
        """
        recommend top n items
        """

        items_to_delete = []
        for item in dicts:
            for (movie, value) in user_list:
                if item == movie:
                        items_to_delete.append(item)

        # Delete items that have been previously rated by the current user
        for item in items_to_delete:
            del dicts[item]

        top_items = sorted(dicts, key = lambda x: dicts[x], reverse = True)[:n+1]

        return top_items
        
if __name__ == "__main__":
    df = pd.read_excel("data-big.xls", sheet_name = 1)
    recom = Icf(df)

    target = "12: Finding Nemo (2003)"
    user = 3712
    num_recoms = 5
    recommend_repeats = False

    dict_raw = recom.sim_matrix(target)
    dict_norm = recom.sim_matrix(target, is_norm = True)

    # Print top 5 most similar movies to target movie, unnormalized
    print("Top " + str(num_recoms) + " movies with most similirity to " + target + ":")
    print("\n")
    movies = recom.recom(num_recoms, dict_raw)
    for item in movies:
        print(item[1])
   
    print("\n\n")
    # Print top 5 recommended movies for specified user, unnormalized
    user_list = []
    preds = recom.prediction(user, user_list)
    print("Top " + str(num_recoms) + " movies with highest recommendation to user " + str(user) + ":")
    print("\n")
    top_items = []
    if recommend_repeats:
        top_items = recom.recom(num_recoms, preds)
    else:
        top_items = recom.recom(num_recoms, preds, user_list)

    for item in top_items:
        # print(item, "\tPredicted rating: " + "%.3f"%preds[item])
        print(item)
        print("\tPredicted rating: " + "%.3f"%preds[item])
    print("\n\n")

    # Print top 5 most similar users to specified movie, normalized
    print("Top " + str(num_recoms) + " movies with most similirity to " + target + " under normalization:")
    print("\n")
    movies = recom.recom(num_recoms, dict_norm)
    for item in movies:
        print(item[1])

    print("\n\n")

    # Print top 5 recommended movies for specified user, normalized
    user_list_norm = []
    preds = recom.prediction(user, user_list_norm, is_norm = True)
    print("Top " + str(num_recoms) + " movies with highest recommendation to user " + str(user) + " under normalization:")
    print("\n")
    if recommend_repeats:
        top_items = recom.recom(num_recoms, preds)
    else:
        top_items = recom.recom(num_recoms, preds, user_list_norm)

    for item in top_items:
        # print(item, "\tPredicted rating: " + "%.3f"%preds[item])
        print(item)
        print("\tPredicted rating: " + "%.3f"%preds[item])

