from pathlib import Path
import os
import sys
import re

import numpy as np
import pandas as pd
import scipy.stats as ss
import seaborn as sns
from matplotlib import pyplot as plt

BOUNDARIES = {"custom": 0, "outer": 1, "inner": 2, "middle": 3}
METHODS = {
    "consistent": 0,
    "left_forehead": 1,
    "right_forehead": 2,
    "center_forehead": 3,
    "left_cheek": 4,
    "right_cheek": 5,
    "chin": 6,
}
MTHDX = {v: k for k, v in METHODS.items()}
labels = (
    "consistent" "left_cheek",
    "left_mouth_corner",
    "mid_top_lip",
    "right_cheek",
    "right_mouth_corner",
)


def get_sum(path: str):
    d: float
    with open(path) as f:
        d = float(f.readlines()[-1])
    return d


def get_boundary_idx(name: str):
    spl = name.split("_")
    for item in spl:
        if item in BOUNDARIES:
            return BOUNDARIES[item]


def get_method_idx(name: str):
    key = "consistent"
    for k, v in METHODS.items():
        if k in name:
            key = k
            break
    return METHODS[key]


def build_data():
    dirpath = "../../data"
    # 10 patients (p), 7 methods (m), 4 boundaries (b)
    p_idx = 0
    data = np.zeros((4, 10, 7))
    for dir in os.listdir(dirpath):
        if not os.path.isfile(dir) and "patient" in dir:
            d = dirpath + f"/{dir}/statistics/data/statistics"
            for f in os.listdir(d):
                if f.endswith(".txt"):
                    full = os.path.join(d, f)
                    s = get_sum(full)
                    b_idx = get_boundary_idx(f)
                    m_idx = get_method_idx(f)
                    data[b_idx, p_idx, m_idx] = s
            p_idx += 1
    return data


def build_comparison_vectors(arr: np.ndarray):
    # consistent is first column
    e = arr[:, 0]
    pairs = []
    for col in range(1, arr.shape[1]):
        o = arr[:, col]
        o_ = []
        e_ = []
        for i in range(arr.shape[0]):
            if e[i] > 0 and o[i] > 0:
                o_.append(o[i])
                e_.append(e[i])
        o_ = np.array(o_)
        e_ = np.array(e_)
        pairs.append((col, (e_, o_)))

    return pairs


def paired_t_test(
    exp: np.ndarray,
    obs: np.ndarray,
):
    t_statistic, p_value = ss.ttest_rel(exp, obs, alternative="less")
    return t_statistic, p_value


ALPHAS = (0.10, 0.15, 0.20)
if __name__ in "__main__":
    # zeroth method, all patients, all inconsistent boundaries taken
    data = build_data()

    p_values = np.zeros((4, 6))
    for k, v in BOUNDARIES.items():
        # print(k, data[v])
        pairs = build_comparison_vectors(data[v])
        # shape (4 x 6)
        for c, (e, o) in pairs:
            m = MTHDX[c]
            t_statistic, p_value = paired_t_test(e, o)
            # print(f"T-Statistic: {t_statistic} | P-Value: {p_value}\n")
            p_values[v, c - 1] = p_value
            """
            out = ""
            for a in ALPHAS:
                choice = ""
                if a > p_value:
                    choice = "Accept"
                else:
                    choice = "Reject"
                out += f"{choice} null hypothesis for [{k} {}] at significance level {a}: P-value: {p_value}\n"

            out += "\n"
            """
    df = pd.DataFrame(p_values)
    df.columns = [v for k, v in MTHDX.items() if k > 0]
    df.index = list(BOUNDARIES.keys())
    df.to_csv("p_values.csv")

    plt.figure(figsize=(20, 15))
    hm = sns.heatmap(
        df, annot=True, fmt=".6f", cmap="Blues", annot_kws={"fontsize": 18}
    )
    hm.tick_params(labelsize=18)
    plt.title("P-values by Inconsistent Boundary Method and Boundary", fontsize=30)
    plt.ylabel("Boundary Type", fontsize=25)
    plt.xlabel("Inconsistent Boundary Method", fontsize=25)
    fig = hm.get_figure()

    fig.savefig("hm.png")
