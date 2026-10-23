/*
 * Smoke test of the generated biobb_gromacs Nextflow modules: grompp -> mdrun on the biobb_gromacs test data.
 * Expects biobb_adapters and biobb_gromacs next to utils_biobb, as in all.sh.
 */

include { BIOBB_GROMACS_GROMPP } from '../../../../biobb_adapters/biobb_adapters/nextflow/biobb_gromacs/grompp'
include { BIOBB_GROMACS_MDRUN } from '../../../../biobb_adapters/biobb_adapters/nextflow/biobb_gromacs/mdrun'

params {
    data: String = "${projectDir}/../../../../biobb_gromacs/biobb_gromacs/test/data/gromacs"
}

workflow {
    main:
    ch_input = channel.of([[id: 'test'], file("${params.data}/grompp.gro"), file("${params.data}/grompp.zip"), [], [], []])

    BIOBB_GROMACS_GROMPP(ch_input)
    BIOBB_GROMACS_MDRUN(BIOBB_GROMACS_GROMPP.out.output_tpr_path.map { meta, tpr -> [meta, tpr, []] })

    channel.topic('versions').unique().view { process, pkg, version -> "${process}: ${pkg} ${version}" }

    publish:
    tpr = BIOBB_GROMACS_GROMPP.out.output_tpr_path
    gro = BIOBB_GROMACS_MDRUN.out.output_gro_path
    log = BIOBB_GROMACS_MDRUN.out.output_log_path
}

output {
    tpr {
        path 'grompp'
    }
    gro {
        path 'mdrun'
    }
    log {
        path 'mdrun'
    }
}
