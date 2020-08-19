import os 
import numpy as np
import pandas as pd 
import networkx as nx 

import itertools

import PyBoolNet
import PyBoolNet.StateTransitionGraphs as STGs
import PyBoolNet.Attractors as ATTRs

from utils import rotate_cyclic_attractor, build_STG_and_determine_attractors#, select_states

def select_states(primes, 
    num_state_samples=10000, 
    seed=0):

    n = len(primes)

    if 2**n <= num_state_samples:
        print ("using entire state space")
        states = set(itertools.product([0, 1], repeat=n))

    else:
        print ("sampling", 
                num_state_samples, 
                "states")
        states = set()
        np.random.seed(seed)

        while len(states) < num_state_samples:
            state = {n: (0 if n in ["Adenosine", "Dopamine", "Enkephalin",
                    "GABA", "Glutamate", "Serotonin", "Ach"]
                    else np.random.choice([0, 1]))
                    for n in primes}
            state = STGs.state2str(state)
            states.add(state)

    states = list(states)

    return states

def main():

    input_nodes = ["Adenosine", "Dopamine", "Enkephalin",
                    "GABA", "Glutamate", "Serotonin", "Ach"]

    primes = PyBoolNet.FileExchange.read_primes(
        "datasets/creb/network.json")

    # primary_attractor = pd.read_csv(
    #     "datasets/creb/primary_attractor.csv",
    #     index_col=0, header=None)
    # assert primary_attractor.shape[0] == len(primes)
    # for n in primary_attractor.index:
    #     assert n in primes, n
    
    # primary_attractor = [
    #     primary_attractor[col].to_dict()
    #     for col in primary_attractor.columns
    # ]
    # primary_attractor = [STGs.state2str(state)
    #     for state in primary_attractor]
    # primary_attractor = rotate_cyclic_attractor(
    #     primary_attractor)
    # assert min(primary_attractor) == primary_attractor[0]

    merge_depths = pd.read_csv("implisig_output/creb/pos_neg/merge_depths.csv", 
        index_col=0)["0"]
    depths = sorted(set(merge_depths.values), reverse=True)

    kernels = [
        ["AC2", "AC5", "Calmodulin", "M2R", "PKA"],
        ["CREB", "CaMKI", "Calmodulin", "Galphai", "PKA"],
        ["mGluR7", "PQtypeCaCh", "cAMP"], ["mGluR7", "cAMP", "Ca2plus"],
        # ["mGluR7", "PQtypeCaCh", "cAMP", "Calmodulin"], ["mGluR7", "cAMP", "Ca2plus", "Calmodulin"],
        # ["mGluR7", "PQtypeCaCh", ], ["mGluR7",  "Ca2plus"],
        # kernel 
            # for kernel_size in [1, 2, 3]
            # for kernel in itertools.combinations(
                # ["mGluR7", "cAMP", "Ca2plus"]
        #     # ["AC2", "AC5", "Calmodulin", "M2R", "PKA"] + ["NtypeCaCh", "PKC", "Ca2plus",] + ["CaMKII"], kernel_size)
        #     ["AC5",
        #         "PKA",
        #         "Gbetagamma",
        #         "DAG",
        #         "mGluR1",
        #         "PKC",
        #         "mGluR7",
        #         "PQtypeCaCh",
        #         "PDK1",
        #         "cAMP",
        #         "CaMKII",
        #         "AC1",
        #         "PIP3",
        #         "NtypeCaCh",
        #         "Calmodulin",
        #         "Ca2plus",
        #         "AC2",
        #         "PI3K",
                # "PLCbeta"]
                # , kernel_size)
            # ["NtypeCaCh", "PKC", "Ca2plus"] + ["CaMKII", "Calmodulin"], kernel_size)
            # merge_depths.index[merge_depths>=depths[2]], kernel_size)
        # ["NtypeCaCh", "PKC", "Ca2plus"], 
        # primes
    ] #+ [ list(merge_depths.index[merge_depths>=depth]) for depth in depths]
    # ]

    states = select_states(primes, 
        num_state_samples=10000)

    for state in states:
        state = STGs.state2dict(primes, state)
        assert not any([
            state[n] for n in input_nodes])

    attractors = build_STG_and_determine_attractors(
        primes, states, return_stg=False)
    
    attractors = map(rotate_cyclic_attractor, attractors)
    attractors = list(map(tuple, attractors))
    unique_attractors = set(attractors)

    for attractor in unique_attractors:
        for state in attractor:
            state = STGs.state2dict(primes, state)
            assert not any([
                state[n] for n in input_nodes])

    print ("number of unique attractors:",
        len(unique_attractors))

    stg = STGs.primes2stg(primes, 
        Update="synchronous", 
        InitialStates=states)

    basins = dict()
    for basin in sorted(nx.weakly_connected_components(stg),
            key=len, reverse=True):
        cycles = list(nx.simple_cycles(stg.subgraph(basin)))
        assert len(cycles) == 1
        attractor = tuple(cycles[0])
        attractor = rotate_cyclic_attractor(attractor)
        assert attractor in unique_attractors
        basins.update({attractor: basin})

    primary_attractor = max(basins, 
        key=lambda k: len(basins[k]))

    # primary_attractor = pd.DataFrame([pd.Series(STGs.state2dict(primes, state))
    #     for state in primary_attractor])
    
    # primary_attractor.to_csv("CREB_primary_attractor.csv")

    # raise SystemError

    print ("primary attractor basin proportion:", 
        len(basins[primary_attractor]) / len(stg))

    df = []

    for target_state in primary_attractor:
        target_state = STGs.state2dict(primes,
            target_state)
        d = {}
        for kernel in kernels:
            print ("processing kernel", kernel,)
            assert all([n in primes for n in kernel])

            primes_modified = PyBoolNet.PrimeImplicants.create_constants(
                primes,
                {n: target_state[n] for n in kernel},
                Copy=True)

            attractors_new = build_STG_and_determine_attractors(
                primes_modified, states, return_stg=False)
            attractors_new = map(rotate_cyclic_attractor,
                attractors_new)
            attractors_new = list(map(tuple, attractors_new))
            unique_attractors_new = set(attractors_new)

            print ("number of unique attractors:", 
                len(unique_attractors_new))
            if len(unique_attractors_new) == 1:

                for unique_attractor in unique_attractors_new:
                    assert min(unique_attractor) == unique_attractor[0]
                    print ("length of obtained attractor", len(unique_attractor))
                    if len(unique_attractor) == 1:
                        print ("checking primary basin membership")

                        attr = build_STG_and_determine_attractors(primes, unique_attractor)
                        assert len(attr) == 1
                        attr = rotate_cyclic_attractor(attr[0])
                        in_primary_basin = int(all([s1==s2 
                            for s1, s2 in zip(attr, primary_attractor)]))
                        print ("in primary basin:", in_primary_basin)
                        d.update({"_".join(kernel): in_primary_basin})
                    else:
                        d.update({"_".join(kernel): 0})
            else:
                d.update({"_".join(kernel): 0})

            print ()
        df.append(pd.Series(d, name=STGs.state2str(target_state)))

    df = pd.DataFrame(df)
    df.to_csv("CREB_kernels.csv", sep=",")

if __name__ == "__main__":
    main()