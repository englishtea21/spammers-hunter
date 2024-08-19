import torch
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification

import os

# implements basic interface of spam detector


class SpamDetector:
    def __init__(self):
        # Initialize tokenizer and model

        self.tokenizer = DistilBertTokenizer.from_pretrained(
            os.getenv("TOKENIZER_PATH")
        )
        self.model = DistilBertForSequenceClassification.from_pretrained(
            os.getenv("MODEL_PATH")
        )

        # Set the device for model inference
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)
        self.model.eval()

    # checks whether the text is spam with built text tokenization
    def is_spam(self, text: str) -> bool:
        inputs = self.tokenizer(
            text, return_tensors="pt", truncation=True, padding=True
        )
        inputs = {key: value.to(self.device) for key, value in inputs.items()}

        with torch.no_grad():
            outputs = self.model(**inputs)

        logits = outputs.logits
        prediction = torch.argmax(logits, dim=1).item()

        # Assuming 1 is the label for spam and 0 for not spam
        return prediction == 1
