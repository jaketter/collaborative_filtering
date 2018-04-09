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
        cosine similirity function: sum(A.B)/(sqrt(sum(A^2))*sqrt(sum(A^2)))
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

        for item in user_rated_items:
            user_list.append(item)

        for item in self.cols:
            values = 0
            scores = 0
            dict_sim = self.sim_matrix(item, is_norm = is_norm)
            for (key, value) in  user_rated_items:
                if key == "User":
                    pass
                else:
                    score = dict_sim[(item, str(key))]
                    if score < 0:
                        score = 0
                    scores += score
                    values += value*score
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


        for item in items_to_delete:
            del dicts[item]

        top_items = sorted(dicts, key = lambda x: dicts[x], reverse = True)[:n+1]

        return top_items
        
if __name__ == "__main__":
    df = pd.read_excel("item-item_data.xlsx", sheet_name = 0)
    recom = Icf(df)
    #test
    target = "318: Shawshank Redemption, The (1994)"
    user = 5277
    recommend_repeats = True

    # print("Test cases:")
    # print(dict_raw[(target, item)])
    # print(dict_norm[(target, item)], "\n")

    dict_raw = recom.sim_matrix(target)
    dict_norm = recom.sim_matrix(target, is_norm = True)

    # Print top 5 most similar movies to target movie, unnormalized
    print("Top 5 movies with most similirity to " + target + ":")
    print(recom.recom(5, dict_raw), "\n")
   
    # Print top 5 recommended movies for specified user, unnormalized
    user_list = []
    preds = recom.prediction(user, user_list)
    print("Top 5 movies with highest recommendation to user " + str(user) + ":")
    if recommend_repeats:
        print(recom.recom(5, preds), "\n")
    else:
        print(recom.recom(5, preds, user_list), "\n")
    
    # Print top 5 most similar users to specified movie, normalized
    print("Top 5 movies with most similirity to " + target + " under normalization:")
    print(recom.recom(5, dict_norm), "\n")

    # Print top 5 recommended movies for specified user, normalized
    user_list_norm = []
    preds = recom.prediction(user, user_list_norm, is_norm = True)
    print("Top 5 movies with highest recommendation to user " + str(user) + " under normalization:")
    if recommend_repeats:
        print(recom.recom(5, preds), "\n")
    else:
        print(recom.recom(5, preds, user_list_norm), "\n")