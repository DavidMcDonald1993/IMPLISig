import os
import argparse

import numpy as np 
import networkx as nx 
import pandas as pd 

from networkx.drawing.nx_agraph import write_dot, graphviz_layout, to_agraph

import glob

def find_cycles(u, n, g, start, l=set(), mode="pos"):   
	
	if n==0:
		assert u == start
		return [[u]]
	
	l = l.union( {u} )

	neighbors = {v 
		for _,  v, w in g.out_edges(u, data="weight")
		if mode=="all"
		or
		w > 0 and mode=="pos"
		or
		w < 0 and mode=="neg"}

	if n > 1:
		neighbors = neighbors - l
	else:
		neighbors = neighbors.intersection({start})
		
	paths = ( [u] + cycle
		for neighbor in neighbors
		for cycle in find_cycles(neighbor, n-1, g, start, l, mode) )
	return paths

def score_subgraph(g, groups):
	subgraph = g.subgraph(groups)

	# all internal edges of subgraph
	k_in = len([(u, v) 
		for u, v, w in subgraph.edges(data="weight") 
		if u != v])

	# return k_in / len(unpack(subgraph)) ** 2
	# k_self = len([(u, v) for 
	# 	u, v, w in subgraph.edges(data="weight") 
	# 	if u == v])
	# if isinstance(groups, frozenset):
	k_self = 0
	# else:
	# 	assert False
	# 	k_self = len([(u, v) for 
	# 		u, v, w in subgraph.edges(data="weight") 
	# 		if u == v])

	k_all = sum((len(set(g.neighbors(u)) - {u}) 
		for u in subgraph))

	return (k_in + k_self) / k_all


def collapse_subgraph(g, subgraph):

	new_edges = []

	for n in subgraph:

		if isinstance(g, nx.MultiDiGraph):
			for u, _, w in g.in_edges(n, data="weight"):
				if u in subgraph: # all internal edges become self loops
					u = subgraph
				new_edges.append(
					(u, subgraph, {"weight": w}))
			for _, v, w in g.out_edges(n, data="weight"):
				if v in subgraph: #  self loops already included
					continue
				new_edges.append(
					(subgraph, v, {"weight": w}))
		else:
			
			# undirected graph
			assert False 
			for _, v, w in g.edges(n, data="weight"):
				if v in subgraph:
					# v = subgraph
					continue
				new_edges.append(
					(subgraph, v, {"weight": w}))

	g.add_edges_from(new_edges)
	g.remove_nodes_from(subgraph)

def bottom_up_partition(g, 
	score_function=score_subgraph,
	max_loop_size=12,
	modes=("pos", "neg")):

	'''
	perform partition in bottom-up manner
	'''

	g = nx.MultiDiGraph(g.copy())
	h = nx.DiGraph()

	h.add_nodes_from( g.nodes() )
	
	# for u, _ in nx.selfloop_edges(g):
	# 	h.add_edge(u, frozenset([u]))
	# 	g = nx.relabel_nodes(g, mapping={u: frozenset([u])})

	# g.remove_edges_from(list(nx.selfloop_edges(g)))

	num_edges = len(g.edges())

	# repeat until g has collapsed into a single node    
	while len(g) > 1:
		print ("number of nodes in g:", len(g),
			"number of edges:", len(g.edges()))

		max_subgraph_score = 0

		###################################
		s = 2
		while s < max_loop_size:
			print ("scoring subgraphs of size", s)

			# subgraph_scores = {}

			for mode in modes:

				subgraph_scores = {}

				for n in g.nodes():
					for cycle in map(frozenset, 
						find_cycles(n, s, g, start=n, mode=mode)):
						if cycle in subgraph_scores:
							# assert np.allclose(subgraph_scores[cycle], 
							# 	score_function(g, cycle))
							continue
						subgraph_scores[cycle] = \
							score_function(g, cycle)

				if len(subgraph_scores) > 0:
					
					max_subgraph_score = max(subgraph_scores.values())

					if max_subgraph_score > 0:
						print ("found positive scoring subgraph of size", 
							s, "with score", max_subgraph_score )
						chosen_subgraphs = [k for k, v in subgraph_scores.items()
							if v == max_subgraph_score]
						break
			if max_subgraph_score > 0:
				break
			else:
				s += 1

		if s == max_loop_size:
			print ("failed to find any postive scoring subgraphs of size", 
				max_loop_size)
			chosen_subgraphs = [frozenset().union(g.nodes())]

		#####################################################
		# subgraph_scores = {}
		# for s in range(2, max_loop_size):
		# 	for n in g.nodes():
		# 		for mode in modes:
		# 			for cycle in map(frozenset, 
		# 				find_cycles(n, s, g, start=n, mode=mode)):
		# 				if cycle in subgraph_scores:
		# 					assert np.allclose(subgraph_scores[cycle], 
		# 						score_function(g, cycle))
		# 					continue
		# 				subgraph_scores[cycle] = \
		# 					score_function(g, cycle)

		# if len(subgraph_scores) > 0:
				
		# 	max_subgraph_score = max(subgraph_scores.values())

		# 	if max_subgraph_score > 0:
		# 		print ("found positive scoring subgraph(s)")
		# 		chosen_subgraphs = [k for k, v in subgraph_scores.items()
		# 			if v == max_subgraph_score]
		# 	else:
		# 		chosen_subgraphs = [frozenset().union(g.nodes())]

		# else:
		# 	chosen_subgraphs = [frozenset().union(g.nodes())]

		####################################################

		overlaps = np.array([[
			len(s1.intersection(s2)) for s2 in chosen_subgraphs]
			for s1 in chosen_subgraphs])

		chosen_subgraphs = {frozenset.union(*[chosen_subgraphs[x]
			for x in cc])
			for cc in nx.connected_components(nx.from_numpy_array(overlaps))
			}

		#####################################################

		for chosen_subgraph in chosen_subgraphs:

			# combine chosen subgraph into super node
			collapse_subgraph(g, chosen_subgraph)

			# add chosen subgraph to h
			h.add_node(chosen_subgraph)
			for n in chosen_subgraph:
				h.add_edge(n, chosen_subgraph)

		assert len(g.edges()) == num_edges, (len(g.edges), num_edges)

	return h

