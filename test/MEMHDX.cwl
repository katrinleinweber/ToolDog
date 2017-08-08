#!/usr/bin/env cwl-runner

cwlVersion: v1.0
id: MEMHDX
label: This tool allows users to perform an automated workflow to analyze, validate
  and visualize large HDX-MS datasets.
baseCommand: COMMAND
doc: "This tool allows users to perform an automated workflow to analyze, validate\
  \ and visualize large HDX-MS datasets. The input file is the output of DynamX software\
  \ from Waters. Output files provide a plot of the data, the fitted model for each\
  \ peptide, a plot of the calculated p -values, and a global visualization of the\
  \ experiment. User could also obtain an overview of all peptides on the 3D structure.\n\
  \nExternal links:\nTool homepage: http://memhdx.c3bi.pasteur.fr/\nbio.tools_ entry:\
  \ MEMHDX\n\n"
class: CommandLineTool
inputs:
  INPUT1:
    label: Mass spectrometry data
    format: http://edamontology.org/format_3475
    type: File
    inputBinding:
      prefix: --INPUT1
outputs:
  OUTPUT1:
    label: Plot
    format: ''
    type: File
    outputBinding:
      glob: OUTPUT1.ext
s:name: MEMHDX
s:about: This tool allows users to perform an automated workflow to analyze, validate
  and visualize large HDX-MS datasets. The input file is the output of DynamX software
  from Waters. Output files provide a plot of the data, the fitted model for each
  peptide, a plot of the calculated p -values, and a global visualization of the experiment.
  User could also obtain an overview of all peptides on the 3D structure.
s:url: http://memhdx.c3bi.pasteur.fr/
s:programmingLanguage:
- R
s:publication:
- id: http://dx.doi.org/10.1093/bioinformatics/btw420
$namespace:
  s: http://schema.org/
