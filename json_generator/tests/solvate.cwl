#!/usr/bin/env cwl-runner
tprcwlVersion: v1.0
class: CommandLineTool
label: Wrapper of the GROMACS solvate  module.
doc: |-
  None
baseCommand: solvate
hints:
  DockerRequirement:
    dockerPull: quay.io/biocontainers/biobb_md:3.0.0--py_0
inputs:
  input_solute_gro_path:
    label: Path to the input GRO file
    doc: |-
      Path to the input GRO file
      Type: string
      File type: input
      Accepted formats: gro
      Example file: https://github.com/bioexcel/biobb_md/raw/master/biobb_md/test/data/gromacs/solvate.gro
    type: File
    format:
    - edam:format_2330
    inputBinding:
      position: 1
      prefix: --input_solute_gro_path
  output_gro_path:
    label: Path to the output GRO file
    doc: |-
      Path to the output GRO file
      Type: string
      File type: output
      Accepted formats: gro
      Example file: https://github.com/bioexcel/biobb_md/raw/master/biobb_md/test/reference/gromacs/ref_solvate.gro
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
      Example file: https://github.com/bioexcel/biobb_md/raw/master/biobb_md/test/data/gromacs/solvate.zip
    type: File
    format:
    - edam:format_3987
    inputBinding:
      position: 3
      prefix: --input_top_zip_path
  output_top_zip_path:
    label: Path the output topology in zip format
    doc: |-
      Path the output topology in zip format
      Type: string
      File type: output
      Accepted formats: zip
      Example file: https://github.com/bioexcel/biobb_md/raw/master/biobb_md/test/reference/gromacs/ref_solvate.zip
    type: string
    format:
    - edam:format_3987
    inputBinding:
      position: 4
      prefix: --output_top_zip_path
    default: system.zip
  config:
    label: Advanced configuration options for biobb_md Solvate
    doc: |-
      Advanced configuration options for biobb_md Solvate. This should be passed as a string containing a dict. The possible options to include here are listed under 'properties' in the biobb_md Solvate documentation: https://biobb-md.readthedocs.io/en/latest/gromacs.html#module-gromacs.solvate
    type: string?
    inputBinding:
      prefix: --config
outputs:
  output_gro_path:
    label: Path to the output GRO file
    doc: |-
      Path to the output GRO file
    type: File
    format:
    - edam:format_2330
    outputBinding:
      glob: $(inputs.output_gro_path)
  output_top_zip_path:
    label: Path the output topology in zip format
    doc: |-
      Path the output topology in zip format
    type: File
    format:
    - edam:format_3987
    outputBinding:
      glob: $(inputs.output_top_zip_path)
$namespaces:
  edam: http://edamontology.org/
$schemas:
- https://raw.githubusercontent.com/edamontology/edamontology/master/EDAM_dev.owl