def decompose_all_sccs(g, 
	score_function=score_subgraph,
	max_loop_size=12,
	modes=("pos", "neg")):
	'''
	run decomposition on each SCC in g
	'''
	h = nx.DiGraph()
	roots = []

	for scc in nx.strongly_connected_components(g):
		print ("processing SCC", scc)
		scc = g.subgraph(scc)
		scc_tree = bottom_up_partition(scc, 
			score_function=score_function,
			max_loop_size=max_loop_size,
			modes=modes)
		degrees = dict(scc_tree.out_degree())
		root = min(degrees, key=degrees.get)
		roots.append(root)
		h = nx.union(h, scc_tree)
		print ()

	# add final root to represent whole network
	all_nodes = frozenset(g.nodes())
	if len(roots) > 1:
		for root in roots:
			h.add_edge(root, all_nodes)

	return h

def unpack(x):
	if isinstance(x, str):
		return [x]
	if not any([isinstance(x_, frozenset) for x_ in x]):
		return list(x)
	else:
		return [_x for x_ in x for _x in unpack(x_)]

def parse_args():
	'''
	Parse from command line
	'''
	parser = argparse.ArgumentParser(description="Read in edgelist and draw SCC decomposition")

	parser.add_argument("--edgelist", 
		dest="edgelist", type=str, default=None,
		help="edgelist to load.")
	# parser.add_argument("--mapping", 
	# 	dest="mapping", type=str, default=None,
	# 	help="mapping file of node ids to names.")
	parser.add_argument("--output", dest="output", 
		type=str, default=None,
		help="Directory to save images/merge depths.")
	parser.add_argument("--modes", nargs="+",
		default=("pos", "neg"))
	parser.add_argument("--draw", action="store_true",
		help="Flag to specify to plot or not.")

	parser.add_argument("--max_loop_size", type=int,
		default=12)

	return parser.parse_args()

