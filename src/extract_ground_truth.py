import json
import os

from digitizer.digitization import annotation_to_thresholds

if __name__ == "__main__":
    for filename in os.listdir("../data/annotations_test"):
        thresholds = annotation_to_thresholds(json.load(open(f"../data/annotations_test/{filename}")))
        thresholds_list = []
        for threshold in thresholds:
            thresholds_list.append([threshold["ear"], threshold["conduction"], threshold["masking"], threshold["frequency"], threshold["threshold"]])
        
        with open(f"../data/ground_truth/{filename.split('.')[0]}.csv", "w") as ofile:
            ofile.write(f"ear,conduction,masking,frequency,threshold\n")
            for t in thresholds_list:
                ofile.write(f"{t[0]},{t[1]},{t[2]},{t[3]},{t[4]}\n")