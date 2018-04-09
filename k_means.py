from math import sqrt

#finds euclidean distance
def euclidean_distance(a, b):
    squares = [(a[i] - b[i])**2 for i in range(len(a))]
    return sqrt(sum(squares))

class Cluster:

    #location is an n-tuple
    #points is some kind of list or array
    def __init__(self, location):
        self.center = location
        self.points = []

    def clear(self):
        self.points = []

    def get_size(self):
        return len(self.points)

    def assign_point(self, point):
        self.points.append(point)

    def assign_points(self, points):
        self.points.extend(points)

    def update_center(self):
        #[[a, b, c], [c, d, e], [f, g, h]] ->
        #[[a, c, f], [b, d, g], [c, e, h]]
        dimensions = zip(self.points)
        num_points = len(points)

        self.center = [sum(x)/num_points for x in dimensions]
            

class KMeans:

    '''
    this is confusing but basically I'm trying to spread the
    starting locations evenly accross the space the data 
    occupies
    '''
    def get_starting_locations(self, points):
        dimensions = zip(points)
        upper_bounds = [max(dimensions[i]) for i in range(len(dimensions))]]
        steps = [bound/num_clusters for bound in upper_bounds]

        starting_locations = [ [step*dim for dim in steps]
                               for step in range(num_clusters)]
    def __init__(self, points, num_clusters=5):

        starting_locations = self.get_starting_locations()
        self.clusters = [Cluster(starting_locations[i])
                         for i in range(num_clusters)]
        self.points = points
        
        #used to see if the clusters change over iterations
        self.prev_sizes = { c : 0 for c in self.clusters }

    def update_previous_sizes(self):
        self.prev_sizes = { c : c.get_size() for c in self.clusters }

    def system_converged(self):
        for c in self.clusters:
            if c.get_size != self.prev_sizes[c]:
                return False
        return True

    def cluster(self):
        while not self.system_converged():
            self.update_previous_sizes()
            self.assign()
            self.update()

    def assign(self, dist_func=euclidean_distance):
        for cluster in self.clusters:
            cluster.clear()

        for point in self.points:
            distances = {
                c : dist_func(point, c.center) for c in self.clusters
            }
            assignment = min(distances, key=lambda x : x[1])[0]
            assignment.assign_point(point)

    def update(self):
        for cluster in self.clusters:
            cluster.update_center()
