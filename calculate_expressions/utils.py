
import os
import fcntl
import functools
import itertools

import numpy as np
import networkx as nx 
import pandas as pd

from PyBoolNet import StateTransitionGraphs as STGs

def rotate_cyclic_attractor(attractor):
	assert len(attractor) == len(set(attractor))
	m = min(attractor)
	i = attractor.index(m)
	return attractor[i:] + attractor[:i]

def select_states(primes, num_state_samples=10000, seed=0):

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
			state = tuple(np.random.randint(2, size=n))
			states.add(state)

	states = list(map(lambda state: 
		STGs.state2str({p: s 
		for p, s in zip(primes, state)}), states))

	return states

def build_STG_and_determine_attractors(
	primes, 
	states, 
	return_stg=False):
	print ("building partial STG to determine attractors for given initial conditions")

	# assume synchronous update scheme

	assert isinstance(states[0], str)

	stg = nx.DiGraph()

	attractors = []

	for i, state in enumerate(states):

		next_state = STGs.state2str(STGs.successor_synchronous(primes, state))

		while next_state not in stg:

			stg.add_edge(state, next_state)
			state = next_state
			next_state = STGs.state2str(STGs.successor_synchronous(primes, state))

		assert next_state in stg
		stg.add_edge(state, next_state) # connect new part of STG to existsing STG
				
		#cyclic attractor? use exising STG to determine attractor

		visited = [state]
		while next_state not in visited:
			visited.append(next_state)
			assert len(list(stg.neighbors(next_state))) == 1
			next_state = list(stg.neighbors(next_state))[0]

		idx = visited.index(next_state)
		attractor = visited[idx:]
		attractors.append(attractor)

	if return_stg:
		return stg, attractors
	else:
		return attractors

def compute_average_activation(primes, genes, attractors):

	counts = {gene: [] for gene in genes}

	for attractor in attractors:

		attractor_counts = {gene: 0 for gene in genes}
		attractor_period = len(attractor)

		for state in attractor:

			state_dict = STGs.state2dict(primes, state)

			for gene in genes:
				attractor_counts[gene] += state_dict[gene]

		for gene in genes:
			counts[gene].append(attractor_counts[gene] / \
				attractor_period)

	return counts



