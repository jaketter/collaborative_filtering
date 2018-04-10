class User:

    def __init__(self, user_id, gender, age, occupation):
        self.user_id = user_id
        self.gender = gender
        self.age = age
        self.occupation = occupation
        
        self.ratings = {}

    def load_rating(self, rating):
        self.ratings[rating['movie']] = rating['score']

    def get_vector_representation(self, genres):
        self.user_vector = [self.genre_scores[genre] for genre in genres]
        return self.user_vector

    def compute_average_rating(self):
        avg = 0
        for rating in iter(self.ratings.values()):
            avg += float(rating)
        avg /= len(self.ratings)
        
        self.average_rating = avg
        return avg

    def compute_adjusted_ratings(self):
        self.adjusted_ratings = {}

        for rating in iter(self.ratings.items()):
            movie = rating[0]
            raw_score = rating[1]
            self.adjusted_ratings[movie] = raw_score - self.average_rating

    #genres enumerates the list of genres
    def load_genre_scores(self, genres):
        self.genre_scores = { g : [x[1] for x in self.ratings.items() if g in x[0].genres] 
                              for g in genres }
        self.adjusted_genre_scores = { g : [x[1] for x in self.adjusted_ratings.items() if g in x[0].genres]
                                       for g in genres }

        self.genre_scores = { g : sum(self.genre_scores[g])/float(len(self.genre_scores[g])) if len(self.genre_scores[g]) > 0
                              else self.average_rating
                              for g in self.genre_scores.keys() }
        self.adjusted_genre_scores = { g : sum(self.adjusted_genre_scores[g])/float(len(self.adjusted_genre_scores[g]))
                                       if len(self.adjusted_genre_scores[g]) > 1 else 0
                                       for g in self.adjusted_genre_scores.keys() }
                                

class Movie:
    
    def __init__(self, movie_id, movie_title, genres):
        self.movie_id = movie_id
        self.movie_title = movie_title
        self.genres = set(genres)
        
