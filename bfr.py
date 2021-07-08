import sys
from os import listdir
from os.path import isfile, join
import math
from Kmeans import Kmeans
from BFRClass import BFRClass
from FinalMerge import FinalMerge
import time
import json
import csv

start_time = time.time()
inputs = sys.argv
# input_folder = inputs[1]
# n_clusters = int(inputs[2])
# output_file = inputs[3]
# intermediate_file = inputs[4]
input_folder = "./data/test1/"
n_clusters = 10
intermediate_file = "intermediate_test1.csv"
output_file = "output_test1.json"


files = [input_folder + f for f in listdir(input_folder)]
one_file = files[0]
f = open(one_file)
data = list(f)
print("number of dimensions: ", len(data[0].split(",")) - 1)
f.close()
print("Number of points: ", len(data))

ten_percent = min(10000, math.ceil(len(data)*0.1))
sample = data[0:ten_percent]
remaining = data[ten_percent:]
# print(len(sample))
# print(len(remaining))

##First file info
DSclassification, CSclassification, DScentroids, CScentroids, RS, unassigned_data, DS_std, CS_std, CS_SUM= Kmeans(n_clusters, sample).fit()
while (n_clusters - 1) not in DS_std or DS_std[n_clusters - 1][0] == 0.0: 
    DSclassification, CSclassification, DScentroids, CScentroids, RS, unassigned_data, DS_std, CS_std, CS_SUM= Kmeans(n_clusters, sample).fit()   
DS, CS, RS, CScentroids, CS_SUM, CS_std, unassigned_data = BFRClass(remaining,n_clusters, DSclassification, CSclassification, DScentroids, CScentroids, RS, unassigned_data, DS_std, CS_std, CS_SUM).fit()
DS_count = sum([len(set(DS[x])) for x in DS])
CS_count = sum([len(CS[x]) for x in CS])
RS_count = len(RS)
print("DS: ", DS_count, " CS: ", CS_count, " RS: ", RS_count)
print("Total: ", DS_count+ CS_count+ RS_count)

header = "round_id,nof_cluster_discard,nof_point_discard,nof_cluster_compression,nof_point_compression,nof_point_retained".split(",")
with open(intermediate_file, 'w+') as csvfile: 
    csvwriter = csv.writer(csvfile) 
    csvwriter.writerow(header)
    csvwriter.writerow([1,len(DS),DS_count,len(CS),CS_count,RS_count])

    ##Intermediate result
    idx = 2
    for fi in files[1:]:
        print(fi)
        f = open(fi)
        data = list(f)
        # print("length of points: ", len(data))
        f.close()
        # print("previous unassigned: ", unassigned_data)
        DS, CS, RS, CScentroids, CS_SUM, CS_std, unassigned_data = BFRClass(data,n_clusters, DS, CS, DScentroids, CScentroids, RS, unassigned_data, DS_std, CS_std, CS_SUM).fit()
        DS_count = sum([len(set(DS[x])) for x in DS])
        CS_count = sum([len(CS[x]) for x in CS])
        RS_count = len(RS)
        # print(CSclassification)
        print("DS: ", DS_count, " CS: ", CS_count, " RS: ", RS_count)
        print("Total: ", DS_count+ CS_count+ RS_count)
        # print("\n")
        csvwriter.writerow([idx,len(DS),DS_count,len(CS),CS_count,RS_count])
        idx += 1

##Step 13: Final Merge 
DS = FinalMerge(DS, CS, RS, DScentroids, CScentroids, DS_std, unassigned_data).classify()

##Write to file
op = open(output_file, "w+")
written = {}
for i in DS:
    points = DS[i]
    for pt in points: 
        written[pt] = i
written = sorted(written.items(), key =lambda kv:kv[0])
written = {str(key): value for key, value in written}
json.dump(written, op)
op.close()

print("Duration: ", "{:.1f}".format(time.time() - start_time), " s")