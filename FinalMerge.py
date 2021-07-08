# vars = [DS, CS, RS, DScentroids, CScentroids, CS_SUM, CS_std, unassigned_data, DScentroids, DS_std]
import math

class FinalMerge: 
    def __init__(self, DS, CS, RS, DScentroids, CScentroids, DS_std, unassigned_data): 
        self.DS = DS
        self.CS = CS
        self.RS = RS
        self.DScentroids = DScentroids
        self.CScentroids = CScentroids
        self.DS_std = DS_std
        self.unassigned_data = unassigned_data
    
    def classify(self):
        self.RSclassification()
        print("finished RS classification")
        self.CSclassification()
        print("finished CS classification")
        return self.DS
            
    def RSclassification(self):
        for i in self.unassigned_data: 
            distances = {}
            for DScent in self.DScentroids:
                distance = self.MahalanobisDistance(self.unassigned_data[i], self.DScentroids[DScent], self.DS_std[DScent])
                distances[DScent] = distance
            minimum_key = min(distances, key=distances.get)
            self.DS[minimum_key].append(i)
    
    def CSclassification(self):
        for i in self.CScentroids: 
            distances = {}
            for DScent in self.DScentroids:
                distance = self.MahalanobisDistance(self.CScentroids[i], self.DScentroids[DScent], self.DS_std[DScent])
                distances[DScent] = distance
            minimum_key = min(distances, key=distances.get)
            self.DS[minimum_key] = self.DS[minimum_key] + self.CS[i]
    
    def MahalanobisDistance(self, pt1, pt2, std):
        pt1 = pt1
        pt2 = pt2
        pt1_distances = pt1[1:]
        pt2_distances = pt2[1:]
        sum_sqrt = sum([((float(pt1_distances[num]) - float(pt2_distances[num]))/std[num])**2 for num in range(len(pt1_distances))])
        return math.sqrt(sum_sqrt)