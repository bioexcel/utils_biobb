#!/usr/bin/env cwl-runner
tprcwlVersion: v1.0

class: CommandLineTool

label: Wrapper of the GROMACS grompp module.

doc: |-
  The GROMACS preprocessor module needs to be fed with the input system and the dynamics parameters to create a portable binary run input file TPR. The dynamics parameters are specified in the mdp section of the configuration YAML file. The parameter names and defaults are the same as the ones in the official MDP specification.

baseCommand: grompp

hints:
  DockerRequirement:
    dockerPull: quay.io/biocontainers/biobb_md:3.0.0--py_0

inputs:
  input_gro_path:
    label: Path to the input GROMACS structure GRO file
    doc: |-
      Path to the input GROMACS structure GRO file
      Type: string
      File type: input
      Accepted formats: gro
      Example file: https://github.com/bioexcel/biobb_md/raw/master/biobb_md/test/data/gromacs/grompp.gro
    type: File
    format:
    - edam:format_2330
    inputBinding:
      position: 1
      prefix: --input_gro_path

  input_top_zip_path:
    label: Path to the input GROMACS topology TOP and ITP files in zip format
    doc: |-
      Path to the input GROMACS topology TOP and ITP files in zip format
      Type: string
      File type: input
      Accepted formats: zip
      Example file: https://github.com/bioexcel/biobb_md/raw/master/biobb_md/test/data/gromacs/grompp.zip
    type: File
    format:
    - edam:format_3987
    inputBinding:
      position: 2
      prefix: --input_top_zip_path

  output_tpr_path:
    label: Path to the output portable binary run file TPR
    doc: |-
      Path to the output portable binary run file TPR
      Type: string
      File type: output
      Accepted formats: tpr
      Example file: https://github.com/bioexcel/biobb_md/raw/master/biobb_md/test/reference/gromacs/ref_grompp.tpr
    type: string
    format:
    - edam:format_2333
    inputBinding:
      position: 3
      prefix: --output_tpr_path
    default: system.tpr

  input_cpt_path:
    label: Path to the input GROMACS checkpoint file CPT
    doc: |-
      Path to the input GROMACS checkpoint file CPT
      Type: string
      File type: input
      Accepted formats: cpt
      Example file: null
    type: File?
    format:
    - edam:format_2333
    inputBinding:
      prefix: --input_cpt_path

  input_ndx_path:
    label: Path to the input GROMACS index files NDX
    doc: |-
      Path to the input GROMACS index files NDX
      Type: string
      File type: input
      Accepted formats: ndx
      Example file: null
    type: File?
    format:
    - edam:format_2330
    inputBinding:
      prefix: --input_ndx_path

  input_mdp_path:
    label: Path of the input GROMACS MDP file
    doc: |-
      Path of the input GROMACS MDP file
      Type: string
      File type: input
      Accepted formats: mdp
      Example file: null
    type: File?
    format:
    - edam:format_2330
    inputBinding:
      prefix: --input_mdp_path

  config:
    label: Advanced configuration options for biobb_md Grompp
    doc: |-
      Advanced configuration options for biobb_md Grompp. This should be passed as a string containing a dict. The possible options to include here are listed under 'properties' in the biobb_md Grompp documentation: https://biobb-md.readthedocs.io/en/latest/gromacs.html#module-gromacs.grompp
    type: string?
    inputBinding:
      prefix: --config

outputs:
  output_tpr_path:
    label: Path to the output portable binary run file TPR
    doc: |-
      Path to the output portable binary run file TPR
    type: File
    format:
    - edam:format_2333
    outputBinding:
      glob: $(inputs.output_tpr_path)

$namespaces:
  edam: http://edamontology.org/

$schemas:
- https://raw.githubusercontent.com/edamontology/edamontology/master/EDAM_dev.owl
