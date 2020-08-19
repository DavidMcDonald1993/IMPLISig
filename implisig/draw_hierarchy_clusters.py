import os

import networkx as nx
from networkx.drawing.nx_agraph import to_agraph

import pickle as pkl

from IMPLISig import unpack, load_graph

def main():

    # mode = "pos_neg"

    networks = ["egfr", "gastric", "tcim", ] + \
        ["saccharomyces_cerevisiae_cell_cycle",
        "schizosaccharomyces_pombe", 
        "mammalian_cortical_development", 
        "arabidopsis_thaliana_development", 
        "mouse_myeloid_development",
        "creb"]

    output_dir = os.path.join("hierarchical_cluster_plots")

    for network in networks:

        network_output_dir = os.path.join(output_dir, network)
        os.makedirs(network_output_dir, exist_ok=True)

        edgelist_filename = os.path.join("datasets", network,
            "edgelist.tsv")
        assert os.path.exists(edgelist_filename)
        g = load_graph(edgelist_filename)
        nx.set_edge_attributes(g, name="arrowhead",
            values={(u, v): ("normal" if w>0 else "tee") 
                for u, v, w in g.edges(data="weight")})

        g.graph['edge'] = {'arrowsize': '.8', 
                'splines': 'curved'}
        g.graph['graph'] = {'scale': '3'}

        core = sorted(max(nx.strongly_connected_components(g), key=len))
        in_component = {n for n in g
            if n not in core and nx.has_path(g, n, core[0])}
        out_component = {n for n in g
            if n not in core and nx.has_path(g, core[0], n)}

        a = to_agraph(g)

        components = []
        subgraphs = []

        if len(core) > 0:
            core_subgraph = a.add_subgraph(name="cluster_core", 
                label="Core")
            core_subgraph.add_nodes_from(core)

            components.append("core")
            subgraphs.append(core_subgraph)

        if len(in_component) > 0:
            in_subgraph = a.add_subgraph(name="cluster_in", 
                label="In-Component", color="red")
            in_subgraph.add_nodes_from(in_component)
            
            components.append("in")
            subgraphs.append(in_subgraph)

        if len(out_component) > 0:
            out_subgraph = a.add_subgraph(name="cluster_out", 
                label="Out-Component", color="blue")
            out_subgraph.add_nodes_from(out_component)

            components.append("out")
            subgraphs.append(out_subgraph)

        for component, subgraph in zip(components, subgraphs):

            if component == "core":
                mode = "pos_neg"
            else:
                mode = "all"

            hierarchy_filename = os.path.join("implisig_output",
                network, component, mode, "hierarchy.pkl")
            print ("reading hierarchy from", hierarchy_filename)
            assert os.path.exists(hierarchy_filename), hierarchy_filename

            hierarchy = load_graph(hierarchy_filename)
            assert nx.is_tree(hierarchy)

            root = [n for n in hierarchy if hierarchy.out_degree(n)==0][0]
            assert root in hierarchy
            assert hierarchy.out_degree(root) == 0
            depths = {n: 
                nx.shortest_path_length(hierarchy, n, root, )
                for n in hierarchy}
            nodes_sorted = filter(lambda x: x is not root and len(unpack(x))>1,
                sorted(depths, key=depths.get, reverse=False))
            node_to_subgraph = {root: subgraph}

            for node in nodes_sorted:
                parent = list(hierarchy.neighbors(node))[0]
                assert parent in node_to_subgraph
                parent_subgraph = node_to_subgraph[parent]
                child_subgraph = parent_subgraph.add_subgraph(
                    name="cluster_{}".format(node), 
                    label="{}-{}".format(component, depths[node]))
                child_subgraph.add_nodes_from(unpack(node))
                node_to_subgraph.update({node: child_subgraph})

            # draw component
            draw_filename = os.path.join(network_output_dir,
                "{}_decomposition.png".format(component))
            print ("drawing to", draw_filename)

            subgraph = subgraph.copy()

            for u, v, arrowhead in g.edges(data="arrowhead"):
                if u in subgraph and v in subgraph:
                    subgraph.add_edge(u, v, arrowhead=arrowhead)

            subgraph.layout("dot")
            subgraph.draw(draw_filename)
        
        # draw overall network
        draw_filename = os.path.join(network_output_dir,
            "network_decomposition.png")
        print ("drawing to", draw_filename)
        
        a.layout("dot")
        a.draw(draw_filename)

        




if __name__ == "__main__":
    main()