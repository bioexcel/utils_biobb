#!/usr/bin/env cwl-runner
tprcwlVersion: v1.0
class: CommandLineTool
label: Wrapper class for the GROMACS genion  module.
doc: |-
  None
baseCommand: genion
hints:
  DockerRequirement:
    dockerPull: quay.io/biocontainers/biobb_md:3.0.0--py_0
inputs:
  input_tpr_path:
    label: Path to the input portable run input TPR file
    doc: |-
      Path to the input portable run input TPR file
      Type: string
      File type: input
      Accepted formats: tpr
      Example file: https://github.com/bioexcel/biobb_md/raw/master/biobb_md/test/data/gromacs/genion.tpr
    type: File
    format:
    - edam:format_2333
    inputBinding:
      position: 1
      prefix: --input_tpr_path
  output_gro_path:
    label: Path to the input structure GRO file
    doc: |-
      Path to the input structure GRO file
      Type: string
      File type: output
      Accepted formats: gro
      Example file: https://github.com/bioexcel/biobb_md/raw/master/biobb_md/test/reference/gromacs/ref_genion.gro
    type: string
    format:
    - edam:format_2330
    inputBinding:
      position: 2
      prefix: --output_gro_path
    default: system.gro
  input_top_zip_path:
    label: Path the input TOP topology in zip format
    doc: |-
      Path the input TOP topology in zip format
      Type: string
      File type: input
      Accepted formats: zip
      Example file: https://github.com/bioexcel/biobb_md/raw/master/biobb_md/test/data/gromacs/genion.zip
    type: File
    format:
    - edam:format_3987
    inputBinding:
      position: 3
      prefix: --input_top_zip_path
  output_top_zip_path:
    label: Path the output topology TOP and ITP files zipball
    doc: |-
      Path the output topology TOP and ITP files zipball
      Type: string
      File type: output
      Accepted formats: zip
      Example file: https://github.com/bioexcel/biobb_md/raw/master/biobb_md/test/reference/gromacs/ref_genion.zip
    type: string
    format:
    - edam:format_3987
    inputBinding:
      position: 4
      prefix: --output_top_zip_path
    default: system.zip
  config:
    label: Advanced configuration options for biobb_md Genion
    doc: |-
      Advanced configuration options for biobb_md Genion. This should be passed as a string containing a dict. The possible options to include here are listed under 'properties' in the biobb_md Genion documentation: https://biobb-md.readthedocs.io/en/latest/gromacs.html#module-gromacs.genion
    type: string?
    inputBinding:
      prefix: --config
outputs:
  output_gro_path:
    label: Path to the input structure GRO file
    doc: |-
      Path to the input structure GRO file
    type: File
    format:
    - edam:format_2330
    outputBinding:
      glob: $(inputs.output_gro_path)
  output_top_zip_path:
    label: Path the output topology TOP and ITP files zipball
    doc: |-
      Path the output topology TOP and ITP files zipball
    type: File
    format:
    - edam:format_3987
    outputBinding:
      glob: $(inputs.output_top_zip_path)
$namespaces:
  edam: http://edamontology.org/
$schemas:
- https://raw.githubusercontent.com/edamontology/edamontology/master/EDAM_dev.owl
