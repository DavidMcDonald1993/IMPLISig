graph [
  directed 1
  graph [
    scale "3"
  ]
  node [
    id 0
    label "Gfi_1"
  ]
  node [
    id 1
    label "cJun"
  ]
  node [
    id 2
    label "EgrNab"
  ]
  edge [
    source 0
    target 2
    weight -1.0
    arrowhead "tee"
  ]
  edge [
    source 0
    target 1
    weight -1.0
    arrowhead "tee"
  ]
  edge [
    source 1
    target 2
    weight 1.0
    arrowhead "normal"
  ]
  edge [
    source 2
    target 0
    weight -1.0
    arrowhead "tee"
  ]
]
