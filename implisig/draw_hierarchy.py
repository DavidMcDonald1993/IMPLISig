import os

import networkx as nx
from networkx.drawing.nx_agraph import to_agraph

import pickle as pkl

from IMPLISig import unpack, load_graph

def main():

    mode = "pos_neg"
    # networks = ["egfr", "gastric", "tcim", "creb"]
    networks = ["creb"]

    output_dir = os.path.join("hierarchy_plots")

    for network in networks:

        network_output_dir = os.path.join(output_dir, network)
        os.makedirs(network_output_dir, exist_ok=True)

        edgelist_filename = os.path.join("datasets", network,
            "edgelist.tsv")
        assert os.path.exists(edgelist_filename)
        # g = nx.read_weighted_edgelist(edgelist_filename, 
            # delimiter="\t", create_using=nx.DiGraph(), nodetype=str)
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

        for component in ["core", "in", "out"]:

            component_output_dir = os.path.join(network_output_dir, 
                component)
            os.makedirs(component_output_dir, exist_ok=True)

            component_edgelist_filename = os.path.join("datasets", 
                network, 
                "{}.gml".format(component))
            print ("reading component from", component_edgelist_filename)
            assert os.path.exists(component_edgelist_filename)
            # component_network = nx.read_weighted_edgelist(component_edgelist_filename, 
                # delimiter="\t", create_using=nx.DiGraph())
            component_network = load_graph(component_edgelist_filename)
            if len(component_network) == 0:
                continue

            nx.set_edge_attributes(component_network, name="arrowhead",
                values={(u, v): ("normal" if w>0 else "tee") 
                    for u, v, w in component_network.edges(data="weight")})

            component_network.graph['edge'] = {'arrowsize': '.8', 
                    'splines': 'curved'}
            component_network.graph['graph'] = {'scale': '3'}

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
                nx.shortest_path_length(hierarchy, n, root)
                for n in hierarchy}
            nodes_sorted = sorted(depths, key=depths.get, reverse=True)
            node_to_id = {n: i for i, n in enumerate(nodes_sorted)}

            for node in nodes_sorted:
                
                draw_filename = os.path.join(component_output_dir, 
                    "{}_{}.png".format(component, node_to_id[node]))

                subnetwork = nx.DiGraph(component_network.subgraph(unpack(node)))

                if isinstance(node, frozenset):


                    for idx, group in enumerate(filter(lambda n: isinstance(n, frozenset), node)):

                        subnetwork.add_node("subnetwork_{}".format(idx),
                            label="", image=os.path.join(component_output_dir, 
                                "{}_{}.png".format(component, node_to_id[group])))

                        group = unpack(group)
                        for n_ in group:

                            new_edges = []

                            for _, v, arrowhead in subnetwork.out_edges(n_, data="arrowhead"):
                                if v in group: 
                                    continue
                                new_edges.append(("subnetwork_{}".format(idx), v, 
                                    {"arrowhead": arrowhead}))
                            for u, _, arrowhead in subnetwork.in_edges(n_, data="arrowhead"):
                                if u in group:
                                    continue
                                new_edges.append((u, "subnetwork_{}".format(idx), 
                                    {"arrowhead": arrowhead}))

                            subnetwork.remove_node(n_)
                            subnetwork.add_edges_from(new_edges)


                a = to_agraph(subnetwork)
                a.layout("dot")
                a.draw(draw_filename)

            
            draw_filename = os.path.join(network_output_dir,
                "{}.png".format(component))
            print ("drawing to", draw_filename)
            
            a = to_agraph(subnetwork)
            a.layout("dot")
            a.draw(draw_filename)

            # replace all edges to/from this component in original graph
            g.add_node(component, label="",
                image=draw_filename)

            for n in component_network:
                new_edges = []

                for _, v, arrowhead in g.out_edges(n, data="arrowhead"):
                    if v in component_network: 
                        continue
                    new_edges.append((component, v, {"arrowhead": arrowhead}))
                for u, _, arrowhead in g.in_edges(n, data="arrowhead"):
                    if u in component_network:
                        continue
                    new_edges.append((u, component, {"arrowhead": arrowhead}))

                g.remove_node(n)
                g.add_edges_from(new_edges)

            print ()
        
        # draw overall network
        draw_filename = os.path.join(network_output_dir,
            "network.png")
        print ("drawing to", draw_filename)
        
        g.graph['edge'] = {'arrowsize': '.8', 
            'splines': 'curved'}
        g.graph['graph'] = {'scale': '3'}

        a = to_agraph(g)
        a.layout("dot")
        a.draw(draw_filename)

        




if __name__ == "__main__":
    main()