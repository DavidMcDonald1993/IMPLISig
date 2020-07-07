import os 
import argparse

import numpy as np
import pandas as pd 
import networkx as nx 


from sklearn.metrics import roc_auc_score, average_precision_score


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("--output", type=str, 
        default="control_kernel_results")

    return parser.parse_args()

def main():

    args = parse_args()

    output_dir = args.output
    if not os.path.exists(output_dir):
        print ("making dir", output_dir)
        os.makedirs(output_dir)

    micro_feature_names = ("$k$", "$k_{{\\text{{in}}}}$", "$k_{{\\text{{out}}}}$",
        "cn", "cc")
    # implisig_variations = ("pos_neg", "pos", "neg", "all")
    implisig_variations = ("pos_neg", )

    metrics = (
        ("AUROC", roc_auc_score),
        ("AP", average_precision_score)
    )

    networks = ("saccharomyces_cerevisiae_cell_cycle", "schizosaccharomyces_pombe",
        "mammalian_cortical_development", "arabidopsis_thaliana_development",
        "mouse_myeloid_development")

    for metric_name, metric in metrics:

        scores = []

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

            control_kernels_filename = os.path.join("datasets", 
                network,
                "control_kernels.csv")
            print ("reading control kernels from", control_kernels_filename)
            assert os.path.exists(control_kernels_filename)
            control_kernels = pd.read_csv(control_kernels_filename, index_col=0)
        
            control_kernels = control_kernels.any(1) # appears in at least one kernel?
            target_nodes = control_kernels.index 

            degrees_of_core = [degrees[n] for n in target_nodes]
            in_degrees_of_core = [graph.in_degree(n) for n in target_nodes]
            out_degrees_of_core = [graph.out_degree(n) for n in target_nodes]
            core_numbers_of_core = [core_numbers[n] for n in target_nodes]
            bcs_of_core = [bcs[n] for n in target_nodes]

            micro_feature_ranks = [
                degrees_of_core,
                in_degrees_of_core,
                out_degrees_of_core,
                core_numbers_of_core,
                bcs_of_core,
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
                assert merge_depths.shape[0] == control_kernels.shape[0], (merge_depths.shape, control_kernels.shape)
                implisig_ranks.append(merge_depths)

            network_scores = []

            for rank_name, rank in zip(
                micro_feature_names + implisig_variations, 
                    micro_feature_ranks + implisig_ranks):

                network_scores.append(pd.Series(
                    [metric(control_kernels, rank)],
                        name=rank_name, index=[network]))

            scores.append(pd.DataFrame(network_scores))

        scores = pd.concat(scores, axis=1)

        ranks = scores.rank(axis=0, 
            ascending=False, 
            method="min")

        scores["Mean {}".format(metric_name)] = scores.mean(1)
        ranks["Mean Rank"] = ranks.mean(1)
        
        scores.to_csv(os.path.join(output_dir, 
            "{}.csv".format(metric_name)))
        ranks.to_csv(os.path.join(output_dir, 
            "{}_ranks.csv".format(metric_name)))
     

if __name__ == "__main__":
    main()