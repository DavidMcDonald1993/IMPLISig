import numpy as np 
import networkx as nx 

# from networkx.drawing.nx_agraph import to_agraph
import os

import argparse

def build_core(graph,
    core_nodes,
    num_core_of_the_core,
    feedback_type):

    # core edges
    core_subgraph = graph.subgraph(core_nodes)
    
    all_core_nodes = set(core_nodes)

    core_of_the_core = core_nodes[:num_core_of_the_core]
    print ("core of the core is ",
        core_of_the_core)

    covered_core = set(core_of_the_core)
    all_core_nodes -= covered_core

    while len(all_core_nodes) > 0:

        start, end = np.random.choice(
            sorted(covered_core), 
            size=2, replace=False)

        # cycle_size = np.random.choice(range(1, 6))
        cycle_size = 1
        cycle_size = min(cycle_size, len(all_core_nodes))
        cycle = list(np.random.choice(
            sorted(all_core_nodes),
            size=cycle_size, 
            replace=False))

        assert all([n not in covered_core for n in cycle])
        
        covered_core = covered_core.union(cycle)
        all_core_nodes -= set(cycle)

        cycle = [start] + cycle + [end]

        weights = np.random.choice([-1, 1], size=len(cycle) - 1)
        # ensure not coherent
        if (weights==1).all():
            idx = np.random.choice(len(weights))
            weights[idx] = -1
        if (weights==-1).all():
            idx = np.random.choice(len(weights))
            weights[idx] = 1
        assert not (weights==1).all()
        assert not (weights==-1).all()

        for u, v, w in zip(cycle[:-1], cycle[1:], weights):
            graph.add_edge(u, v, weight=w)
        
        # assert nx.is_strongly_connected(graph.subgraph(core_of_the_core))

    # connect planted feedback loop
    if feedback_type == "pos_neg":
        if np.random.rand() <= .5:
            feedback_type = "pos"
        else:
            feedback_type = "neg"

    if feedback_type == "pos":
        weights = np.ones(num_core_of_the_core, dtype=int)
    elif feedback_type == "neg":
        weights = -np.ones(num_core_of_the_core, dtype=int)
    else:
        weights = np.random.choice([-1, 1], 
            size=num_core_of_the_core, replace=True).astype(int)
        if (weights==1).all():
            idx = np.random.choice(num_core_of_the_core)
            weights[idx] = -1
        if (weights==-1).all():
            idx = np.random.choice(num_core_of_the_core)
            weights[idx] = 1
        assert not (weights==1).all()
        assert not (weights==-1).all()
    
    for u, v, w in zip(core_of_the_core, 
            core_of_the_core[1:] + core_of_the_core[:1],
            weights):
        assert u != v

        graph.add_edge(u, v, weight=w) # planted feedback loop

    assert nx.is_strongly_connected(core_subgraph)

    num_cycles = 0
    for cycle in nx.simple_cycles(graph.subgraph(core_nodes)):
        assert len(cycle) >= num_core_of_the_core
        num_cycles += 1

        if len(cycle) == num_core_of_the_core and \
            all([x in cycle for x in core_of_the_core]):
            continue
        assert abs(sum((graph.edges[(u, v)]["weight"]
            for u, v in zip(cycle, cycle[1:] + cycle[:1])))) < len(cycle), len(cycle)
        
    assert num_cycles > 1


def build_network_structure(
    num_in=2,
    num_core=5,
    num_out=5,
    max_in_connections=3,
    num_input_nodes=2,
    num_output_nodes=2,
    seed=0,
    num_core_of_the_core=3, 
    feedback_type="pos"):

    np.random.seed(seed)

    N = num_in + num_core + num_out

    in_nodes = ["n{}".format(i) for i in range(num_in)]
    core_nodes = ["n{}".format(i) for i in range(num_in, num_in+num_core)]
    out_nodes = ["n{}".format(i) for i in range(num_in+num_core, N)]

    print ("in nodes are", in_nodes)
    print ("core nodes are", core_nodes)
    print ("out nodes are", out_nodes)

    graph = nx.DiGraph()

    graph.add_nodes_from(  in_nodes + core_nodes + out_nodes )

    ## in nodes to in nodes
    for in_node in in_nodes[:num_input_nodes]:

        num_in_connections = np.random.choice(range(1, max_in_connections+1))
        in_choices = np.random.choice(in_nodes[num_input_nodes:] + core_nodes, size=num_in_connections, replace=True)
        for in_choice in in_choices:
            graph.add_edge(in_node, in_choice, weight=np.random.choice((-1, 1)))


    # add edges from in nodes to core
    for in_node in in_nodes[num_input_nodes:]:
        
        num_in_connections = np.random.choice(range(1, max_in_connections+1))
        core_choices = np.random.choice(core_nodes, size=num_in_connections, replace=True)
        for core_node in core_choices:
            graph.add_edge(in_node, core_node, weight=np.random.choice((-1, 1)))


    # core to out nodes
    for out_node in out_nodes[:-num_output_nodes]:
        
        num_out_connections = np.random.choice(range(1,
            max_in_connections+1))
        core_choices = np.random.choice(
            core_nodes, 
            size=num_out_connections, 
            replace=True)

        for core_node in core_choices:
            graph.add_edge(core_node, out_node, weight=np.random.choice((-1, 1)))

    # out to out (if num_output < num_out)
    for out_node in out_nodes[-num_output_nodes:]:

        num_out_connections = np.random.choice(range(1,
            max_in_connections+1))

        out_choices = np.random.choice(
            core_nodes + out_nodes[:-num_output_nodes], 
            size=num_out_connections, 
            replace=True)

        for out_choice in out_choices:
            graph.add_edge( out_choice, out_node, 
                weight=np.random.choice((-1, 1)))

    # build core 
    build_core(graph, core_nodes, num_core_of_the_core, feedback_type)

    assert nx.is_weakly_connected(graph)

    return graph


