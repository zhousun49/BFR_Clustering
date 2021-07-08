import math
from itertools import combinations
# DSclassification, CSclassification, DScentroids, CScentroids, RS, unassigned_data, DS_std, CS_std, CS_SUM
class BFRClass: 
    def __init__(self, data, n_clusters, DSclassification, CSclassification, DScentroids, CScentroids, RS, unassigned_data, DS_std, CS_std, CS_SUM):
        dic = {}
        self.k = n_clusters
        self.unassigned_data = unassigned_data
        for i in data:
            spt = i.split(",")
            dic[int(spt[0])] = spt
        self.data = dic
        self.DScentroids = DScentroids
        self.CScentroids = CScentroids
        self.DS_std = DS_std
        self.CS_std = CS_std
        self.DS = DSclassification
        self.CS = CSclassification
        self.RS = RS
        self.CS_SUM = CS_SUM
        
    def fit(self):
        largek = self.k*3
        distances = []
        ##Assigning points
        for i in self.data: 
            distances = {}
            for DScent in self.DScentroids:
                distance = self.MahalanobisDistance(i, self.DScentroids[DScent], self.DS_std[DScent], "classify")
                distances[DScent] = distance
            minimum_key = min(distances, key=distances.get)
#             print(distances)
            if (distances[minimum_key] < 2*math.sqrt(len(self.data[i]) - 1)):
                self.DS[minimum_key].append(i)
            else: 
                if (len(self.CScentroids) != 0): 
                    CSdistances = {}
                    for CScent in self.CScentroids:
                        CSdistance = self.MahalanobisDistance(i, self.CScentroids[CScent], self.CS_std[CScent], "classify")
                        CSdistances[CScent] = CSdistance
                    minimum_key = min(CSdistances, key=CSdistances.get)
                    if (CSdistances[minimum_key] < 2*math.sqrt(len(self.data[i]) - 1)):
                        self.CS[minimum_key].append(i)
                    else: 
                        self.RS.add(i)
                else: 
                    self.RS.add(i)
        # print("RS: ", self.RS)
        for i in self.unassigned_data: 
            self.data[i] = self.unassigned_data[i]
            
        ##Step 10, seperate CS and RS again
        if len(self.RS) != 0: 
            centers = self.initCentroid(self.RS, largek)
            idx = 0
            while True: 
                CS_result = self.initClassify(self.RS, centers, idx)
#                 print("classification result: ", CS_result)
                updated_centroids = self.updateCentroid(CS_result)
                CS_centroids = updated_centroids
                self.newCS_centroids = updated_centroids
                if updated_centroids[0] == self.newCS_centroids[0]:
                    break
#                 print("Run number: ", idx)
                idx += 1
            # print("finished classifying RS")
            self.generateCSstats(CS_result)
            returned_CS_centroids = {}
            for i in self.new_CSclassification:
                returned_CS_centroids[i] = self.newCS_centroids[i]
            self.newCS_centroids = returned_CS_centroids
            ##Add new CS centroids, points and std to existing data 
#             print("old CS centroids: ", self.CScentroids)
            if len(self.CScentroids) != 0 and len(self.newCS_centroids) != 0: 
                # print("one max: ", max(self.CS.keys()))
                max_idx = max(max(self.CScentroids.keys()), max(self.CS.keys()), max(self.CS_std.keys()))
                # print("max index: ", max_idx)
                for i in self.newCS_centroids: 
                    self.CScentroids[max_idx + 1 + i] = self.newCS_centroids[i]
                for i in CS_result: 
                    self.CS[max_idx + 1 + i] = CS_result[i]
                for i in self.newCS_std: 
                    self.CS_std[max_idx + 1 + i] = self.newCS_std[i]
                for i in self.newCS_SUM: 
                    self.CS_SUM[max_idx + 1 + i] = self.newCS_SUM[i]
            elif len(self.CScentroids) == 0 and len(self.newCS_centroids) != 0: 
                for i in self.newCS_centroids: 
                    self.CScentroids[i] = self.newCS_centroids[i]
                for i in CS_result: 
                    self.CS[i] = CS_result[i]
                for i in self.newCS_std: 
                    self.CS_std[i] = self.newCS_std[i]
                for i in self.newCS_SUM: 
                    self.CS_SUM[i] = self.newCS_SUM[i]
        ##Step11: mergeCS clusters
#         print("new centroids: ", self.newCS_centroids)
#         print("new std: ", self.newCS_std)
        CS_combinations = list(combinations(self.CScentroids, 2))
        ##Return CSSUM from previous
        ##Can compute centroid from existing points, and std info from existing points
        for i in CS_combinations: 
#             print("combo: ", i)
            if i[0] in self.CScentroids and i[1] in self.CScentroids: 
                distance = self.MahalanobisDistance(self.CScentroids[i[0]], self.CScentroids[i[1]], self.CS_std[i[0]], "merge")
                if (distances[minimum_key] < 2*math.sqrt(len(self.CScentroids[i[0]]) - 1)):
                    self.mergeCS(i[0], i[1])
