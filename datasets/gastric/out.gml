graph [
  directed 1
  graph [
    scale "3"
  ]
  node [
    id 0
    label "Caspase8"
  ]
  node [
    id 1
    label "ITCH"
  ]
  node [
    id 2
    label "BAD"
  ]
  node [
    id 3
    label "BCL2"
  ]
  node [
    id 4
    label "BAX"
  ]
  node [
    id 5
    label "CFLAR"
  ]
  node [
    id 6
    label "Caspase9"
  ]
  node [
    id 7
    label "CytochromeC"
  ]
  edge [
    source 1
    target 5
    weight -1.0
    arrowhead "tee"
  ]
  edge [
    source 2
    target 3
    weight -1.0
    arrowhead "tee"
  ]
  edge [
    source 3
    target 7
    weight -1.0
    arrowhead "tee"
  ]
  edge [
    source 4
    target 7
    weight 1.0
    arrowhead "normal"
  ]
  edge [
    source 5
    target 0
    weight -1.0
    arrowhead "tee"
  ]
  edge [
    source 7
    target 6
    weight 1.0
    arrowhead "normal"
  ]
]
