"""python3-test kernel

A subclass of the standard python3 kernel with the `getpass()` function
modified to obtain values from environment variables.
"""

import sys
import os
from ipykernel.ipkernel import IPythonKernel


class BatchIPythonKernel(IPythonKernel):
    def getpass(self, prompt='', stream=None):
        var_name = '_'.join([
            ''.join(
                filter(str.isalnum, word)
            ).upper() for word in prompt.split()
        ])
        if var_name not in os.environ:
            raise RuntimeError(f'{var_name} not found in the environment')
        return os.environ[var_name]


if __name__ == "__main__":
    # Remove the CWD from sys.path while we load stuff.
    # This is added back by InteractiveShellApp.init_path()
    if sys.path[0] == "":
        del sys.path[0]


    from ipykernel.kernelapp import IPKernelApp
    IPKernelApp.launch_instance(kernel_class=BatchIPythonKernel)
