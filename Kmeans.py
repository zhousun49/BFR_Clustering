import random 
import math

class Kmeans:
    def __init__(self, k, data):
        self.k = k
        dic = {}
        for i in data:
            spt = i.split(",")
            dic[int(spt[0])] = spt
        self.data = dic
        self.filter_length = math.ceil(len(self.data)*0.018)
        
    def fit(self): 
        ##Initiate and seperate into 50 clusters
        largek = 3*self.k
        random_centroids = self.initCentroid(list(self.data.keys()), largek, "DS")
        idx = 0
        while True: 
            mid_result = self.initClassify(list(self.data.keys()), random_centroids, idx, "DS")
            updated_centroids = self.updateCentroid(mid_result)
            if updated_centroids[0] == self.centroids[0]:
                break
            random_centroids = updated_centroids
            self.centroids = updated_centroids
            print("Run number: ", idx)
            idx += 1
        # print("finished classifying first ", largek)
        # print("First centroid length: ", len(self.centroids))
        ##Cluster number = 5. Get rid of discard set
        inliers = self.initRS(mid_result)
        k_random_centroids = self.initCentroid(inliers, self.k, "DS")
        idx = 0
        while True: 
            mid_result = self.initClassify(inliers, k_random_centroids, idx, "DS")
#             print("middle result length: ", len(mid_result))
            updated_centroids = self.updateCentroid(mid_result)
            if updated_centroids[0] == self.centroids[0]:
                break
            k_random_centroids = updated_centroids
            self.centroids = updated_centroids
            print("Run number: ", idx)
            idx += 1
        # print("finished classifying second ", self.k)
        # print("DS centroid length: ", len(self.centroids))
        inliers = self.appendRS(mid_result)
        self.DSclassification = mid_result
        self.DS = inliers
        self.generateDSstats(self.DSclassification)
        # print("DS length: ", len(self.DS))
        # print("Total number of points after bigk classification: ", len(self.RS)+len(self.DS))
        ##Compute CS from RS
        CS_centroids = self.initCentroid(self.RS, largek, "RS")
        # print("CS centroids: ", len(CS_centroids))
#         print("RS before dividing into CS: ", self.RS)
        if (len(CS_centroids) > 0): 
            idx = 0
            while True: 
                CS_result = self.initClassify(self.RS, CS_centroids, idx, "RS")
                updated_centroids = self.updateCentroid(CS_result)
    #             print("CS result", CS_result)
                CS_centroids = updated_centroids
                self.centroidsCS = updated_centroids
                if updated_centroids[0] == self.centroidsCS[0]:
                    break
                print("Run number: ", idx)
                idx += 1
            # print("finished classifying third ", largek)
            # print("CS centroids: ", len(updated_centroids))
            self.generateCSstats(CS_result)
        else: 
            self.CS = {}
        print("DS: ", len(self.DS), " CS: ", len(self.CS), " RS: ", len(self.RS))
        print("Total number of points: ", len(self.RS)+len(self.DS)+len(self.CS))
#         print([self.SUMQ[x]/float(self.N) -  (self.SUM[x]/float(self.N))^2 for x in range(len(self.SUMQ))])
        DS_std_dict = {}
        for i in self.N:
            returned = []
            for p in range(len(self.SUM[i])):
                returned.append(math.sqrt(self.SUMQ[i][p]/self.N[i] -  (self.SUM[i][p]/self.N[i])**2))
            DS_std_dict[i] = returned
        
        if len(self.CS) != 0: 
            returned_CS_centroids = {}
            for i in self.CSclassification:
                returned_CS_centroids[i] = self.centroidsCS[i]
            CS_std_dict = {}
            for i in self.CSN:
                returned = []
                for p in range(len(self.CSSUM[i])):
                    returned.append(math.sqrt(self.CSSUMQ[i][p]/self.CSN[i] -  (self.CSSUM[i][p]/self.CSN[i])**2))
                CS_std_dict[i] = returned
        else: 
            self.CSSUM = {}
            CS_std_dict = {}
            returned_CS_centroids = {}
            self.CSclassification = {}

        ##Unassigned data: RS
        if len(self.RS) != 0: 
            unassigned = {}
            for i in self.RS:
                unassigned[i] = self.data[i]
        else: 
            unassigned = {}
        return self.DSclassification, self.CSclassification, self.centroids, returned_CS_centroids, self.RS, unassigned, DS_std_dict,  CS_std_dict, self.CSSUM
