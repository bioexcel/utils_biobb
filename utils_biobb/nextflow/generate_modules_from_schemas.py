#!/usr/bin/env python3
"""
Generate Nextflow modules from biobb JSON schemas.

Supports multiple biobb packages by reading schemas directly from the biobb
repository or local json_schemas/ subdirectories.

Schema lookup order:
  1. {biobb_root}/biobb_{package}/biobb_{package}/json_schemas/ (original source)
  2. json_schemas/{package}/ (local fallback)

Usage:
  # Using original biobb repository (recommended)
  python scripts/generate_modules_from_schemas.py \\
    --package biobb_gromacs \\
    --container quay.io/biocontainers/biobb_gromacs:5.2.1--pyhdfd78af_0 \\
    --biobb-root /home/gelpi/DEVEL/BioExcel/biobb

  # Using local schemas
  python scripts/generate_modules_from_schemas.py \\
    --package biobb_model \\
    --container quay.io/biocontainers/biobb_model:5.0.0

  # With custom module subpath
  python scripts/generate_modules_from_schemas.py \\
    --package biobb_amber \\
    --container quay.io/biocontainers/biobb_amber:24.0.0--pyh1234567_0 \\
    --module-subpath md_simulation \\
    --biobb-root /path/to/biobb

Environment variables:
  BIOBB_ROOT: Default biobb root directory (can be overridden by --biobb-root)
"""
import json
import os
import re
import argparse
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
MODULES_DIR = BASE_DIR / 'modules'

# Package-specific module subpath (e.g., 'biobb_gromacs.gromacs' or 'biobb_amber.md_simulation')
PACKAGE_MODULE_SUBPATH = {
    'biobb_gromacs': 'gromacs',
    'biobb_amber': 'md_simulation',
    'biobb_model': 'model',
}

# Package-specific emit/filename mappings (optional overrides)
PACKAGE_EMIT_MAP = {
    'biobb_gromacs': {
        'top_zip': 'top',
        'gro': 'gro',
        'tpr': 'tpr',
        'ndx': 'ndx',
        'itp': 'itp',
        'edr': 'edr',
        'log': 'log',
        'trr': 'trr',
        'xtc': 'xtc',
        'cpt': 'cpt',
        'xvg': 'xvg',
        'zip': 'top',
    },
}

PACKAGE_FILENAME_MAP = {
    'biobb_gromacs': {
        'top_zip': '{}_top.zip',
        'gro': '{}.gro',
        'tpr': '{}.tpr',
        'ndx': '{}.ndx',
        'itp': '{}.itp',
        'edr': '{}.edr',
        'log': '{}.log',
        'trr': '{}.trr',
        'xtc': '{}.xtc',
        'cpt': '{}.cpt',
        'xvg': '{}.xvg',
        'zip': '{}.zip',
    },
}

PACKAGE_EXTENSION_HINTS = {
    'biobb_gromacs': {
        'dhdl': 'xvg',
    },
}

# Generic mappings (fallback for packages without specific overrides)
EMIT_MAP = {
    'top_zip': 'top',
    'gro': 'gro',
    'tpr': 'tpr',
    'ndx': 'ndx',
    'itp': 'itp',
    'edr': 'edr',
    'log': 'log',
    'trr': 'trr',
    'xtc': 'xtc',
    'cpt': 'cpt',
    'xvg': 'xvg',
    'zip': 'top',
}

FILENAME_MAP = {
    'top_zip': '{}_top.zip',
    'gro': '{}.gro',
    'tpr': '{}.tpr',
    'ndx': '{}.ndx',
    'itp': '{}.itp',
    'edr': '{}.edr',
    'log': '{}.log',
    'trr': '{}.trr',
    'xtc': '{}.xtc',
    'cpt': '{}.cpt',
    'xvg': '{}.xvg',
    'zip': '{}.zip',
}

EXTENSION_HINTS = {
    'dhdl': 'xvg',
}


def normalize_var(name: str) -> str:
    if name.endswith('_path'):
        return name[:-5]
    return name


def infer_extension(prop_info, package: str = 'biobb_gromacs'):
    """Infer file extension from property info."""
    ext_hints = PACKAGE_EXTENSION_HINTS.get(package, EXTENSION_HINTS)
    ext = ext_hints.get(prop_info.get('name', ''), None)
    if ext:
        return ext
    for pattern in prop_info.get('enum', []):
        match = re.search(r'\\\.([a-z0-9]+)\$', pattern)
        if match:
            return match.group(1)
    return None