#                 print("distance: ", distance)
        ##Dissipating remaining points RS into CS and see if they can merge with existing clusters
        unassigned = {}
        for i in self.RS:
            unassigned[i] = self.data[i]
        to_delete = []
        for i in self.CS:
            if len(self.CS[i]) <= 1: 
                to_delete.append(i)
        for i in to_delete: 
            del(self.CS[i])
        return self.DS, self.CS, self.RS, self.CScentroids, self.CS_SUM, self.CS_std, unassigned
    
    def mergeCS(self, cluster1, cluster2):
        ##New cluster
        max_cluster_num = max(self.CS)
        c1_pts = self.CS[cluster1]
        c2_pts = self.CS[cluster2]
        self.CS[max_cluster_num + 1] =  c1_pts + c2_pts 
        ##New centroids
        new_centroid = [] 
        for i in  range(len(self.CScentroids[cluster1])): 
            new_centroid.append((self.CScentroids[cluster1][i]*len(c1_pts) + self.CScentroids[cluster2][i]*len(c2_pts))/(len(c1_pts) + len(c2_pts)))
        self.CScentroids[max_cluster_num + 1] = new_centroid
#         print("new centroid: ", len(new_centroid))
        ##New sum and std
        new_CS_SUM = []
        for i in  range(len(self.CS_SUM[cluster1])): 
            new_CS_SUM.append(self.CS_SUM[cluster1][i] + self.CS_SUM[cluster2][i]) 
        self.CS_SUM[max_cluster_num + 1] = new_CS_SUM
        std = []
        for p in range(len(new_CS_SUM)):
            std.append(math.sqrt(new_CS_SUM[p]**2/(len(c1_pts) + len(c2_pts)) -  (new_CS_SUM[p]/(len(c1_pts) + len(c2_pts)))**2))
        self.CS_std[max_cluster_num + 1] = std
        ##Remove original cluster numbers
        del(self.CS[cluster1])
        del(self.CS[cluster2])
        del(self.CScentroids[cluster1])
        del(self.CScentroids[cluster2])
        del(self.CS_SUM[cluster1])
        del(self.CS_SUM[cluster2])
        del(self.CS_std[cluster1])
        del(self.CS_std[cluster2])
        
        
    def EuclideanDistance(self, pt1, pt2):
        pt1 = self.data[pt1]
        pt2 = pt2
        pt1_distances = pt1[1:]
        pt2_distances = pt2[1:]
        sum_sqrt = sum([(float(pt1_distances[num]) - float(pt2_distances[num]))**2 for num in range(len(pt1_distances))])
        return math.sqrt(sum_sqrt)
    
    def initClassify(self, points, centers, idx): 
        ##First run, no need for duplicate points
        if idx == 0: 
            initial_points = [int(x[0]) for x in self.new_CScentroids.values()]  
            # print("initial: ", initial_points)
        else: 
            initial_points = []
        ##Centroid Keys for DS and RS
        centroids_dic = self.new_CScentroids
        classification_result = {}
        if idx == 0: 
            for i in range(len(centers)): 
                classification_result[i] = [initial_points[i]]
        for point in points:
            if (point not in initial_points): 
                distances = []
                for c in centroids_dic: 
                    distances.append(self.EuclideanDistance(point, centroids_dic[c]))   
                assigned_cluster = distances.index(min(distances))
                if assigned_cluster in classification_result: 
                    classification_result[assigned_cluster].append(point)
                else: 
                    classification_result[assigned_cluster] = [point]
        return classification_result

    def updateCentroid(self, first_classification): 
        center = {}
        for i in first_classification:
            one_cluster_points = first_classification[i]
            c = []
#             print("first classification: ", i)
            for p in one_cluster_points: 
#                 print("point: ", p)
                test_list = [float(x) for x in self.data[p]]
                c.append(test_list)
            sums = [sum(x) for x in zip(*c)]
            new_center = [x/len(c) for x in sums]
            center[i] = new_center
        return center
    
    def initCentroid(self, points, k):
        # print("RS points: ", points)
        idx = 0
        points = list(points)
        lst = []
        k = min(len(points), k)
        self.new_CScentroids = {}
        while idx < k:
            self.new_CScentroids[idx] = self.data[points[idx]]
            lst.append(idx)
            idx += 1
#         print("new cs centroids: ", self.new_CScentroids)
        return lst

    def MahalanobisDistance(self, pt1, pt2, std, option):
        if option == "classify":
            pt1 = self.data[pt1]
        elif option == "merge":
            pt1 = pt1
        pt2 = pt2
        pt1_distances = pt1[1:]
        pt2_distances = pt2[1:]
        sum_sqrt = sum([((float(pt1_distances[num]) - float(pt2_distances[num]))/std[num])**2 for num in range(len(pt1_distances))])
        return math.sqrt(sum_sqrt)

    def generateCSstats(self, CS_result): 
        self.RS = set()
        CS_classification = {}
        for i in CS_result:
#             print("CS result: ", CS_result[i])
            if (len(CS_result[i])) <= 1:
                self.RS.update(CS_result[i])
            else: 
                CS_classification[i] = CS_result[i]
#         print("CS result: ", CS_classification)
#         print("new RS: ", self.RS)
        self.new_CSclassification = CS_classification   
        CSN = {}
        CSSUM = {}
        CSSUMQ = {}
        for i in CS_classification: 
            CSN[i] = len(CS_classification[i])
            points_1d = []
            for j in CS_classification[i]: 
                test_list = [float(x) for x in self.data[j]]
                points_1d.append(test_list)
            sums = [sum(x) for x in zip(*points_1d)]
            CSSUM[i] = sums[1:]
            sumsquare = [x**2 for x in CSSUM[i]]
            CSSUMQ[i] = sumsquare
        self.newCS_SUM = CSSUM
        CS_std_dict = {}
        for i in CSN:
            returned = []
            for p in range(len(CSSUM[i])):
                returned.append(math.sqrt(CSSUMQ[i][p]/CSN[i] -  (CSSUM[i][p]/CSN[i])**2))
            CS_std_dict[i] = returned
#         print("CS std: ", CS_std_dict)
        self.newCS_std = CS_std_dict