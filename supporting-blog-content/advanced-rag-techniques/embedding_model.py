import torch
from transformers import pipeline, AutoTokenizer
from tqdm import tqdm

class EmbeddingModel:
    def __init__(self, model_name):
        if torch.backends.mps.is_available():
            self.device = "mps"
            print("Using MPS")
        else:
            self.device = "cpu"
            print("Using CPU")
        ''' 
        Initialize embedding model and pipeline. 
        Load into mac GPU (Change to cuda if using nvidia)
        '''
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.embedding_pipeline = pipeline("feature-extraction", 
                                            model=model_name, 
                                            trust_remote_code=True, 
                                            device=self.device)
        
    def get_embeddings_from_text(self, texts):
        ''' 
        Given a list of strings or a list of lists of strings, 
        return a list of embeddings (List of floating point numbers).
        If a list of lists is provided, each inner list is joined with newlines.
        '''
        # Check if the input is a list of lists
        if isinstance(texts[0], list):
            # Join each inner list with newlines
            texts = ['\n'.join(inner_list) for inner_list in texts]
        
        embeddings = self.embedding_pipeline(texts, 
                                            truncation=True, 
                                            padding=True, 
                                            max_length=512)
        return embeddings
    

    def embed_documents_text_wise(self, documents, text_field="chunk", embedding_field_postfix="_embedding", batch_size=32):
        ''' 
        Given a list of document objects, grab the text, 
        batch embed, then put the embeddings into the document objects.
        '''
        for i in tqdm(range(0, len(documents), batch_size), desc="Embedding documents"):
            batch = documents[i:i+batch_size]
            texts = [doc[text_field] for doc in batch]
            embeddings = self.get_embeddings_from_text(texts)
            for doc, embedding in zip(batch, embeddings):
                doc.update({text_field+embedding_field_postfix:embedding[0][0]})
        return text_field+embedding_field_postfix
    

    def get_embeddings_from_tokens(self, token_lists, max_length=512):
        ''' 
        Given a list of token ID lists, return a list of embeddings 
        Pad or truncate input to max_length
        '''
        # Determine the device
        device = next(self.embedding_pipeline.model.parameters()).device

        # Pad or truncate token lists to max_length
        padded_token_lists = [
            tokens[:max_length] + [self.embedding_pipeline.tokenizer.pad_token_id] * (max_length - len(tokens))
            for tokens in token_lists
        ]

        # Convert list of token lists to a 2D tensor and move to the correct device
        input_ids = torch.tensor(padded_token_lists).to(device)
        
        # Create attention mask (1 for real tokens, 0 for padding)
        attention_mask = (input_ids != self.embedding_pipeline.tokenizer.pad_token_id).long().to(device)
        
        with torch.no_grad():
            outputs = self.embedding_pipeline.model(input_ids, attention_mask=attention_mask)
            # Mean pooling - take average of all tokens
            embeddings = outputs.last_hidden_state.mean(dim=1)
        
        return embeddings.cpu().tolist()

    def embed_documents_token_wise(self, documents, token_field="chunk", embedding_field_postfix="_embedding", batch_size=32, max_length=512):
        ''' 
        Given a list of document objects which have been converted to tokens, get the tokens
        batch embed, then put the embeddings into the document objects.
        Pad or truncate input to max_length
        '''
        for i in tqdm(range(0, len(documents), batch_size), desc="Embedding documents"):
            batch = documents[i:i+batch_size]
            texts = [doc[token_field][:max_length] for doc in batch]  # Truncate if necessary
            embeddings = self.get_embeddings_from_tokens(texts, max_length)
            for doc, embedding in zip(batch, embeddings):
                doc.update({token_field+embedding_field_postfix:embedding})
        return token_field+embedding_field_postfix


    
    # def tokenize(self, text):
    #     """
    #     Tokenize the input text using the model's tokenizer.
    #     """
    #     return self.tokenizer.encode(text, add_special_tokens=False)
    
    # def decode(self, tokens):
    #     """
    #     Tokenize the input text using the model's tokenizer.
    #     """
    #     return self.tokenizer.decode(tokens)