import os 

import networkx as nx
from networkx.drawing.nx_agraph import to_agraph

import pickle as pkl

def main():
    
    networks = ["egfr", "gastric", "tcim"] + \
        ["saccharomyces_cerevisiae_cell_cycle",
        "schizosaccharomyces_pombe",
        "mammalian_cortical_development",
        "arabidopsis_thaliana_development", 
        "mouse_myeloid_development",
        "creb"]

    for network in networks:
        data_dir = os.path.join("datasets", network)

        edgelist_filename = os.path.join(data_dir, "edgelist.tsv")
        print ("reading edgelist from", edgelist_filename)
        assert os.path.exists(edgelist_filename)

        g = nx.read_weighted_edgelist(edgelist_filename, delimiter="\t",
            create_using=nx.DiGraph())
        
        nx.set_edge_attributes(g, name="arrowhead",
                values={(u, v): ("normal" if w>0 else "tee") 
                    for u, v, w in g.edges(data="weight")})

        core = sorted(max(nx.strongly_connected_components(g), key=len))
        in_component = {n for n in g
            if n not in core and nx.has_path(g, n, core[0])}
        out_component = {n for n in g
            if n not in core and nx.has_path(g, core[0], n)}

        core = g.subgraph(core)
        in_component = g.subgraph(in_component)
        out_component = g.subgraph(out_component)

        for name, component in zip(("core", "in", "out"),
            (core, in_component, out_component)):

            filename = os.path.join(data_dir, "{}.gml".format(name))
            print("writing edgelist to", filename)
            nx.write_gml(component, filename)

            draw_filename = os.path.join(data_dir, "{}.png".format(name))
            print ("saving drawing to", draw_filename)

            component.graph['edge'] = {'arrowsize': '.8', 
                    'splines': 'curved'}
            component.graph['graph'] = {'scale': '3'}

            a = to_agraph(component)
            a.layout("dot")
            a.draw(draw_filename)

            print ()

        a = to_agraph(g)
    
        if len(core) > 0:
            core_subgraph = a.add_subgraph(name="cluster_core", 
                label="Core")
            core_subgraph.add_nodes_from(core)


        if len(in_component) > 0:
            in_subgraph = a.add_subgraph(name="cluster_in", 
                label="In-Component", color="red")
            in_subgraph.add_nodes_from(in_component)
            

        if len(out_component) > 0:
            out_subgraph = a.add_subgraph(name="cluster_out", 
                label="Out-Component", color="blue")
            out_subgraph.add_nodes_from(out_component)


        a.layout("dot")
        a.draw(os.path.join(data_dir, "whole_network.png"))



if __name__ == "__main__":
    main()