def main():

	args = parse_args()

	edgelist_file = args.edgelist
	
	print ("decomposing", edgelist_file)

	g = nx.read_weighted_edgelist(edgelist_file, 
		create_using=nx.DiGraph(), 
		delimiter="\t")

	g = g.subgraph(max(nx.strongly_connected_components(g), key=len)) # only process largest SCC

	print ("found graph with", len(g), 
		"nodes and", len(g.edges()), "edges")

	nx.set_edge_attributes(g, name="arrowhead",
		values={(u, v): ("normal" if w>0 else "tee") 
			for u, v, w in g.edges(data="weight")})

	output_dir = args.output
	output_dir = os.path.join(output_dir, "_".join(args.modes))
	if not os.path.exists(output_dir):
		os.makedirs(output_dir, exist_ok=True)

	h = decompose_all_sccs(g, 
		max_loop_size=args.max_loop_size,
		modes=args.modes)
	
	print ("determining merge depths")

	out_degrees = dict(h.out_degree())
	root = min(out_degrees, key=out_degrees.get)

	core = list(
		max(nx.strongly_connected_components(g),
		key=len))

	merge_depths = {node: \
		nx.shortest_path_length(h, node, root) 
		for node in core }

	merge_depth_filename = os.path.join(output_dir,
		"merge_depths.csv")
	print ("saving merge depths to", merge_depth_filename)
	pd.Series(merge_depths).to_csv(merge_depth_filename)

	max_merge_depth = max(merge_depths.values())
	genes_with_max_merge_depth = [k 
		for k, v in merge_depths.items()
		if v == max_merge_depth]
	print ("genes with maximum merge depth")
	print (genes_with_max_merge_depth)
	print ()

	# # target input genes
	# in_component = [
	# 	n for n in g
	# 	if n not in core
	# 	and nx.has_path(g, n, core[0])
	# ]

	# scores = {u: 
	# 	np.mean([1. / nx.shortest_path_length(g, u, c) 
	# 		for c in genes_with_max_merge_depth])
	# 	for u in in_component
	# }

	# score_filename = os.path.join(output_dir, 
	# 	"in_component_scores.csv")
	# print ("saving scores to", score_filename)
	# pd.DataFrame.from_dict(scores, 
	# 	orient="index").to_csv(score_filename)
	# print ()


	### DRAWING
	if args.draw:

		draw_height = 2

		print ("DRAWING DECOMPOSITION AT HEIGHT",
			draw_height)

		h = h.reverse()

		node_id_map = {}
		node_height_map = {}

		for i, n in enumerate(h.nodes()):
			if isinstance(n, frozenset):
				g_ = nx.MultiDiGraph(g.subgraph(unpack(n)))
			else:
				g_ = nx.MultiDiGraph(g.subgraph([n]))
				g_.remove_edges_from(list(nx.selfloop_edges(g_)))
			nx.set_edge_attributes(g_, name="arrowhead",
				values={(u, v, w): ("normal" if w>0 else "tee") 
					for u, v, w in g_.edges(data="weight")})

			node_id_map.update({n: i})

			children = list(h.neighbors(n))
			if len(children) == 0:
				height = 0
			else:
				height = max([nx.shortest_path_length(h, n, 
					el) for el in unpack(n)])

			if height > draw_height:
				continue
			
			node_height_map.update({n: height})

			for no, child in enumerate(children):
				# make super node
				node = "supernode_{}".format(no)
				image_filename = os.path.join(output_dir, 
					"subgraph_{}.png".format(node_id_map[child]))
				assert os.path.exists(image_filename)
				g_.add_node(node, label="", 
					image=image_filename)
				for n_ in unpack(child):
					for u, _, w in g_.in_edges(n_, data="weight"):
						if u == node:
							continue
						g_.add_edge(u, node, 
						weight=w, 
						arrowhead=("normal" if w>0 else "tee"))
					for _, v, w in g_.out_edges(n_, data="weight"):
						if v == node:
							continue
						g_.add_edge(node, v, 
						weight=w,
						arrowhead=("normal" if w>0 else "tee"))
					g_.remove_node(n_)
				
			plot_filename = os.path.join(output_dir,
				"subgraph_{}.png".format(i))
			g_.graph['edge'] = {'arrowsize': '.8', 
				'splines': 'curved'}
			g_.graph['graph'] = {'scale': '3'}

			# nx.set_edge_attributes(g_, name="len", values=".1" )

			a = to_agraph(g_)
			a.layout('fdp')   
			a.draw(plot_filename)

		h = h.reverse()
		
		# draw hierarchy
		nx.set_node_attributes(h, name="image", 
			values={n: 
			os.path.join(output_dir, 
			"subgraph_{}.png".format(i) )
			for i, n in enumerate(h.nodes())})
		nx.set_node_attributes(h, name="label", values="")

		tree_plot_filename = os.path.join(output_dir, 
			"scc_tree.png")
		h.graph['edge'] = {'arrowsize': '.8', 'splines': 'curved'}
		h.graph['graph'] = {'scale': '3'}

		a = to_agraph(h)
		a.layout('dot')   
		a.draw(tree_plot_filename)

		print ("plotted", tree_plot_filename)

		# cleanup of directory
		print ("cleaning up directory")
		nodes_to_remove = [node_id_map[n]
			for n, h in node_height_map.items()
			if h < draw_height]
		# for f in glob.iglob(os.path.join(output_dir, 
		# 	"subgraph_*.png")):
		for f in (os.path.join(output_dir, 
			"subgraph_{}.png".format(n) )
			for n in nodes_to_remove):
			os.remove(f)

if __name__ == "__main__":
	main()