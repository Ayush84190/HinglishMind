import pandas as pd
import re
from sklearn.model_selection import train_test_split
from transformers import XLMRobertaTokenizer

def clean_text(text):
    text = str(text)
    text = re.sub(r'\s+', ' ', text)
    text = text.strip().lower()
    return text

def load_and_preprocess_data(csv_path='data/stress_dataset.csv'):
    df = pd.read_csv(csv_path)
    df['cleaned_text'] = df['text'].apply(clean_text)
    df = df.dropna(subset=['label'])
    df['label'] = df['label'].astype(int)
    print(f"✅ Loaded {len(df)} samples")
    print(f"📊 Class dist:\n{df['label'].value_counts().sort_index()}")
    return df

def tokenize_dataset(df, model_name='xlm-roberta-base', max_length=128):
    tokenizer = XLMRobertaTokenizer.from_pretrained(model_name)
    def tokenize_function(examples):
        return tokenizer(examples, padding='max_length', truncation=True, max_length=max_length, return_tensors=None)
    tokenized = tokenize_function(df['cleaned_text'].tolist())
    return tokenized, tokenizer

def create_train_val_test_split(df, train_ratio=0.8, val_ratio=0.1, test_ratio=0.1):
    train_val, test = train_test_split(df, test_size=test_ratio, random_state=42, stratify=df['label'])
    val_ratio_adjusted = val_ratio / (train_ratio + val_ratio)
    train, val = train_test_split(train_val, test_size=val_ratio_adjusted, random_state=42, stratify=train_val['label'])
    print(f"📊 Split: Train={len(train)}, Val={len(val)}, Test={len(test)}")
    return train, val, test

if __name__ == "__main__":
    df = load_and_preprocess_data()
    train, val, test = create_train_val_test_split(df)
    tokenized, _ = tokenize_dataset(df.head(5))
    print("✅ Tokenization OK")
