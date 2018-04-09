

class Classifier:
    self.cluster_string = 'cluster'
    self.individual_string = 'individual'

    def __init__(self, method):
        if method == self.cluster_string:
            self.classifier = ClusterClassifier()
        elif method == self.individual_string:
            self.classifier = IndividualClassifier()
        else:
            raise Exception('Invalid classification method. cluster or individual.')
            

class ClusterClassifier(Classifier):

    def __init__(self):

class IndividualClassifier(Classifier):

    def __init__(self):