#         print("length of points in outliers: ", len(self.RS))
#         print("new inliers: ", new_inliers)
#         print("classification results: ", self.classification_result)
        
    
    def initCentroid(self, points, k, option):
        if option == "DS": 
            self.centroids = {}
            idx = 0
            randomlist = random.sample(range(0, len(points)), k)
            while idx < k:
                self.centroids[idx] = self.data[randomlist[idx]]
                idx += 1
            return randomlist
        elif option == "RS":
            # print("RS points: ", points)
            self.centroidsCS = {}
            idx = 0
            points = list(points)
            lst = []
            k = min(len(points), k)
            # print("points: ", points)
            # print("k: ", k)
            while idx < k:
                self.centroidsCS[idx] = self.data[points[idx]]
                lst.append(points[idx])
                idx += 1
            return lst
    
    def EuclideanDistance(self, pt1, pt2):
        pt1 = self.data[pt1]
        pt2 = pt2
        pt1_distances = pt1[1:]
        pt2_distances = pt2[1:]
        sum_sqrt = sum([(float(pt1_distances[num]) - float(pt2_distances[num]))**2 for num in range(len(pt1_distances))])
        return math.sqrt(sum_sqrt)

    def initClassify(self, points, centers, idx, option): 
        ##First run, no need for duplicate points
        if idx == 0: 
            if option == "DS": 
                initial_points = [int(x[0]) for x in self.centroids.values()]
            elif option == "RS": 
                initial_points = [int(x[0]) for x in self.centroidsCS.values()]  
#                 print("initial points: ", initial_points)
        else: 
            initial_points = []
        ##Centroid Keys for DS and RS
        if option == "DS": 
            centroids_dic = self.centroids
        elif option == "RS": 
            centroids_dic = self.centroidsCS
        classification_result = {}
        if idx == 0: 
            for i in range(len(centers)): 
                classification_result[i] = [centers[i]]
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
            for p in one_cluster_points: 
                test_list = [float(x) for x in self.data[p]]
                c.append(test_list)
            sums = [sum(x) for x in zip(*c)]
            new_center = [x/len(c) for x in sums]
            center[i] = new_center
        return center

    def appendRS(self, final_result):
        inliers = set()
        # print("filter length: ", self.filter_length)
        for i in final_result:
            if (len(final_result[i])) < self.filter_length:
                self.RS.update(final_result[i])
            else: 
                inliers.update(final_result[i])
        return inliers

    def initRS(self, final_result):
        self.RS = set()
        inliers = set()
        for i in final_result:
            if (len(final_result[i])) < self.filter_length:
                self.RS.update(final_result[i])
            else: 
                inliers.update(final_result[i])
        return inliers
    
    def generateDSstats(self, classification):
        N = {}
        SUM = {}
        SUMQ = {}
        for i in classification: 
            N[i] = len(classification[i])
            points_1d = []
            for j in classification[i]: 
                test_list = [float(x) for x in self.data[j]]
                points_1d.append(test_list)
            sums = [sum(x) for x in zip(*points_1d)]
            SUM[i] = sums[1:]
            sumsquare = [x**2 for x in SUM[i]]
            SUMQ[i] = sumsquare
        self.N = N
        self.SUM = SUM
        self.SUMQ = SUMQ
    
    def generateCSstats(self, CS_result): 
        self.RS = set()
        CS = set()
        CS_classification = {}
        for i in CS_result:
            if (len(CS_result[i])) <= 1:
                self.RS.update(CS_result[i])
            else: 
                CS_classification[i] = CS_result[i]
                CS.update(CS_result[i])
        self.CSclassification = CS_classification
        self.CS = CS
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
        self.CSN = CSN
        self.CSSUM = CSSUM
        self.CSSUMQ = CSSUMQ