#!/usr/bin/env cwl-runner
tprcwlVersion: v1.0
class: CommandLineTool
label: Wrapper class for the GROMACS genrestr  module.
doc: |-
  None
baseCommand: genrestr
hints:
  DockerRequirement:
    dockerPull: quay.io/biocontainers/biobb_md:3.0.0--py_0
inputs:
  input_structure_path:
    label: Path to the input structure PDB, GRO or TPR format
    doc: |-
      Path to the input structure PDB, GRO or TPR format
      Type: string
      File type: input
      Accepted formats: pdb, gro, tpr
      Example file: https://github.com/bioexcel/biobb_md/raw/master/biobb_md/test/data/gromacs/genrestr.gro
    type: File
    format:
    - edam:format_1476
    - edam:format_2330
    - edam:format_2333
    inputBinding:
      position: 1
      prefix: --input_structure_path
  input_ndx_path:
    label: Path to the input GROMACS index file, NDX format
    doc: |-
      Path to the input GROMACS index file, NDX format
      Type: string
      File type: input
      Accepted formats: ndx
      Example file: https://github.com/bioexcel/biobb_md/raw/master/biobb_md/test/data/gromacs/genrestr.ndx
    type: File
    format:
    - edam:format_2330
    inputBinding:
      position: 2
      prefix: --input_ndx_path
  output_itp_path:
    label: Path the output ITP topology file with restrains
    doc: |-
      Path the output ITP topology file with restrains
      Type: string
      File type: output
      Accepted formats: itp
      Example file: https://github.com/bioexcel/biobb_md/raw/master/biobb_md/test/reference/gromacs/ref_genrestr.itp
    type: string
    format:
    - edam:format_3883
    inputBinding:
      position: 3
      prefix: --output_itp_path
    default: system.itp
  config:
    label: Advanced configuration options for biobb_md Genrestr
    doc: |-
      Advanced configuration options for biobb_md Genrestr. This should be passed as a string containing a dict. The possible options to include here are listed under 'properties' in the biobb_md Genrestr documentation: https://biobb-md.readthedocs.io/en/latest/gromacs.html#module-gromacs.genrestr
    type: string?
    inputBinding:
      prefix: --config
outputs:
  output_itp_path:
    label: Path the output ITP topology file with restrains
    doc: |-
      Path the output ITP topology file with restrains
    type: File
    format:
    - edam:format_3883
    outputBinding:
      glob: $(inputs.output_itp_path)
$namespaces:
  edam: http://edamontology.org/
$schemas:
- https://raw.githubusercontent.com/edamontology/edamontology/master/EDAM_dev.owl
