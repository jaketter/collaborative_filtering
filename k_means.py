from math import sqrt
from os.path import isdir, isfile
from os import listdir
import csv
import errno
import os
import copy
import json

from data_structures import User, Movie

#finds euclidean distance
def euclidean_distance(a, b):
    if len(a) == 0:
        squares = [(b[i])**2 for i in range(len(b))]
    elif len(b) == 0:
        squares = [(a[i])**2 for i in range(len(a))]
    else:
        squares = [(a[i] - b[i])**2 for i in range(len(a))]
    return sqrt(sum(squares))

class Cluster:

    #location is an n-tuple
    #users is a collection of tuples from user coordinates to the user
    #they represent
    def __init__(self, location):
        self.center = location
        self.users = {}

    def clear(self):
        self.users = {}

    def get_size(self):
        return len(self.users)

    def assign_user(self, vector, user):
        self.users[vector] = user

    def get_users(self):
        return self.users

    def assign_users(self, users):
        self.users.update(users)

    def update_center(self):
        #[[a, b, c], [c, d, e], [f, g, h]] ->
        #[[a, c, f], [b, d, g], [c, e, h]]
        user_vecs = list(self.users.keys())
        dimensions = zip(*user_vecs)
        num_users = len(self.users)

        self.center = [sum(x)/num_users for x in dimensions]

    def top_n_movies(self, n):
        all_rated_movies = {}
        for user in self.users.values():
            for movie in user.ratings.items():
                all_rated_movies.setdefault(movie[0], []).append(movie[1])

        movie_ratings = {movie : sum(all_rated_movies[movie])/float(len(all_rated_movies[movie])) for movie in all_rated_movies.keys()}
        movie_ratings = [(movie,movie_ratings[movie]) for movie in movie_ratings.keys()]
        movie_ratings.sort(key=lambda x : x[1])
        movies = [movie[0] for movie in movie_ratings]

        return movies[:n]
            

class KMeans:
    '''
    this is confusing but basically I'm trying to spread the
    starting locations evenly accross the space the data 
    occupies
    '''
    def get_starting_locations(self, vectors, num_clusters):
        dimensions = list(zip(*vectors))
        upper_bounds = [max(dimensions[i]) for i in range(len(dimensions))]
        steps = [bound/num_clusters for bound in upper_bounds]

        starting_locations = [ [step*dim for dim in steps]
                               for step in range(num_clusters)]
        return starting_locations

    def __init__(self, users, num_clusters=5):
        starting_locations = self.get_starting_locations(list(users.keys()), num_clusters)
        self.clusters = [Cluster(starting_locations[i])
                         for i in range(num_clusters)]
        self.users = users
        
        #used to see if the clusters change over iterations
        self.prev_sizes = { c : None for c in self.clusters }

    def update_previous_sizes(self):
        self.prev_sizes = { c : c.get_size() for c in self.clusters }

    def system_converged(self):
        for c in self.clusters:
            if c.get_size() != self.prev_sizes[c]:
                return False
        return True

    def cluster(self):
        i = 0
        while not self.system_converged():
            self.update_previous_sizes()
            self.assign()
            if i % 10 == 0:
                for cluster in self.clusters:
                    print(len(cluster.users))
                print()
            i += 1
            self.update()
            
        self.assign()
        for cluster in self.clusters:
            print(len(cluster.users))

    def assign(self, dist_func=euclidean_distance):
        for cluster in self.clusters:
            cluster.clear()

        for user in self.users.items():
            distances = {
                c : dist_func(user[0], c.center) for c in self.clusters
            }
            assignment = min(distances.items(), key=lambda x : x[1])[0]
            assignment.assign_user(user[0], user[1])

    def update(self):
        for cluster in self.clusters:
            cluster.update_center()

    def get_cluster_centers(self):
        return [c.center for c in clusters]

ratings_heading = ['user_id', 'movie_id', 'rating', 'timestamp']
users_heading = ['user_id', 'gender', 'age', 'occupation']
movies_heading = ['movie_id', 'title', 'genres']

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and isdir(path):
            pass
        else:
            raise

