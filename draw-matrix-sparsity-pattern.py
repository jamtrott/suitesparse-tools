#!/usr/bin/env python3

"""Plot the sparsity pattern of a sparse matrix.

Load a sparse matrix in the matrix market format create a figure
displaying the sparsity pattern of the matrix. The sparsity pattern
shows the locations of non-zero entries in the matrix.

"""

import argparse
import os
import sys
import tarfile

import matplotlib.pyplot as plt
from matplotlib.ticker import NullLocator
import numpy as np
import scipy.sparse


def draw_matrix_sparsity_pattern(
        matrix,
        precision=0,
        marker=',',
        markersize=1.0,
        title=None,
        title_fontdict=None,
        title_loc='center',
        title_pad=None,
        size=None,
        axis_frameon=None,
        xaxis_major_locator=None,
        xaxis_minor_locator=None,
        yaxis_major_locator=None,
        yaxis_minor_locator=None):
    """Render a figure."""
    f = plt.figure()
    ax = f.gca()

    if axis_frameon is not None:
        ax.set_frame_on(axis_frameon)
    if size:
        f.set_size_inches(*size)
    if title:
        ax.set_title(title, fontdict=title_fontdict,
                     loc=title_loc, pad=title_pad)

    ax.spy(matrix,
           precision=precision,
           marker=marker,
           markersize=markersize)

    ax.get_xaxis().set_major_locator(xaxis_major_locator)
    ax.get_xaxis().set_minor_locator(xaxis_minor_locator)
    ax.get_yaxis().set_major_locator(yaxis_major_locator)
    ax.get_yaxis().set_minor_locator(yaxis_minor_locator)
    return f


def save_figure(figure, filename, dpi=300, verbose=False):
    """Save a figure to the given filename."""
    if verbose:
        print('Saving figure to {}'.format(filename))
    figure.savefig(filename, dpi=dpi, bbox_inches='tight')
    plt.close(figure)


class Matrix:
    def __init__(
            self, rows, columns, numEntries,
            row_index, column_index, values):
        self.rows = rows
        self.columns = columns
        self.numEntries = numEntries
        self.row_index = row_index
        self.column_index = column_index
        self.values = values


def matrix_market_to_coo(matrix):
    return scipy.sparse.coo_matrix(
        (matrix.values, (matrix.row_index, matrix.column_index)))


def load_matrix_market(f):
    line = f.readline()
    while line and line.startswith(b'%'):
        line = f.readline()

    x = line.split()
    rows = int(x[0])
    columns = int(x[1])
    numEntries = int(x[2])

    row_index = np.zeros(numEntries).astype(int)
    column_index = np.zeros(numEntries).astype(int)
    values = np.zeros(numEntries)

    n = 0
    for line in f:
        x = line.split()
        row_index[n] = int(x[0])
        column_index[n] = int(x[1])
        values[n] = float(x[2])
        n = n + 1

    return Matrix(
        rows, columns, numEntries,
        row_index, column_index, values)


def mmspy(filename, precision=0, size=None, title=None, title_fontdict=None):
    tarball = None
    matrix = None

    print('Loading matrix from {}'.format(filename))
    if ".tar.gz:" in filename:
        tarball, filename = filename.split(":")
        with tarfile.open(tarball, 'r') as tar:
            with tar.extractfile(filename) as f:
                matrix = load_matrix_market(f)
    else:
        with open(filename, 'rb') as f:
            matrix = load_matrix_market(f)

    coo_matrix = matrix_market_to_coo(matrix)

    fig = draw_matrix_sparsity_pattern(
        coo_matrix, precision=precision,
        title=title, title_fontdict=title_fontdict,
        size=size,
        xaxis_major_locator=NullLocator(),
        xaxis_minor_locator=NullLocator(),
        yaxis_major_locator=NullLocator(),
        yaxis_minor_locator=NullLocator())
    return fig


def main():
    parser = argparse.ArgumentParser(
        prog=sys.argv[0],
        description='Plot the sparsity pattern of a sparse matrix')
    parser.add_argument('FILE', nargs=1, help='File in matrix market format')
    parser.add_argument('--output-file', metavar='PATH')
    parser.add_argument('--width', metavar='W', type=float, default=6,
                        help='Width in inches')
    parser.add_argument('--height', metavar='H', type=float, default=6,
                        help='Height in inches')
    parser.add_argument('--dpi', metavar='DPI', type=int, default=300,
                        help='Figure resolution in dots-per-inch')
    args = parser.parse_args()

    filename = args.FILE[0]
    matrix_name = os.path.splitext(os.path.basename(filename))[0]
    figure = mmspy(filename, size=(args.width, args.height), title=matrix_name)
    output_path = '{}.png'.format(matrix_name)
    save_figure(figure, output_path, dpi=args.dpi, verbose=True)


if __name__ == '__main__':
    main()
