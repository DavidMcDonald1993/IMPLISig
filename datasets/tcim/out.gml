graph [
  directed 1
  graph [
    scale "3"
  ]
  node [
    id 0
    label "Invasion"
  ]
  node [
    id 1
    label "EMT"
  ]
  node [
    id 2
    label "VIM"
  ]
  node [
    id 3
    label "ERK"
  ]
  node [
    id 4
    label "CellCycleArrest"
  ]
  node [
    id 5
    label "Apoptosis"
  ]
  node [
    id 6
    label "p21"
  ]
  node [
    id 7
    label "SMAD"
  ]
  node [
    id 8
    label "Migration"
  ]
  node [
    id 9
    label "Metastasis"
  ]
  edge [
    source 0
    target 8
    weight 1.0
    arrowhead "normal"
  ]
  edge [
    source 1
    target 8
    weight 1.0
    arrowhead "normal"
  ]
  edge [
    source 2
    target 8
    weight 1.0
    arrowhead "normal"
  ]
  edge [
    source 3
    target 5
    weight -1.0
    arrowhead "tee"
  ]
  edge [
    source 3
    target 8
    weight 1.0
    arrowhead "normal"
  ]
  edge [
    source 3
    target 6
    weight -1.0
    arrowhead "tee"
  ]
  edge [
    source 6
    target 4
    weight 1.0
    arrowhead "normal"
  ]
  edge [
    source 7
    target 3
    weight 1.0
    arrowhead "normal"
  ]
  edge [
    source 7
    target 0
    weight 1.0
    arrowhead "normal"
  ]
  edge [
    source 7
    target 6
    weight 1.0
    arrowhead "normal"
  ]
  edge [
    source 8
    target 9
    weight 1.0
    arrowhead "normal"
  ]
]
