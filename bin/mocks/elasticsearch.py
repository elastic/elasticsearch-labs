import os
import sys


def patch_elasticsearch():
    # preserve the original import path
    saved_path = sys.path.copy()

    # remove the path entry that refers to this directory
    for path in sys.path:
        if not path.startswith('/'):
            path = os.path.join(os.getcwd(), path)
        if __file__ == os.path.join(path, 'elasticsearch.py'):
            sys.path.remove(path)
            break

    # remove this module, and import the real one instead
    del sys.modules['elasticsearch']
    import elasticsearch

    # restore the import path
    sys.path = saved_path

    # preserve the original Elasticsearch.__init__ method   
    orig_es_init = elasticsearch.Elasticsearch.__init__

    # patched version of Elasticsearch.__init__ that connects to self-hosted
    # regardless of connection arguments given
    def patched_es_init(self, *args, **kwargs):
        if 'cloud_id' in kwargs:
            assert kwargs['cloud_id'] == 'foo'
        if 'api_key' in kwargs:
            assert kwargs['api_key'] == 'bar'
        return orig_es_init(self, 'http://localhost:9200')

    # patch Elasticsearch.__init__
    elasticsearch.Elasticsearch.__init__ = patched_es_init


patch_elasticsearch()
del patch_elasticsearch
