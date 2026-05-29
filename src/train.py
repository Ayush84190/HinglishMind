import torch
from transformers import XLMRobertaForSequenceClassification, XLMRobertaTokenizer, Trainer, TrainingArguments
from datasets import Dataset
from sklearn.metrics import accuracy_score, f1_score
import numpy as np
from preprocess import load_and_preprocess_data, create_train_val_test_split

df = load_and_preprocess_data('data/stress_dataset.csv')
train_df, val_df, test_df = create_train_val_test_split(df)

tokenizer = XLMRobertaTokenizer.from_pretrained('xlm-roberta-base')

def tokenize_function(examples):
    return tokenizer(examples, padding='max_length', truncation=True, max_length=128)

train_enc = tokenize_function(train_df['cleaned_text'].tolist())
val_enc = tokenize_function(val_df['cleaned_text'].tolist())

train_dataset = Dataset.from_dict({'input_ids': train_enc['input_ids'], 'attention_mask': train_enc['attention_mask'], 'labels': train_df['label'].tolist()})
val_dataset = Dataset.from_dict({'input_ids': val_enc['input_ids'], 'attention_mask': val_enc['attention_mask'], 'labels': val_df['label'].tolist()})

model = XLMRobertaForSequenceClassification.from_pretrained('xlm-roberta-base', num_labels=3,
    id2label={0:'Normal',1:'Mild Stress',2:'High Stress'},
    label2id={'Normal':0,'Mild Stress':1,'High Stress':2})

def compute_metrics(eval_pred):
    preds = np.argmax(eval_pred.predictions, axis=1)
    return {'accuracy': accuracy_score(eval_pred.label_ids, preds), 'f1': f1_score(eval_pred.label_ids, preds, average='weighted')}

training_args = TrainingArguments(
    output_dir='./results', num_train_epochs=5, per_device_train_batch_size=8, per_device_eval_batch_size=8,
    warmup_steps=100, weight_decay=0.01, logging_dir='./logs', logging_steps=10,
    eval_strategy='epoch', save_strategy='epoch', load_best_model_at_end=True, metric_for_best_model='f1', report_to='none')

trainer = Trainer(model=model, args=training_args, train_dataset=train_dataset, eval_dataset=val_dataset, compute_metrics=compute_metrics)
trainer.train()

model.save_pretrained('../model')
tokenizer.save_pretrained('../model')
print("✅ Model saved to ../model")

# Quick test eval
test_enc = tokenize_function(test_df['cleaned_text'].tolist())
test_dataset = Dataset.from_dict({'input_ids': test_enc['input_ids'], 'attention_mask': test_enc['attention_mask'], 'labels': test_df['label'].tolist()})
results = trainer.evaluate(test_dataset)
print(f"📊 Test results: {results}")
