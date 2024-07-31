import uuid
import re


class Chunker: 
    def __init__(self, tokenizer):
        self.tokenizer = tokenizer 
    
    def split_into_sentences(self, text):
        """Split text into sentences."""
        return re.split(r'(?<=[.!?])\s+', text)

        
    def enrich_document(self, documents, processors, text_col='text'):
        for doc in documents: 
            for (processor, field) in processors: 
                doc.update({field: processor(doc[text_col])})
 
    def sentence_wise_tokenized_chunk_documents(self, documents, chunk_size=256, overlap=20, min_chunk_size=50):
        """
        Chunk documents based on the specified flow:
        1. Split text into sentences.
        2. Tokenize using the provided tokenizer method.
        3. Build chunks up to the chunk_size limit.
        4. Create overlap based on tokens.
        5. Only add chunks that meet the minimum token size requirement.
        """
        chunked_documents = []

        for doc in documents:
            sentences = self.split_into_sentences(doc['text'])
            tokens = []
            sentence_boundaries = [0]

            # Tokenize all sentences and keep track of sentence boundaries
            for sentence in sentences:
                sentence_tokens = self.tokenizer.encode(sentence, add_special_tokens=True)
                tokens.extend(sentence_tokens)
                sentence_boundaries.append(len(tokens))

            # Create chunks
            chunk_start = 0
            while chunk_start < len(tokens):
                chunk_end = chunk_start + chunk_size

                # Find the last complete sentence that fits in the chunk
                sentence_end = next((i for i in sentence_boundaries if i > chunk_end), len(tokens))
                chunk_end = min(chunk_end, sentence_end)

                # Create the chunk
                chunk_tokens = tokens[chunk_start:chunk_end]

                # Check if the chunk meets the minimum size requirement
                if len(chunk_tokens) >= min_chunk_size:
                    # Create a new document object for this chunk
                    chunk_doc = {
                        'id_': str(uuid.uuid4()),
                        'chunk': chunk_tokens,
                        'original_text': self.tokenizer.decode(chunk_tokens),
                        'chunk_index': len(chunked_documents),
                        'parent_id': doc['id_'],
                        'chunk_token_count': len(chunk_tokens)
                    }

                    # Copy all other fields from the original document
                    for key, value in doc.items():
                        if key != 'text' and key not in chunk_doc:
                            chunk_doc[key] = value

                    chunked_documents.append(chunk_doc)

                # Move to the next chunk start, considering overlap
                chunk_start = max(chunk_start + chunk_size - overlap, chunk_end - overlap)

        return chunked_documents