def output_filename(process_name: str, prop_name: str, prop_info=None, package: str = 'biobb_gromacs') -> str:
    """Generate output filename based on property name and package-specific mappings."""
    key = prop_name
    if key.startswith('output_'):
        key = key[len('output_'):]
    if key.endswith('_path'):
        key = key[:-5]
    
    # Check package-specific filename map first
    fname_map = PACKAGE_FILENAME_MAP.get(package, FILENAME_MAP)
    if key in fname_map:
        return fname_map[key].format(process_name)
    
    if prop_info is not None:
        ext = infer_extension(prop_info, package)
        if ext:
            if key == 'top_zip':
                return f"{process_name}_top.zip"
            return f"{process_name}.{ext}"
    return f"{process_name}_{key}"


def emit_name(prop_name: str, package: str = 'biobb_gromacs') -> str:
    """Get emit name based on property name and package-specific mappings."""
    key = prop_name
    if key.startswith('output_'):
        key = key[len('output_'):]
    if key.endswith('_path'):
        key = key[:-5]
    
    # Check package-specific emit map first
    emit_map = PACKAGE_EMIT_MAP.get(package, EMIT_MAP)
    return emit_map.get(key, key.split('_')[0])

def render_module(process_name, input_props, output_props, properties, required_inputs, required_outputs, 
                  package: str = 'biobb_gromacs', container_image: str = None, module_subpath: str = None):
    """Render a Nextflow process module for a biobb function.
    
    Args:
        process_name: Name of the process (e.g., 'pdb2gmx')
        input_props: List of input property names
        output_props: List of output property names
        properties: Dict of property schemas
        required_inputs: List of required input property names
        required_outputs: List of required output property names
        package: biobb package name (e.g., 'biobb_gromacs')
        container_image: Container image URI
        module_subpath: Submodule path within the package (e.g., 'gromacs' for biobb_gromacs.gromacs)
    """
    if container_image is None:
        raise ValueError("container_image is required")
    
    if module_subpath is None:
        module_subpath = PACKAGE_MODULE_SUBPATH.get(package, 'module')
    
    lines = []
    lines.append(f"process {process_name} {{")
    lines.append(f"    tag '{process_name}'")
    lines.append(f"    container '{container_image}'")
    lines.append("    publishDir params.workflow_dir+\"/\"+cfg.step_name, mode: 'copy', overwrite: true")
    lines.append("")
    lines.append("    input:")
    lines.append("    val cfg")
    for prop_name in input_props:
        if prop_name not in required_inputs:
            continue
        var_name = normalize_var(prop_name)
        lines.append(f"    path {var_name}")
    lines.append("")
    lines.append("    output:")
    for prop_name in output_props:
        out_file = output_filename(process_name, prop_name, prop_info=properties[prop_name], package=package)
        emit = emit_name(prop_name, package=package)
        optional = ', optional: true' if prop_name not in required_outputs else ''
        lines.append(f"    path '{out_file}', emit: '{emit}'{optional}")
    lines.append("    path '*_command.log', emit: 'log', optional: true")
    lines.append("")
    lines.append("    script:")
    lines.append("    def stepCfg = [:]")
    for prop_name in input_props:
        if prop_name not in required_inputs:
            continue
        var_name = normalize_var(prop_name)
        lines.append(f"    if ({var_name}) stepCfg['{prop_name}'] = {var_name}.name")
    for prop_name in output_props:
        out_file = output_filename(process_name, prop_name, prop_info=properties[prop_name], package=package)
        lines.append(f"    stepCfg['{prop_name}'] = '{out_file}'")
    lines.append("    def step_name = cfg.containsKey('step_name') ? cfg.step_name : ''")
    lines.append("    def stepProperties = cfg.containsKey('properties') && cfg.properties ? new LinkedHashMap(cfg.properties) : [:]")
    lines.append("    stepProperties['working_dir_path'] = step_name ? \"workdir/${step_name}\" : 'workdir'")
    lines.append("    stepCfg['properties'] = stepProperties")
    lines.append("    def configJson = groovy.json.JsonOutput.toJson(stepCfg)")
    lines.append('    """')
    lines.append("    export STEP_NAME='${step_name}'")
    lines.append("    python - <<'PY'")
    lines.append("import json")
    lines.append(f"from {package}.{module_subpath}.{process_name} import {process_name}")
    lines.append("cfg = json.loads('''${configJson}''')")
    lines.append(f"{process_name}(**cfg)")
    lines.append("PY")
    lines.append("    if [ -n \"\\${STEP_NAME}\" ]; then mv .command.log \\${STEP_NAME}_command.log; fi")
    lines.append('    """')
    lines.append("}")
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(
        description='Generate Nextflow modules from biobb JSON schemas.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Generate GROMACS modules (default if schema files exist)
  python scripts/generate_modules_from_schemas.py \\
    --package biobb_gromacs \\
    --container quay.io/biocontainers/biobb_gromacs:5.2.1--pyhdfd78af_0

  # Generate AMBER modules
  python scripts/generate_modules_from_schemas.py \\
    --package biobb_amber \\
    --container quay.io/biocontainers/biobb_amber:24.0.0--pyh1234567_0 \\
    --module-subpath md_simulation

  # Use custom schema directory
  python scripts/generate_modules_from_schemas.py \\
    --package biobb_gromacs \\
    --container quay.io/biocontainers/biobb_gromacs:5.2.1--pyhdfd78af_0 \\
    --schema-dir /path/to/schemas
        '''
    )
    parser.add_argument(
        '--package',
        required=True,
        help='biobb package name (e.g., biobb_gromacs, biobb_amber)'
    )
    parser.add_argument(
        '--container',
        required=True,
        help='Container image URI (e.g., quay.io/biocontainers/biobb_gromacs:5.2.1--pyhdfd78af_0)'
    )
    parser.add_argument(
        '--schema-dir',
        default=None,
        help='Custom schema directory (defaults to json_schemas/{package}/)'
    )
    parser.add_argument(
        '--module-subpath',
        default=None,
        help='Submodule path within the package (e.g., "gromacs", "md_simulation"). Auto-detected if not provided.'
    )
    parser.add_argument(
        '--biobb-root',
        default=os.environ.get('BIOBB_ROOT', '/home/gelpi/DEVEL/BioExcel/biobb'),
        help='Root directory of biobb repositories. Defaults to BIOBB_ROOT env var or /home/gelpi/DEVEL/BioExcel/biobb. '
             'Schema lookup: {biobb_root}/biobb_{package}/biobb_{package}/json_schemas/'
    )
    
    args = parser.parse_args()
    
    # Normalize package name to handle both 'biobb_gromacs' and 'gromacs' formats
    full_package_name, short_package_name = args.package, args.package
    
    # Determine schema directory with priority order
    biobb_root = Path(args.biobb_root)
    
    # Priority 1: explicit --schema-dir
    if args.schema_dir:
        schema_dir = Path(args.schema_dir)
    else:
        # Priority 2: biobb root directory
            schema_dir = biobb_root / full_package_name / full_package_name / 'json_schemas'
        
        # Priority 3: fallback to local json_schemas/{package}/
            if not schema_dir.exists():
                schema_dir = BASE_DIR / 'json_schemas' / short_package_name
    
    if not schema_dir.exists():
        print(f"Error: Schema directory not found:", file=sys.stderr)
        if not args.schema_dir:
            print(f"  Tried (biobb root):  {biobb_root / full_package_name / full_package_name / 'json_schemas'}", file=sys.stderr)
            print(f"  Tried (local):       {BASE_DIR / 'json_schemas' / short_package_name}", file=sys.stderr)
            print(f"\nSet BIOBB_ROOT env var or use --biobb-root to specify the biobb repository location.", file=sys.stderr)
        else:
            print(f"  Specified path: {schema_dir}", file=sys.stderr)
        sys.exit(1)
    
    created = []
    for schema_file in sorted(schema_dir.glob('*.json')):
        # Skip the package metadata schema if it exists
        if schema_file.name in [f'{full_package_name}.json', f'{short_package_name}.json']:
            continue
        
        with open(schema_file, 'r') as f:
            schema = json.load(f)
        
        process_name = schema_file.stem
        properties = schema.get('properties', {})
        required = schema.get('required', [])
        input_props = [k for k, v in properties.items() if v.get('filetype') == 'input']
        output_props = [k for k, v in properties.items() if v.get('filetype') == 'output']
        
        if not input_props and not output_props:
            continue
        
        module_dir = MODULES_DIR / args.package / process_name
        # Use short package name for module directory (e.g., 'gromacs' not 'biobb_gromacs')
        module_dir = MODULES_DIR / short_package_name / process_name
        module_dir.mkdir(parents=True, exist_ok=True)
        
        content = render_module(
            process_name,
            input_props,
            output_props,
            properties,
            [p for p in input_props if p in required],
            [p for p in output_props if p in required],
            package=full_package_name,
            container_image=args.container,
            module_subpath=args.module_subpath
        )
        
        target_file = module_dir / 'main.nf'
        with open(target_file, 'w') as f:
            f.write(content)
        created.append(str(target_file.relative_to(BASE_DIR)))
    
    if created:
        print(f'Generated {len(created)} module(s) for {full_package_name}:')
        for path in created:
            print(' -', path)
    else:
        print(f'No modules generated. Check that schemas exist in {schema_dir}', file=sys.stderr)


if __name__ == '__main__':
    main()
