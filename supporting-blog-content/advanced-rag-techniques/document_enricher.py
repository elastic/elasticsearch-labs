from tqdm import tqdm


class DocumentEnricher:

    def __init__(self):
        pass 

    def enrich_document(self, documents, processors, text_col='text'):
        for doc in tqdm(documents, desc="Enriching documents using processors: "+str(processors)): 
            for (processor, field) in processors: 
                metadata=processor(doc[text_col])
                if isinstance(metadata, list):
                    metadata='\n'.join(metadata)
                doc.update({field: metadata})
 
    