"""Tools for the SuiteSparse matrix collection."""

import csv


class Matrix:
    """Statistics for a single matrix in the SuiteSparse Matrix Collection."""
    def __init__(self, matrix_id, group, name, rows, columns, nonzeros,
                 real, binary, nd, posdef, pattern_symmetry, numerical_symmetry, kind,
                 pattern_entries):
        self.matrix_id = matrix_id
        self.group = group
        self.name = name
        self.rows = rows
        self.columns = columns
        self.nonzeros = nonzeros
        self.real = real
        self.binary = binary
        self.nd = nd
        self.posdef = posdef
        self.pattern_symmetry = pattern_symmetry
        self.numerical_symmetry = numerical_symmetry
        self.kind = kind
        self.pattern_entries = pattern_entries


class Collection:
    """Statistics for the SuiteSparse Matrix Collection."""
    def __init__(self, num_matrices, date, matrices):
        self.num_matrices = num_matrices
        self.date = date
        self.matrices = matrices


def parse_stats(path):
    """Parse the index of all the matrices in the SuiteSparse Matrix Collection."""
    with open(path, 'r') as f:
        r = csv.reader(f)
        num_matrices = int(next(r)[0])
        date = next(r)[0]
        matrices = []
        matrix_id = 1

        for (group, name, rows, columns, nonzeros,
             real, binary, nd, posdef, pattern_symmetry,
             numerical_symmetry, kind, pattern_entries) in r:
            matrix = Matrix(
                matrix_id, group, name, int(rows), int(columns), int(nonzeros),
                real == '1', binary == '1', nd == '1', posdef == '1',
                pattern_symmetry == '1', numerical_symmetry == '1', kind,
                int(pattern_entries))
            matrices.append(matrix)
            matrix_id = matrix_id + 1
        return Collection(num_matrices, date, matrices)