def parse(path, file_name):
    data = []
    with open(path + file_name, 'r') as file:
        for line in file:
            line_data = line.split('::')
            data.append(line_data)
            
    new_path = './ml-1m/csv/' + file_name[:-4] + '.csv'
    mkdir_p('./ml-1m/csv/')
    with open(new_path, 'w') as file:
        writer = csv.writer(file)
        file_name = file_name[0:-4:1]
        if file_name == 'movies':
            writer.writerow(movies_heading)
        elif file_name == 'ratings':
            writer.writerow(ratings_heading)
        elif file_name == 'users':
            writer.writerow(users_heading)
        else:
            raise Exception('Tried to parse invalid file')
        for line in data:
            writer.writerow(line)

def parse_dat_files(path):
    for file_name in listdir(path):
        if file_name[-4:] == '.dat':
            parse(path, file_name)



def main():
    target_user = 1

    if not isdir('./ml-1m/csv/'):
        data_path = './ml-1m/'
        parse_dat_files(data_path)
    data_path = './ml-1m/csv/'
    
    user_path = data_path + './users.csv'
    rating_path = data_path + './ratings.csv'
    movie_path = data_path + './movies.csv'

    users = []
    movies = {}
    all_genres = set([])
    vector_users = {}

    target_user_ratings = []

    with open(user_path, 'r') as file:
        data_stream = csv.DictReader(file)
        
        for line in data_stream:
            user_id = int(line['user_id'])
            gender = line['gender']
            age = int(line['age'])
            occupation = line['occupation']
            new_user = User(user_id, gender, age, occupation)
            users.append(new_user)

    with open(movie_path, 'r') as file:
        data_stream = csv.DictReader(file)
        
        for line in data_stream:
            movie_id = int(line['movie_id'])
            title = line['title']
            genres = line['genres']
            genres = genres.split('|')
            for i in range(len(genres)):
                genres[i] = genres[i].strip('\n')
                

            all_genres.update(genres)
            movies[movie_id] = Movie(movie_id, title, genres)
            

    with open(rating_path, 'r') as file:
        data_stream = csv.DictReader(file)
    
        for line in data_stream:
            user_id = int(line['user_id'])
            movie_id = int(line['movie_id'])
            rating = int(line['rating'])

            rating = {'movie' : movies[movie_id], 'score' : rating}
            if user_id == target_user:
                target_user_ratings.append(rating)
            else:
                users[user_id-1].load_rating(rating)


    for user in users:
        if user.user_id == target_user:
            continue
        user.compute_average_rating()
        user.compute_adjusted_ratings()
        user.load_genre_scores(list(all_genres))
        
        user_vector = user.get_vector_representation(all_genres)
        vector_users[tuple(user_vector)] = user

    if isfile('./clusters.json'):
        with open('./clusters.json', 'r') as file:
            json_structure = json.load(file)
        clusters = [Cluster(cluster['center']) for cluster in json_structure.values()]
        for cluster in json_structure.keys():
            cluster_users = [users[i-1] for i in json_structure[cluster]['users']]
            cluster_users = { tuple(user.get_vector_representation(all_genres)) : user for users in cluster_users }
            clusters[int(cluster)].assign_users(cluster_users)
    else:
        algorithm = KMeans(vector_users, len(all_genres))
        algorithm.cluster()
        clusters = algorithm.clusters

        json_structure = {c : 
                          {
                            'center' : clusters[i].center,
                              'users' : [user.user_id for user in clusters[i].users.values()]
                          } for c in range(len(clusters))}

        with open('./clusters.json', 'w') as file:
            file.write(json.dumps(json_structure, indent=2))

    target_user = users[target_user-1]
    for rating in range(5):
        target_user.load_rating(target_user_ratings[rating])

    target_user.compute_average_rating()
    target_user.compute_adjusted_ratings()
    target_user.load_genre_scores(list(all_genres))
    target_user_vector = target_user.get_vector_representation(list(all_genres))
    
    distances = {c : euclidean_distance(target_user_vector, c.center) for c in clusters}
    closest_cluster = min(distances.items(), key=lambda x : x[1])[0]

    for movie in closest_cluster.top_n_movies(5):
        print(movie.movie_id)

if __name__ == '__main__':
    main()
