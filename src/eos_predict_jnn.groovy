/*
 * Evaluate one unary NNAP .jnn model on EOS POSCARs listed in a CSV file.
 *
 * Usage:
 *   jse src/eos_predict_jnn.groovy METADATA_CSV MODEL.JNN OUTPUT_CSV
 *
 * The output path must not exist.  This prevents accidental replacement of
 * validation artifacts from a prior evaluation.
 */

import java.util.Locale

import jse.code.IO
import jse.vasp.POSCAR
import jsex.nnap.NNAP

if (args.length != 3) {
    throw new IllegalArgumentException(
        'Usage: jse src/eos_predict_jnn.groovy METADATA_CSV MODEL.JNN OUTPUT_CSV'
    )
}

String metadataPath = args[0]
String modelPath = args[1]
String outputPath = args[2]
if (!IO.isfile(metadataPath)) {
    throw new IllegalArgumentException("Missing metadata CSV: ${metadataPath}")
}
if (!IO.isfile(modelPath)) {
    throw new IllegalArgumentException("Missing NNAP model: ${modelPath}")
}
if (IO.exists(outputPath)) {
    throw new IllegalStateException("Refusing to overwrite existing output: ${outputPath}")
}

List<String[]> inputRows = IO.csv2str(metadataPath)
if (inputRows.size() < 2) {
    throw new IllegalArgumentException("EOS metadata has no data rows: ${metadataPath}")
}
Map<String, Integer> columns = [:]
String[] header = inputRows[0]
for (int column in 0..<header.length) {
    columns[header[column]] = column
}
List<String> requiredColumns = [
    'structure',
    'scale',
    'natoms',
    'volume_A3',
    'volume_per_atom_A3',
    'poscar_path',
]
for (String column in requiredColumns) {
    if (!columns.containsKey(column)) {
        throw new IllegalArgumentException("EOS metadata is missing column: ${column}")
    }
}

NNAP potential = new NNAP(modelPath)
if (potential.ntypes() != 1) {
    potential.close()
    throw new IllegalArgumentException(
        "EOS evaluator only accepts unary models; found ${potential.ntypes()} types in ${modelPath}"
    )
}

List<List<String>> outputRows = [[
    'structure',
    'scale',
    'natoms',
    'volume_A3',
    'volume_per_atom_A3',
    'volume_ratio',
    'poscar_path',
    'jnn_path',
    'nnap_energy_eV',
    'nnap_energy_per_atom_eV',
]]
try {
    for (int rowIndex in 1..<inputRows.size()) {
        String[] row = inputRows[rowIndex]
        String structure = valueAt(row, columns, 'structure')
        String scale = valueAt(row, columns, 'scale')
        int natoms = Integer.parseInt(valueAt(row, columns, 'natoms'))
        String volume = valueAt(row, columns, 'volume_A3')
        String volumePerAtom = valueAt(row, columns, 'volume_per_atom_A3')
        String volumeRatio = columns.containsKey('volume_ratio')
            ? valueAt(row, columns, 'volume_ratio')
            : ''
        String poscarPath = valueAt(row, columns, 'poscar_path')
        if (!IO.isfile(poscarPath)) {
            throw new IllegalArgumentException("Missing EOS POSCAR: ${poscarPath}")
        }

        POSCAR atoms = POSCAR.read(poscarPath)
        if (atoms.natoms() != natoms) {
            throw new IllegalArgumentException(
                "Metadata/POSCAR atom-count mismatch for ${poscarPath}: ${natoms} != ${atoms.natoms()}"
            )
        }
        if (atoms.ntypes() != 1 || atoms.symbol(1) != potential.symbol(1)) {
            throw new IllegalArgumentException(
                "POSCAR/model species mismatch for ${poscarPath}: ${atoms.symbol(1)} vs ${potential.symbol(1)}"
            )
        }

        double energy = potential.calEnergy(atoms)
        if (!Double.isFinite(energy)) {
            throw new IllegalStateException("Non-finite NNAP energy for ${poscarPath}")
        }
        outputRows << [
            structure,
            scale,
            Integer.toString(natoms),
            volume,
            volumePerAtom,
            volumeRatio,
            poscarPath,
            modelPath,
            String.format(Locale.ROOT, '%.12f', energy),
            String.format(Locale.ROOT, '%.12f', energy / natoms),
        ]
    }
} finally {
    potential.close()
}

IO.str2csv(outputRows, outputPath)
println("predictions: ${outputPath}")
println("n_structures: ${outputRows.size() - 1}")

String valueAt(String[] row, Map<String, Integer> columns, String name) {
    int index = columns[name]
    if (index >= row.length) {
        throw new IllegalArgumentException("Missing value for ${name}")
    }
    return row[index]
}
