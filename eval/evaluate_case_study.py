import os 
import argparse

import numpy as np
import pandas as pd 
import networkx as nx 

from sklearn.metrics import roc_auc_score, average_precision_score

def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("--output", type=str, 
        default="case_study_results")

    return parser.parse_args()

def main():

    significance = 0.05

    args = parse_args()

    output_dir = args.output
    if not os.path.exists(output_dir):
        print ("making dir", output_dir)
        os.makedirs(output_dir)

    micro_feature_names = ("$k$", 
        "$k_{{\\text{{in}}}}$",
        "$k_{{\\text{{out}}}}$",
        "bc", 
        "cc",
        "cn")
    # implisig_variations = ("pos_neg", "pos", "neg", "all")
    implisig_variations = ("pos_neg", 
        # "neg_pos"
        )

    metrics = (
        ("AUROC", roc_auc_score),
        ("AP", average_precision_score)
    )

    networks = (
        # "gastric", 
        # "egfr", 
        # "tcim", 
        # "bladder", 
        # "liver"
        "creb",
        )

    for network in networks:

        edgelist_filename = os.path.join("datasets",
            network, 
            "edgelist.tsv")
        print ("reading graph from", edgelist_filename)
        assert os.path.exists(edgelist_filename)
        graph = nx.read_weighted_edgelist(edgelist_filename,
            delimiter="\t", 
            create_using=nx.DiGraph())

        degrees = nx.degree(graph)
        bcs = nx.betweenness_centrality(graph)
        ccs = nx.clustering(graph)
        graph.remove_edges_from(nx.selfloop_edges(graph))
        core_numbers = nx.core_number(graph)

        p_val_filename = os.path.join(
            "expressions", 
            network,
            "p_values.csv")
        print ("reading p-values from", p_val_filename)
        assert os.path.exists(p_val_filename)
        p_values = pd.read_csv(p_val_filename, index_col=0)
        p_values = p_values < significance
        output_nodes = p_values.columns
        target_nodes = p_values.index

        # filter out any targets with no significant change in expression
        idx = np.logical_and(p_values.any(0), (1-p_values).any(0))
        assert idx.any(), idx
        output_nodes = output_nodes[idx]

        degrees_of_core = [degrees[n] for n in target_nodes]
        in_degrees_of_core = [graph.in_degree(n) for n in target_nodes]
        out_degrees_of_core = [graph.out_degree(n) for n in target_nodes]
        bcs_of_core = [bcs[n] for n in target_nodes]
        ccs_of_core = [ccs[n] for n in target_nodes]
        core_numbers_of_core = [core_numbers[n] for n in target_nodes]


        micro_feature_ranks = [
            degrees_of_core,
            in_degrees_of_core,
            out_degrees_of_core,
            bcs_of_core,
            ccs_of_core,
            core_numbers_of_core,
        ]

        implisig_ranks = []
        for implisig_variation in implisig_variations:
            merge_depths_filename = os.path.join(
                "implisig_output",
                network, 
                implisig_variation, 
                "merge_depths.csv")
            print ("reading merge depths from", merge_depths_filename)
            assert os.path.exists(merge_depths_filename)
            merge_depths = pd.read_csv(merge_depths_filename, index_col=0)["0"]
            merge_depths = merge_depths.loc[target_nodes]
            assert merge_depths.shape[0] == p_values.shape[0], (merge_depths.shape, p_values.shape)
            implisig_ranks.append(merge_depths)

        for metric_name, metric in metrics:

            scores = []

            for rank_name, rank in zip(
                micro_feature_names + implisig_variations, 
                    micro_feature_ranks + implisig_ranks):

                scores.append(pd.Series(
                    [metric(p_values[output_node], rank) 
                        for output_node in output_nodes],
                    name=rank_name, index=output_nodes))

            scores = pd.DataFrame(scores)

            ranks = scores.rank(axis=0, 
                ascending=False, 
                method="min")

            scores["Mean {}".format(metric_name)] = scores.mean(1)
            ranks["Mean Rank"] = ranks.mean(1)
            
            scores.to_csv(os.path.join(output_dir, 
                "{}_{}.csv".format(network, metric_name)))
            ranks.to_csv(os.path.join(output_dir, 
                "{}_{}_ranks.csv".format(network, metric_name)))
     

if __name__ == "__main__":
    main()