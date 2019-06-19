#!/usr/bin/env python3

"""Download matrices from the SuiteSparse matrix collection.

For example, the command:
  > python3 download-suitesparse.py -j10

will download all the matrices in the SuiteSparse Matrix Collection
and place them in the folder suitesparse/.  The matrices may be
downloaded in parallel, if a number of jobs are specified.

"""

import argparse
import csv
import os
import subprocess
import sys
import urllib.parse

from multiprocessing.dummy import Pool


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


def wget_has_show_progress():
    """Check for a version of wget that supports progress bars.

    The --show-progress option is available since wget 1.16.
    """
    wget_version = subprocess.check_output(
    ['wget', '--version']).decode().rstrip()
    wget_version_tuple = tuple(map(int, (wget_version.split(' ')[2].split("."))))
    wget_version_major = wget_version_tuple[0]
    wget_version_minor = wget_version_tuple[1]
    wget_has_show_progress = (wget_version_major == 1 and wget_version_minor >= 16)
    return wget_has_show_progress


def download_file(url, prefix, verbose=False, wget_args=[]):
    """Download a file using wget."""
    command = (['wget', '-N']
               + ([] if verbose else ['-q'])
               + (['--show-progress', '--progress=bar:force:noscroll']
                  if wget_has_show_progress() else [])
               + ['-P', prefix]
               + wget_args
               + [url])

    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    returncode = None
    while returncode is None:
        try:
            (stdout, stderr) = process.communicate(timeout=1)
        except subprocess.TimeoutExpired:
            (stdout, stderr) = process.communicate()
        sys.stdout.write(stdout.decode())
        sys.stdout.write(stderr.decode())
        returncode = process.poll()

    if process.returncode != 0:
        raise RuntimeError(
            'Command failed with exit code {} ({})\n'
            'command: {}\nstdout: {}\nstderr: {}\n'.format(
                process.returncode,
                os.strerror(process.returncode),
                ' '.join(command),
                stdout.decode(),
                stderr.decode()))


def download_stats(suitesparse_url, prefix, verbose=False, wget_args=[]):
    """Get the index of all the matrices in the SuiteSparse Matrix Collection."""
    output_path = os.path.join(prefix, 'ssstats.csv')
    url = urllib.parse.urljoin(suitesparse_url, 'files/ssstats.csv')
    download_file(url, prefix, verbose, wget_args)
    return output_path


def download_matrix(suitesparse_url, prefix, matrix, verbose=False, wget_args=[]):
    """Download a matrix from the SuiteSparse Matrix Collection using wget."""
    output_path = os.path.join(prefix, matrix.group, '{}.tar.gz'.format(matrix.name))
    if os.path.isfile(output_path):
        return output_path

    url = '{}/MM/{}/{}.tar.gz'.format(suitesparse_url, matrix.group, matrix.name)
    download_file(url, os.path.join(prefix, matrix.group), verbose, wget_args)
    return output_path


def download_matrices(suitesparse_url, prefix, jobs=1, verbose=False, wget_args=[]):
    if not os.path.exists(prefix):
        os.makedirs(prefix)

    ssstats_path = download_stats(suitesparse_url, prefix, verbose, wget_args)
    suitesparse_collection = parse_stats(ssstats_path)
    with Pool(processes=jobs) as pool:
        pool.map(
            lambda matrix: download_matrix(
                suitesparse_url, prefix, matrix, verbose, wget_args),
            suitesparse_collection.matrices)


def main():
    """Download the matrices in the SuiteSparse Matrix Collection."""
    default_prefix = 'suitesparse/'
    default_url = 'https://sparse.tamu.edu/'
    default_jobs = 1

    parser = argparse.ArgumentParser(
        description="Download the matrices in the SuiteSparse Matrix Collection.")
    parser.add_argument(
        '--prefix', metavar='PATH',
        default=default_prefix,
        help='Download the files to the specified location (default: {})'
        .format(default_prefix))
    parser.add_argument(
        '--suitesparse-url', metavar='URL',
        default=default_url,
        help='URL to the SuiteSparse Matrix Collection (default: {})'
        .format(default_url))
    parser.add_argument(
        '-j', '--jobs', metavar='N', type=int,
        default=1,
        help='Number of jobs to download matrices simultaneously (default: {})'
        .format(default_jobs))
    parser.add_argument(
        '-v', '--verbose', action="store_true")
    parser.add_argument(
        'wget_args', metavar='...', nargs=argparse.REMAINDER,
        help='Arguments passed to wget')
    args, remainder = parser.parse_known_args()

    download_matrices(
        args.suitesparse_url, args.prefix, args.jobs, args.verbose, remainder)


if __name__ == '__main__':
    main()
