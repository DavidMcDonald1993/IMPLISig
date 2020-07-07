import os
from pathlib import Path

import numpy as np 
import networkx as nx
import pandas as pd

import itertools

import PyBoolNet
from PyBoolNet import Attractors
from PyBoolNet import StateTransitionGraphs as STGs

from utils import select_states, build_STG_and_determine_attractors, compute_average_activation

import argparse

def touch(filename):
    Path(filename).touch()

def parse_args():
    '''
    Parse from command line
    '''
    parser = argparse.ArgumentParser(description="Compute activations for boolean networks")

    # parser.add_argument("-i", 
    #     dest="i", type=int, default=0,
    #     help="index of list of modification.")

    parser.add_argument("--edgelist", 
        dest="edgelist", type=str, default=None,
        help="edgelist to load.")

    parser.add_argument("--primes", 
        dest="primes", type=str, default=None,
        help="path of primes to load.")
    parser.add_argument("--control_modification", 
        dest="control_modification", type=str, default=None, nargs="*",
        help="genes to set to overexpressed in control.")

    parser.add_argument("--output", dest="output", 
        type=str, default=None,
        help="Directory to save results.")

    parser.add_argument("--output_nodes", dest="output_nodes", 
        type=str, default=None, nargs="+",
        help="Output nodes of interest.")

    return parser.parse_args()

def main():

    # chunksize = 100

    args = parse_args()

    output_dir = args.output
    # output_dir = os.path.join(output_dir, "chunks")
    if not os.path.exists(output_dir):
        print ("making", output_dir)
        os.makedirs(output_dir, exist_ok=True)
    

    edgelist_filename = args.edgelist
    print ("loading interaction graph from", edgelist_filename)
    g = nx.read_weighted_edgelist(edgelist_filename, 
        delimiter="\t",
        create_using=nx.DiGraph())

    output_nodes = args.output_nodes
    if output_nodes[0] == "output": # all nodes with no outgoing edges
        output_nodes = [n for n in g if g.out_degree(n) == 0]

    for gene in output_nodes:
        assert gene in g, gene

    core = max(nx.strongly_connected_components(g), 
        key=len) # determine core of the network

    # remove any cancer genes from consideration
    control_modification = args.control_modification

    core = core - set(control_modification)
    core -= set(output_nodes)

    core = sorted(core)

    print ("core is", core)

    possible_candidates = [genes 
        for n_genes in (1, ) 
            for genes in itertools.combinations(core, 
                n_genes)]

    possible_candidates = [("control",)] + possible_candidates

    print ("number of possible candidates is", 
        len(possible_candidates))

    output_filenames = {output_node: 
        os.path.join(output_dir, 
        "{}_expressions.csv.gz".format(output_node))
        for output_node in output_nodes}

    output_dfs = {output_node: 
        (pd.read_csv(filename, index_col=0)
            if os.path.exists(filename)
            else pd.DataFrame()) 
        for output_node, filename in output_filenames.items()}

    primes_filename = args.primes
    if primes_filename.endswith(".bnet"):
        print ("loading from bnet file", primes_filename)
        json_filename = primes_filename.replace(".bnet", ".json")
        if os.path.exists(json_filename):
            print ("json file", json_filename, 
                "exists")
            primes = PyBoolNet.FileExchange.read_primes(json_filename)
        else:
            print("saving primes json to", json_filename)
            primes = PyBoolNet.FileExchange.bnet2primes(primes_filename, 
                FnamePRIMES=json_filename
                ) # write to json
    else:
        assert primes_filename.endswith(".json")
        print ("loading primes from json", primes_filename)
        primes = PyBoolNet.FileExchange.read_primes(primes_filename)

    if len(control_modification) > 0:
        print ("turning on", "_".join(control_modification),
            "to simulate cancer mutation")
        primes = PyBoolNet.PrimeImplicants.\
            create_constants(primes, 
            {mutation: 1 for mutation in control_modification}, # turn on control_modification
            Copy=True)

    for gene in output_nodes:
        assert gene in primes, gene

    states = select_states(primes)

    update = "synchronous"

    chosen_candidates = possible_candidates

    for chosen_candidate in chosen_candidates:
        chosen_candidate_identifier = "+".join(chosen_candidate)
        print ("chosen candidate is", chosen_candidate_identifier)

        if all([chosen_candidate_identifier in df.index
            for df in output_dfs.values()]):
                print (chosen_candidate_identifier, "already processed")
                continue

        # mad modification to network if necessary
        if chosen_candidate_identifier is not "control":
            
            print ("switching off", chosen_candidate)
            
            modified_network = PyBoolNet.PrimeImplicants.\
                create_constants(primes, 
                {gene: 0 for gene in chosen_candidate}, # turn off targets 
                Copy=True)

        else:
            # do nothing for control case
            modified_network = primes

        print ("determining attractors")
        attractors = build_STG_and_determine_attractors(
            modified_network, 
            states)

        print ("determing activations for output nodes", output_nodes)
        gene_counts = compute_average_activation(
            modified_network, 
            genes=output_nodes,
            attractors=attractors)

        for output_node in output_nodes:
            output_dfs[output_node] = output_dfs[output_node]\
                .append(pd.Series(gene_counts[output_node], 
                name=chosen_candidate_identifier, 
                index=[str(i) for i in range(len(states))]))

        print ()

    print ("writing results to files")
    for output_node in output_nodes:
        output_dfs[output_node].to_csv(
            output_filenames[output_node])

if __name__ == "__main__":
    main()