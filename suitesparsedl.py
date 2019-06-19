"""Tools for downloading data from the SuiteSparse matrix collection."""

from multiprocessing.dummy import Pool
import os
import subprocess
import sys
import urllib.parse

import suitesparse

# The --show-progress option is only available for wget 1.16 and
# newer versions.
wget_version = subprocess.check_output(
    ['wget', '--version']).decode('utf-8').rstrip()
wget_version_tuple = tuple(map(int, (wget_version.split(' ')[2].split("."))))
wget_version_major = wget_version_tuple[0]
wget_version_minor = wget_version_tuple[1]
wget_has_show_progress = (
    wget_version_major == 1 and wget_version_minor >= 16)

def download_file(url, prefix, verbose=False, wget_args=[]):
    """Download a file using wget."""
    command = (['wget', '-N']
               + ([] if verbose else ['-q'])
               + (['-q', '--show-progress', '--progress=bar:force:noscroll'] if wget_has_show_progress else [])
               + ['-P', prefix]
               + wget_args
               + [url])

    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (stdout, stderr) = process.communicate()
    while process.poll() is None:
        sys.stdout.write(stdout.decode())
        sys.stdout.write(stderr.decode())

    if process.returncode != 0:
        raise RuntimeError(
            'Command failed with exit code {} ({})\n'
            'command: {}\nstdout: {}\nstderr: {}\n'.format(
                process.returncode,
                os.strerror(process.returncode),
                ' '.join(command),
                stdout.decode(),
                stderr.decode()))

    sys.stdout.write(stdout.decode())
    sys.stdout.write(stderr.decode())


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
    suitesparse_collection = suitesparse.parse_stats(ssstats_path)
    with Pool(processes=jobs) as pool:
        pool.map(
            lambda matrix: download_matrix(suitesparse_url, prefix, matrix, verbose, wget_args),
            suitesparse_collection.matrices)
