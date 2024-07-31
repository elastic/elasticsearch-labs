import spacy

class EntityExtractor:
    def __init__(self, model="en_core_web_lg", ignore_types=[
                                                            'CARDINAL',
                                                            'MONEY',
                                                            'NORP',
                                                            'ORDINAL',
                                                            'PERCENT',
                                                            'QUANTITY'
                                                            ]):
        # Load the spaCy model
        self.nlp = spacy.load(model)
        
        # Keep only the NER component in the pipeline
        self.nlp.select_pipes(enable=["ner"])

        # Set the list of entity types to ignore (default to empty list if None)
        self.ignore_types = ignore_types or []

    def extract_entities(self, text):
        # Process the text
        doc = self.nlp(text)
        
        # Extract entities, ignoring specified types
        entities = list(set([ent.text for ent in doc.ents if ent.label_ not in self.ignore_types]))
        
        return entities

    def get_entity_types(self):
        # Return the list of entity types the model can recognize, excluding ignored types
        all_types = self.nlp.get_pipe("ner").labels
        return [t for t in all_types if t not in self.ignore_types]

    def set_ignore_types(self, ignore_types):
        # Update the list of entity types to ignore
        self.ignore_types = ignore_types

    def get_ignore_types(self):
        # Return the current list of ignored entity types
        return self.ignore_types