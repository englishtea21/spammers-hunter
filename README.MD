# Telegram Anti-Spam Bot

This project is a Telegram bot designed to protect groups from spam using a classification model based on DistilBERT (multi-language cased) from transformers package. The bot utilizes a machine learning model trained to identify spam messages in both English and Russian, along with other languages, to ensure effective spam detection in various contexts.

## Features

- **Spam Detection**: Identifies and handles spam messages in Telegram groups.
- **Customizable**: Adjust spam detection parameters and manage blocked users.
- **Efficient**: Leverages a pre-trained DistilBERT model for fast and accurate classification.

## Datasets Used

The model was trained on the following datasets:

- **Russian Spam Dataset**:
  - [spam_dataset_v6](https://huggingface.co/datasets/RUSpam/spam_dataset_v6)
- **English Spam Datasets**: 
  - [Telegram Spam Dataset](https://huggingface.co/datasets/thehamkercat/telegram-spam-ham)
  - [SMS Spam Dataset](https://huggingface.co/datasets/ucirvine/sms_spam)
  - [General Spam Detection Dataset](https://huggingface.co/datasets/Deysi/spam-detection-dataset)

These datasets contain a variety of spam messages, including SMS spam, and feature numerous emojis and special characters, aligning with the context of Telegram chats.

## Model Training

- **Sequence Length**: The model training took into account the fundamental limitations on sequence length, specifically the maximum message length in Telegram.
- **Special Characters**: The training data includes a large number of emojis and special characters to ensure robustness in the Telegram environment.

## Libraries Used

- **Telegram Bot Framework**:
  - `aiogram==3.12.0`
  - `aioschedule==0.5.2`
  - `aiosignal==1.3.1`
  - `async-timeout==4.0.3`

- **Machine Learning**:
  - `transformers==4.44.0`
  - `torch==2.4.0`

- **Configuration and Database**:
  - `pyyaml==6.0.2`
  - `python-dotenv==1.0.1`
  - `sqlalchemy==2.0.32`
  - `aiosqlite==0.20.0`
  - `asyncpg==0.29.0`
  - `dogpile.cache==1.3.3`

- **Other**:
  - `pytz==2024.1`
