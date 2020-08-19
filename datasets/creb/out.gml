graph [
  directed 1
  graph [
    scale "3"
  ]
  node [
    id 0
    label "ILK"
  ]
  node [
    id 1
    label "AKT"
  ]
  node [
    id 2
    label "CREM"
  ]
  node [
    id 3
    label "cJun"
  ]
  node [
    id 4
    label "RasGAP"
  ]
  node [
    id 5
    label "GSK3"
  ]
  node [
    id 6
    label "CaMKI"
  ]
  node [
    id 7
    label "CaMKIV"
  ]
  node [
    id 8
    label "RSK"
  ]
  node [
    id 9
    label "CREB"
  ]
  node [
    id 10
    label "PIP2"
  ]
  node [
    id 11
    label "CaMKK"
  ]
  node [
    id 12
    label "CBP"
  ]
  edge [
    source 0
    target 1
    weight 1.0
    arrowhead "normal"
  ]
  edge [
    source 0
    target 5
    weight -1.0
    arrowhead "tee"
  ]
  edge [
    source 1
    target 5
    weight -1.0
    arrowhead "tee"
  ]
  edge [
    source 2
    target 9
    weight -1.0
    arrowhead "tee"
  ]
  edge [
    source 3
    target 9
    weight 1.0
    arrowhead "normal"
  ]
  edge [
    source 4
    target 1
    weight 1.0
    arrowhead "normal"
  ]
  edge [
    source 5
    target 9
    weight 1.0
    arrowhead "normal"
  ]
  edge [
    source 5
    target 3
    weight -1.0
    arrowhead "tee"
  ]
  edge [
    source 6
    target 9
    weight 1.0
    arrowhead "normal"
  ]
  edge [
    source 7
    target 9
    weight 1.0
    arrowhead "normal"
  ]
  edge [
    source 7
    target 2
    weight 1.0
    arrowhead "normal"
  ]
  edge [
    source 8
    target 9
    weight 1.0
    arrowhead "normal"
  ]
  edge [
    source 10
    target 1
    weight 1.0
    arrowhead "normal"
  ]
  edge [
    source 11
    target 1
    weight 1.0
    arrowhead "normal"
  ]
  edge [
    source 11
    target 6
    weight 1.0
    arrowhead "normal"
  ]
  edge [
    source 11
    target 7
    weight 1.0
    arrowhead "normal"
  ]
  edge [
    source 12
    target 3
    weight 1.0
    arrowhead "normal"
  ]
]
