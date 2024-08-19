import torch
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification

import os


class SpamDetector:
    def __init__(self):
        # Initialize tokenizer and model

        print(os.path.abspath("./aiogram-bot/spam_detection/tokenizer"))
        print(os.path.abspath("./aiogram-bot/spam_detection/model"))

        self.tokenizer = DistilBertTokenizer.from_pretrained(
            "./aiogram-bot/spam_detection/tokenizer"
        )
        self.model = DistilBertForSequenceClassification.from_pretrained(
            "./aiogram-bot/spam_detection/model"
        )

        # Set the device for model inference
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)
        self.model.eval()

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
