# Notebook Telemetry
#
# Elastic relies on anonymous usage statistics to continuously improve. This
# script allows us to see which notebooks are most used, which in turn helps us
# redirect our efforts to the areas that matter most to our users.
#
# What data is collected?
#
# This script configures your elasticsearch client to send a custom user agent
# string with requests made to Elastic Cloud. The new user agent contains
# the name of the notebook and the platform you are running it on. Here is an
# example user agent:
#
#     searchlabs-py/00-quick-start (Colab)
#
# No other data is collected by this script.

import os

SEARCHLABS_USER_AGENT = "searchlabs-py"


def get_notebook_name():
    """Return the name of the running notebook."""
    name = "unknown"

    # first we try to get the name from the Jupyter environment
    if os.environ.get("JPY_SESSION_NAME"):
        name = os.path.basename(os.environ["JPY_SESSION_NAME"])

    # next we check for Visual Studio Code metadata
    elif "__vsc_ipynb_file__" in globals():
        name = os.path.basename(globals()["__vsc_ipynb_file__"])
    # else we try to get it from the Colab environment
    else:
        import requests

        try:
            name = requests.get("http://172.28.0.12:9000/api/sessions").json()[0][
                "name"
            ]
        except Exception:
            pass

    return name.split(".ipynb")[0].lower()


def get_notebook_platform():
    """Return the platform under which the notebook is running."""
    platform = "Unknown"

    if "VSCODE_PID" in os.environ:
        platform = "VSCode"
    elif "COLAB_RELEASE_TAG" in os.environ:
        platform = "Colab"
    elif "JPY_SESSION_NAME" in os.environ:
        platform = "Jupyter"
    else:
        platform = "Unknown"
    return platform


def enable_telemetry(client, notebook_name=None):
    """Enable telemetry for the given elasticsearch client instance."""
    if "nbtest" in os.environ.get("_", ""):
        # no telemetry for tests
        return client

    platform = get_notebook_platform()
    if notebook_name is None:
        notebook_name = get_notebook_name()

    client = client.options(
        headers={"user-agent": f"{SEARCHLABS_USER_AGENT}/{notebook_name} ({platform})"}
    )
    print(f'Telemetry enabled for "{notebook_name}". Thank you!')
    return client
