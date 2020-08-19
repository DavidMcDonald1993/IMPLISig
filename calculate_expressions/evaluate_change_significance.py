import os

import glob

import numpy as np 
import pandas as pd 
import networkx as nx

from scipy.stats import ttest_rel # paired ttest

import argparse

def load_dfs(df_directory):

    print ("loading data from directory", df_directory)

    dfs = {}

    full_dfs = glob.glob(os.path.join(df_directory, 
        "*expressions.csv.gz"))
    # if len(full_dfs) == 0:

    #     print ("full dataframes not found, loading chunks from directory",
    #         os.path.join(df_directory, "chunks"))

    #     for f in glob.iglob(os.path.join(df_directory, "chunks",
    #         "*chunk*.csv")):
    #         _file = f.split("/")[-1]
    #         output_node = _file.split("_expressions")[0]
    #         df = pd.read_csv(f, index_col=0)
    #         if output_node in dfs:
    #             dfs[output_node] = dfs[output_node].append(df)
    #         else:
    #             dfs[output_node] = df
    #         print ("read", _file)

    #     for output_node, df in dfs.items():
    #         df.to_csv(os.path.join(df_directory, 
    #             "{}_expressions_full.csv".format(output_node)))

    # else:
    assert len(full_dfs) > 0
    print ("loading full dataframes")
    for full_df in full_dfs:
        _file = full_df.split("/")[-1]
        output_node = _file.split("_expressions")[0]
        dfs[output_node] = pd.read_csv(full_df, index_col=0)
        print ("read", _file)

    return dfs

def evaluate_change_significance(dfs, 
    pro_cancer_outputs, 
    anti_cancer_outputs,
    output_dir,
    one_tailed=True):

    print ("evaluating change significance",
        "using paired ttest")

    p_value_df = pd.DataFrame()

    for output_node, df in dfs.items():

        if output_node not in pro_cancer_outputs.union(
            anti_cancer_outputs):
            continue

        print ("processing output node ", output_node)

        target_set_p_values = {}

        control_expressions = df.loc["control"]

        target_sets = set(df.index) - {"control"} 

        print ("number of target sets:", len(target_sets))

        for target_set in target_sets:

            print ("processing target set", target_set,
                "for output", output_node)

            target_set_expressions = df.loc[target_set]
            
            if control_expressions.equals(target_set_expressions):
                p_value = 1. # no change in expression
            else:
                if output_node in anti_cancer_outputs:
                    # expect increase in expression
                    # target set > control
                    t_statistic, p_value = ttest_rel(
                        target_set_expressions, 
                        control_expressions,
                        nan_policy="omit",
                        # equal_var=False
                        )
                else:
                    assert output_node in pro_cancer_outputs, output_node
                    # expect decrease in expression
                    # control_expressions > target_set
                    t_statistic, p_value = ttest_rel(
                        control_expressions, 
                        target_set_expressions, 
                        nan_policy="omit",
                        # equal_var=False
                        )

                assert not np.isnan(p_value), t_statistic

                if one_tailed:
                    p_value /= 2 # one tailed ttest
                    if t_statistic < 0:
                        p_value = 1 - p_value

            assert target_set not in target_set_p_values

            target_set_p_values.update(
                {target_set: p_value})
        
        p_value_df[output_node] = pd.Series(target_set_p_values) 

    rank_df = p_value_df.rank(axis=0, 
        ascending=True, method="min")
    mean_rank_df = rank_df.mean(axis=1) # mean over all outputs
    mean_rank_df = mean_rank_df.sort_values(ascending=True)
    
    p_value_df_filename = os.path.join(output_dir, 
        "p_values.csv")
    print ("writing p-values to", p_value_df_filename)
    p_value_df.to_csv(p_value_df_filename)

    rank_df_filename = os.path.join(output_dir, 
        "ranks.csv")
    print ("writing ranks to", rank_df_filename)
    rank_df.to_csv(rank_df_filename)

    mean_rank_filename = os.path.join(output_dir,
        "mean_ranks.csv")
    print ("writing mean ranks to", mean_rank_filename)
    mean_rank_df.to_csv(mean_rank_filename)

    # # split up by number of genes
    # splits = [s.split("+") for s in p_value_df.index]

    # for n_genes in (1, 2, 3):

    #     idx = [len(s) == n_genes for s in splits]

    #     p_value_df_n_genes = p_value_df.loc[idx]

    #     rank_df_n_genes = p_value_df_n_genes.rank(
    #         axis=0, ascending=True, method="min")
    #     mean_rank_df_n_genes = rank_df_n_genes.mean(axis=1) # mean over all outputs
    #     mean_rank_df_n_genes = mean_rank_df_n_genes.\
    #         sort_values(ascending=True)

    #     p_value_df_filename = os.path.join(output_dir, 
    #         "p_values_{}_targets.csv".format(n_genes))
    #     print ("writing p-values to", p_value_df_filename)
    #     p_value_df_n_genes.to_csv(p_value_df_filename)

    #     rank_df_filename = os.path.join(output_dir, 
    #         "rank_dataframe_{}_targets.csv".format(n_genes))
    #     print ("writing ranks to", rank_df_filename)
    #     rank_df_n_genes.to_csv(rank_df_filename)

    #     mean_rank_filename = os.path.join(output_dir,
    #         "mean_ranks_{}_targets.csv".format(n_genes))
    #     print ("writing mean ranks to", mean_rank_filename)
    #     mean_rank_df_n_genes.to_csv(mean_rank_filename)

def parse_args():
    '''
    Parse from command line
    '''
    parser = argparse.ArgumentParser(
        description="Evaluate targeted networks")

    parser.add_argument("-d", "--df_directory", 
        dest="df_directory", 
        type=str, default=None,
        help="Directory to load results.")

    return parser.parse_args()


def main():

    args = parse_args()
    directory = args.df_directory

    dfs = load_dfs(directory)

    if "gastric" in directory:
        pro_cancer_outputs = {"RSK", "TCF", "cMYC"}
        anti_cancer_outputs = {"Caspase8", "Caspase9", "FOXO"}
        one_tailed = True
    elif "egfr" in directory:
        pro_cancer_outputs = {"elk1", "creb", "ap1",
            "cmyc", "p70s6_2", "hsp27"}
        anti_cancer_outputs = {"pro_apoptotic"}
        one_tailed = True
    elif "tcim" in directory:
        pro_cancer_outputs = {
            # "Migration", 
            "Metastasis", 
            # "Invasion",
            }
        anti_cancer_outputs = {"CellCycleArrest", "Apoptosis"}
        one_tailed = True
    elif "liver" in directory:
        pro_cancer_outputs = {"BAD", "Myc", "CyclinD1",
            "MCL_1"}
        anti_cancer_outputs = {"BIM", "p27Kip1"}
        one_tailed = True
    elif "bladder" in directory:
        pro_cancer_outputs = {"Proliferation", }
        anti_cancer_outputs = {
            "Apoptosis_b1", 
            "Apoptosis_b2",
            "Growth_Arrest", }
        one_tailed = True
    elif "creb" in directory:
        pro_cancer_outputs = {"CREB"}
        anti_cancer_outputs = {}
        one_tailed = False
    else:
        assert "synthetic" in directory
        pro_cancer_outputs = set(dfs.keys())
        anti_cancer_outputs = set()
        one_tailed = False # do not consider direction

    for output in pro_cancer_outputs.union(anti_cancer_outputs):
        assert output in dfs.keys(), output 

    evaluate_change_significance(dfs,
        pro_cancer_outputs, anti_cancer_outputs, directory, 
        one_tailed=one_tailed)


if __name__ == "__main__":
    main()