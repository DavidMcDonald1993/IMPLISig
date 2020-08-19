import os 

import numpy as np
import pandas as pd
import networkx as nx 


from neet.boolean import LogicNetwork


def main():

    num_seeds = 1000

    networks = [os.path.join("datasets", network) 
        for network in ["egfr", "gastric", "tcim"] + \
            ["saccharomyces_cerevisiae_cell_cycle", 
            "schizosaccharomyces_pombe", "mammalian_cortical_development",
            "arabidopsis_thaliana_development", "mouse_myeloid_development", "creb"]] + \
            [os.path.join("synthetic_bow_tie", str(num_core)) 
                for num_core in (6, 10, 15)]

    statistics = []

    for net in networks:
        assert os.path.exists(net), net

        net_stats = []

        if "synthetic_bow_tie" in net:
            networks = (os.path.join(net, "{:03d}".format(seed), "pos_neg")
                for seed in range(num_seeds))

        else:
            networks = (net, )

        for network in networks:

            network_stats = {}

            edgelist_filename = os.path.join(network,
                "edgelist.tsv")
            print ("reading edgelist from", edgelist_filename)
            assert os.path.exists(edgelist_filename)
            graph = nx.read_weighted_edgelist(edgelist_filename,
                delimiter="\t", create_using=nx.DiGraph())

            network_stats.update({"N": len(graph)})
            network_stats.update({"number_of_edges": len(graph.edges())})


            print ("computing degrees")
            degrees = nx.degree(graph)
            print ("computing betweenness centrality")
            bcs = nx.betweenness_centrality(graph)


            network_stats.update({"mean_degree": np.mean([degrees[n] for n in graph])})
            network_stats.update({"mean_betweenness_centrality": np.mean([bcs[n] for n in graph])})
            network_stats.update({"density": nx.density(graph)})

            print ("determining core")
            core = sorted(max(nx.strongly_connected_components(graph), key=len))

            print ("determining in-component")
            in_component = {n for n in graph 
                if nx.has_path(graph, n, core[0]) and n not in core}
            print ("determining out-component")
            out_component = {n for n in graph 
                if nx.has_path(graph, core[0], n) and n not in core}

            assert len(in_component.intersection(out_component)) == 0

            network_stats.update({"in_component_size": len(in_component) })
            network_stats.update({"core_size": len(core) })
            network_stats.update({"out_component_size": len(out_component) })

            core = graph.subgraph(core)

            network_stats.update({"core_mean_degree": np.mean([degrees[n] for n in core])})
            network_stats.update({"core_mean_betweenness_centrality": np.mean([bcs[n] for n in core])})
            network_stats.update({"core_density": nx.density(core)})

            # print ("enumerating number of cycles in core")
            # network_stats.update({"core_num_cycles": len(list(nx.simple_cycles(core)))})

            logic_file = os.path.join(network, 
                "network.txt")
            # assert os.path.exists(logic_file)
            if os.path.exists(logic_file):
                print ("reading logic from", logic_file)
                logic_net = LogicNetwork.read_logic(logic_file)
                
                print ("computing average sensitivity")
                network_stats.update({"average_sensitivity": logic_net.average_sensitivity()})
            else:
                network_stats.update({"average_sensitivity": "--"})

            net_stats.append(pd.Series(network_stats, name=network))

        net_stats = pd.DataFrame(net_stats)
        net_stats_mean = net_stats.mean(0)
        if net_stats.shape[0] > 1:
            net_stats_std = net_stats.std(0)
            for idx in net_stats_mean.index:
                if net_stats_std[idx] == 0:
                    continue
                net_stats_mean[idx] = "${:.03f}_{{\\pm{:.03f}}}$".format(
                    net_stats_mean[idx], net_stats_std[idx])

        statistics.append(net_stats_mean)

        print ()
        
    statistics = pd.DataFrame(statistics)
    statistics.to_csv("network_statistics.csv")

if __name__ == "__main__":
    main()