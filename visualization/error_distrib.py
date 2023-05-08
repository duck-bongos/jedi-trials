from collections import Counter
import matplotlib.pyplot as plt

filename = "data/metrics/non-rigid_distances.txt"
with open(filename, "r") as f:
    r = f.read()
    data = [
        float(line.split(" ")[2])
        for line in r.split("\n")[2:]
        if len(line.split(" ")) == 3
    ]
    counts = Counter(data)

values = list(counts.keys())
counts = list(counts.values())

bins = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90]
plt.hist(values, bins, edgecolor="k")
plt.xticks(bins)
plt.axvline(x=27.664, color="r", label="Average distance")
plt.title("Counts of Distance")
plt.savefig("data/metrics/distances.png")
