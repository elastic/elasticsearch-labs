#!/usr/bin/env python
import argparse
from copy import deepcopy
import difflib
import os
import re
import sys

# these suppress jupyter warnings on startup
os.environ['PYDEVD_DISABLE_FILE_VALIDATION'] = '1'
os.environ['JUPYTER_PLATFORM_DIRS'] = '1'

from jupyter_core.paths import jupyter_data_dir
from jupyter_client.kernelspec import KernelSpecManager
import nbformat
from nbconvert.preprocessors import ExecutePreprocessor
from rich import print as rprint
from rich.markdown import Markdown

basedir = os.path.abspath(os.path.dirname(__file__))

# The list of tuples below is used for masking parts of the output of code
# cells so that they do not trigger spurious diff errors.
# Each tuple has a regular expression to match, and a replacement string.
MASKS = [
    (r'instance-[0-9]+', 'instance-XXXXX'),
    (r'[0-9]+\.[0-9]+\.[0-9]+', '<major>.<minor>.<patch>'),
    (r"'cluster_name': '[^']+'", "'cluster_name': 'XXXXX'"),
    (r"'cluster_uuid': '[^']+'", "'cluster_uuid': 'XXXXX'"),
    (r"'build_hash': '[^']+'", "'build_hash': 'XXXXX'"),
    (r"'build_date': '[^']+'", "'build_date': 'XXXXX'"),
    (r"'_version': [0-9]+", "'_version': X"),
    (r'^ID: .*$', 'ID: XXXXX', 'ID: XXXXXX'),
    (r'^Score: [0-9]+\.[0-9][0-9]*$', 'Score: X.XXX'),
]


def register_python3_test_kernel():
    kernel_spec_manager = KernelSpecManager(data_dir=jupyter_data_dir())
    kernel_spec_manager.install_kernel_spec(
        os.path.join(basedir, 'python3-test'), 'python3-test', user=True)


def unregister_python3_test_kernel():
    kernel_spec_manager = KernelSpecManager(data_dir=jupyter_data_dir())
    kernel_spec_manager.remove_kernel_spec('python3-test')


def preprocess_output(output):
    """This function masks the output to hide insignificant differences."""
    for mask in MASKS:
        output = re.sub(mask[0], mask[1], output, flags=re.MULTILINE)
    return output


def diff_output(source_output, test_output):
    """Generate a diff report."""
    source_lines = [line + '\n' for line in source_output.split('\n')]
    test_lines = [line + '\n' for line in test_output.split('\n')]
    diff = ''.join(difflib.unified_diff(
        source_lines, test_lines, fromfile='source.txt', tofile='test.txt'))
    rprint(Markdown(f'```diff\n{diff}```\n', code_theme='vim'))


def nbtest_one(notebook, verbose):
    """Run a notebook and ensure output is the same as in the original."""
    rprint(f'Running [yellow]{notebook}[default]...', end='')

    try:
        with open(notebook, 'rt') as f:
            nb = nbformat.read(f, as_version=4)
    except FileNotFoundError:
        rprint(' [red]Not found[default]')
        return 1
    original_cells = deepcopy(nb.cells)

    ep = ExecutePreprocessor(timeout=600, kernel_name='python3-test')
    try:
        ep.preprocess(nb, {'metadata': {'path': basedir}})
    except Exception as exc:
        rprint(' [red]Failed[default]')
        print(exc)
        return 1

    ret = 0
    cell = 0
    for source, test in zip(original_cells, nb.cells):
        cell += 1
        if source['cell_type'] == 'code':
            source_output = {
                output.get('name', '?'): output.get('text', '')
                for output in source['outputs']
            }
            test_output = {
                output.get('name', '?'): output.get('text', '')
                for output in test['outputs']
            }
            for name in source_output:
                if name not in ['stdout', 'stderr']:
                    if verbose:
                        rprint(f'>>>>> [magenta]code cell #{cell}({name})'
                               '[default]: [dim white]Skipped[default]')
                    continue
                base = preprocess_output(str(source_output[name]))
                current = preprocess_output(str(test_output.get(name, '')))
                if  base == current:
                    if verbose:
                        rprint(f'>>>>> [yellow]code cell #{cell}/({name})'
                               '[default]: [green]OK[default]')
                else:
                    if ret == 0:
                        ret = 1
                        rprint(' [red]Failed[default]')
                    rprint(f'>>>>> [yellow]code cell #{cell}/({name})'
                           '[default]: [red]Error[default]')
                    diff_output(base, current)
        else:
            if verbose:
                rprint(f'>>>>> [magenta]{source["cell_type"]} cell #{cell}'
                       '[default]: [dim white]Skipped[default]')
    if ret == 0:
        rprint(' [green]OK[default]')
    return ret



def nbtest(notebook, verbose):
    """Main entry point. The given notebooks are executed, and for any cells
    that include output, the newly generated output is diffed.
    """
    ret = 0
    for nb in notebook:
        ret += nbtest_one(notebook=nb, verbose=verbose)
    return ret


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('notebooks', nargs='+')
    parser.add_argument('-v', '--verbose', action='store_true')
    return parser.parse_args()


def main():
    args = parse_args()
    register_python3_test_kernel()
    try:
        sys.exit(nbtest(**args.__dict__))
    finally:
        unregister_python3_test_kernel()


if __name__ == '__main__':
    main()
