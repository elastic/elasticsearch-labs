from llama_index.core import SimpleDirectoryReader

class LlamaIndexProcessor:
    def __init__(self):
        pass 
    
    def load_documents(self, directory_path):
        ''' 
        Load all documents in directory
        '''
        reader = SimpleDirectoryReader(input_dir=directory_path)
        return reader.load_data()
    