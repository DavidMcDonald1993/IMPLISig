import os 

import numpy as np
import pandas as pd 

from scipy.stats import ttest_ind

from matplotlib import pyplot as plt

def set_box_color(bp, color):
    plt.setp(bp['boxes'], color=color)
    plt.setp(bp['whiskers'], color=color)
    plt.setp(bp['caps'], color=color)
    plt.setp(bp['medians'], color=color)

def main():

    # num_core_of_the_core = 3
    core_of_the_core = ["n3", "n4", "n5"] # assume three inputs
    significance = 0.05

    seeds = range(1000)
    feedback_loops = (
        "pos", 
        "neg", 
        "pos_neg", 
        )
    feedback_loop_labels = (
        "POSITIVE",
        "NEGATIVE", 
        "POSITIVE/NEGATIVE", 
        )

    num_cores = (
        6, 
        10, 
        15, 
        # 30 
        )

    for num_core in num_cores:

        group_a = []
        group_b = []
        p_vals = []

        for feedback_loop in feedback_loops:

            filenames = (os.path.join("expressions", 
                "synthetic_bow_tie", 
                str(num_core),
                "{:03d}".format(seed), 
                feedback_loop,
                "p_values.csv")
                for seed in seeds)

            core_of_the_core_counts = []
            other_core_counts = []

            for filename in filenames:
                assert os.path.exists(filename), filename
                print ("reading p values from", filename)
                p_values = pd.read_csv(filename, index_col=0)
                p_values = p_values < significance

                # mean over all outputs
                expected_changed_outputs = p_values.mean(axis=1)

                # core_of_the_core = sorted(expected_changed_outputs.index)\
                #     [:num_core_of_the_core]

                # print (core_of_the_core)
                # raise SystemError

                core_of_the_core_idx = expected_changed_outputs.\
                    index.isin(core_of_the_core)

                core_of_the_core_counts.extend(
                    expected_changed_outputs.loc[
                        core_of_the_core_idx].values)

                other_core_counts.extend(
                    expected_changed_outputs.loc[
                        ~core_of_the_core_idx].values)

            print ("num examples of core of the core", len(core_of_the_core_counts))
            print ("num examples of non core of the core", len(other_core_counts))

            # one sided t test
            t, p = ttest_ind(core_of_the_core_counts, 
                other_core_counts, 
                equal_var=False)
            p = p / 2
            if t < 0: #  one sided
                p = 1 - p

            print ("p_value from t test", p)

            group_a.append(core_of_the_core_counts)
            group_b.append(other_core_counts)
            p_vals.append(p)

        plt.style.use("ggplot")

        plt.figure(figsize=(10, 5))

        bpl = plt.boxplot(group_a, notch=True, whis=1.5,
            positions=np.array(range(len(group_a)))*2.0-0.4, sym='', widths=0.6)
        bpr = plt.boxplot(group_b, notch=True, whis=1.5,
            positions=np.array(range(len(group_b)))*2.0+0.4, sym='', widths=0.6)
        set_box_color(bpl, '#D7191C') # colors are from http://colorbrewer2.org/
        set_box_color(bpr, '#2C7BB6')

        # draw temporary red and blue lines and use them to create a legend
        plt.plot([], c='#D7191C', label='A: Core feedback loop')
        plt.plot([], c='#2C7BB6', label='B: Other core nodes')
        plt.legend(loc="lower right")

        plt.xticks(range(0, len(feedback_loops) * 2, 2), 
            # ["Synthetic$_{{NUM\_CORE={}}}$\np-val: {:.04E}".format(num_core, p_val)
            ["Synthetic$_{{LOOP={}}}$\n".format(feedback_loop) + \
                "Mean A: {:.03f}\n".format(np.mean(a)) + \
                "Mean B: {:.03f}\n".format(np.mean(b)) +\
                    "One-sided p-val: {:.04E}".format(p_val)
                for feedback_loop, a, b,  p_val in zip(feedback_loop_labels, group_a, group_b, p_vals)])
        plt.xlim(-2, len(feedback_loops)*2)
        plt.ylabel("Proportion of changed outputs")
        plt.ylim(-0.1, 1.1)
        plt.tight_layout()
        filename = "boxcompare_num_core={}.png".format(num_core)
        print ("writing to", filename)
        plt.savefig(filename)

if __name__ == "__main__":
    main()