def build_rules(
    graph,
    and_p=.5):

    rules = {}

    for n in graph:

        in_nodes = [u if w > 0 else "!"+u 
            for u, _, w in graph.in_edges(n, data="weight")]
        num_in_nodes = len(in_nodes)

        if num_in_nodes == 0:
            ## handle input nodes
            rule = n

        else:

            connectives = np.random.choice(["&", "|"], 
                p=[and_p, 1-and_p], size=num_in_nodes-1)

            terms = []
            
            brackets = 0
            term = in_nodes.pop(0)
            for connective in connectives:
                if connective == "|":
                    term += connective
                    if not brackets:
                        brackets = 1
                        term = "(" + term
                else:
                    assert connective == "&"
                    term += ")" * brackets
                    terms.append(term)
                    brackets = 0
                    term = ""
                term += in_nodes.pop(0)


            if term != "":
                term += ")" * brackets
                terms.append(term)
                brackets = 0
                term = ""

            rule = " & ".join(terms)

        rules.update({n: rule})

    return rules


def write_bnet(
    rules, 
    filename):

    if not filename.endswith(".bnet"):
        filename += ".bnet"

    
    with open(filename, "w") as f:

        for k, v in rules.items():
            f.write("{},\t{}\n".format(k, v))


def write_neet_logic(rules,
    filename):

    if not filename.endswith(".txt"):
        filename += ".txt"

    with open(filename, "w") as f:

        for k, v in rules.items():

            v = v.replace("|", " OR ")
            v = v.replace("&", " AND ")
            v = v.replace("!", "NOT ")
            v = v.replace("(", "( ")
            v = v.replace(")", " )")
            f.write("{} = {}\n".format(k, v))


def parse_args():
    '''
    Parse from command line
    '''
    parser = argparse.ArgumentParser(description="Generate bow tie networks with dynamics descrbed by .bnet file.")

    parser.add_argument("--num_in", 
        dest="num_in", type=int, default=10,
        help="Number of nodes in the in component.")
    parser.add_argument("--num_core", 
        dest="num_core", type=int, default=6,
        help="Number of nodes in the core.")
    parser.add_argument("--num_out", 
        dest="num_out", type=int, default=10,
        help="Number of nodes in the out component.")

    parser.add_argument("--max_in_connections", 
        dest="max_in_connections", type=int, default=3,
        help="Maximum number of edges from nodes in the in component.")

    parser.add_argument("--num_input_nodes", 
        dest="num_input_nodes", type=int, default=10,
        help="Number of nodes with no incoming  edges.")
    parser.add_argument("--num_output_nodes", 
        dest="num_output_nodes", type=int, default=10,
        help="Number of nodes with no outgoing edges.")

    parser.add_argument("--root_directory", 
        dest="root_directory", type=str, 
        default="synthetic_bow_tie",
        help="Directory to save networks.")

    # parser.add_argument("--seed", 
    #     dest="seed", type=int, default=0,
    #     help="Random seed.")

    return parser.parse_args()

def main():

    args = parse_args()

    root_directory = args.root_directory
    if not os.path.exists(root_directory):
        print ("making directory", root_directory)
        os.makedirs(root_directory, exist_ok=True)

    num_in = args.num_in
    num_core = args.num_core
    num_out = args.num_out

    max_in_connections = args.max_in_connections
    num_input_nodes = args.num_input_nodes
    num_output_nodes = args.num_output_nodes

    num_seeds = 1000
    feedback_types = ("pos_neg", "pos", "neg", )

    for seed in range(num_seeds):

        for feedback_type in feedback_types:

            output_directory = os.path.join(root_directory, 
                "{:03d}".format(seed),
                feedback_type)
            
            if not os.path.exists(output_directory):
                os.makedirs(output_directory, exist_ok=True)

            graph = build_network_structure(
                num_in,
                num_core,
                num_out,
                max_in_connections,
                num_input_nodes,
                num_output_nodes,
                seed=seed,
                feedback_type=feedback_type)

            # nx.set_edge_attributes(graph, name="arrowhead",
            #     values={(u, v): ("normal" if w>0 else "tee") 
            #         for u, v, w in graph.edges(data="weight")})

            # draw network
            # plot_filename = os.path.join(output_directory, "whole_network.png")
            # graph.graph['edge'] = {'arrowsize': '.8', 'splines': 'curved'}
            # graph.graph['graph'] = {'scale': '3'}

            # a = to_agraph(graph)
            # a.layout('dot')   
            # a.draw(plot_filename)

            edgelist_filename = os.path.join(output_directory, "edgelist.tsv")
            print ("writing edgelist to", edgelist_filename)
            nx.write_edgelist(graph, edgelist_filename, 
                data=["weight"], delimiter="\t")

            rules = build_rules(graph)

            bnet_filename = os.path.join(output_directory, "network.bnet")
            write_bnet(rules, bnet_filename)

            neet_logic_filename = os.path.join(output_directory, "network.txt")
            write_neet_logic(rules, neet_logic_filename)

        print ("completed seed", seed)


if __name__ == "__main__":
    main()