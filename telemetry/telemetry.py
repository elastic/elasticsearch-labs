# Notebook Telemetry
#
# Elastic relies on anonymous usage statistics to continuously improve. This
# script allows us to see which notebooks are most used, which in turn helps us
# redirect our efforts to the areas that matter most to our users.
#
# What data is collected?
#
# This script configures your elasticsearch client to send a custom user agent
# string with requests made to Elastic Cloud. The new user agent only contains
# the name of the notebook. Here is an example user agent:
#
#     searchlabs/00-quick-start
#
# No other data is collected by this script.

import os


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


def enable_telemetry(client, notebook_name=None):
    """Enable telemetry for the given elasticsearch client instance."""
    if "nbtest" in os.environ.get("_", ""):
        # no telemetry for tests
        return

    if notebook_name is None:
        notebook_name = get_notebook_name()

    client.options(
        headers={**client._headers, "User-Agent": f"searchlabs/{notebook_name}"}
    )
    print(f'Telemetry enabled for "{notebook_name}". Thank you!')
