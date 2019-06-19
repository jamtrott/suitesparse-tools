#!/usr/bin/env python3

"""Download matrices from the SuiteSparse matrix collection.

For example, the command:
  > python3 download-suitesparse.py -j10

will download all the matrices in the SuiteSparse Matrix Collection
and place them in the folder suitesparse/.  The matrices may be
downloaded in parallel, if a number of jobs are specified.

"""

import argparse
import suitesparsedl


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
        help='Download the files to the specified location (default: {})'.format(default_prefix))
    parser.add_argument(
        '--suitesparse-url', metavar='URL',
        default=default_url,
        help='URL to the SuiteSparse Matrix Collection (default: {})'.format(default_url))
    parser.add_argument(
        '-j', '--jobs', metavar='N', type=int,
        default=1, help='Number of jobs to download matrices simultaneously (default: {})'.format(default_jobs))
    parser.add_argument(
        '-v', '--verbose', action="store_true")
    parser.add_argument('wget_args', metavar='...', nargs=argparse.REMAINDER, help='Arguments passed to wget')
    args, remainder = parser.parse_known_args()

    suitesparsedl.download_matrices(
        args.suitesparse_url, args.prefix, args.jobs, args.verbose, remainder)


if __name__ == '__main__':
    main()
