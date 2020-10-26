#!/usr/bin/env cwl-runner
tprcwlVersion: v1.0
class: CommandLineTool
label: Wrapper of the GROMACS editconf  module.
doc: |-
  None
baseCommand: editconf
hints:
  DockerRequirement:
    dockerPull: quay.io/biocontainers/biobb_md:3.0.0--py_0
inputs:
  input_gro_path:
    label: Path to the input GRO file
    doc: |-
      Path to the input GRO file
      Type: string
      File type: input
      Accepted formats: gro
      Example file: https://github.com/bioexcel/biobb_md/raw/master/biobb_md/test/data/gromacs/editconf.gro
    type: File
    format:
    - edam:format_2330
    inputBinding:
      position: 1
      prefix: --input_gro_path
  output_gro_path:
    label: Path to the output GRO file
    doc: |-
      Path to the output GRO file
      Type: string
      File type: output
      Accepted formats: gro
      Example file: https://github.com/bioexcel/biobb_md/raw/master/biobb_md/test/reference/gromacs/ref_editconf.gro
    type: string
    format:
    - edam:format_2330
    inputBinding:
      position: 2
      prefix: --output_gro_path
    default: system.gro
  config:
    label: Advanced configuration options for biobb_md Editconf
    doc: |-
      Advanced configuration options for biobb_md Editconf. This should be passed as a string containing a dict. The possible options to include here are listed under 'properties' in the biobb_md Editconf documentation: https://biobb-md.readthedocs.io/en/latest/gromacs.html#module-gromacs.editconf
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
$namespaces:
  edam: http://edamontology.org/
$schemas:
- https://raw.githubusercontent.com/edamontology/edamontology/master/EDAM_dev.owl
