import torch
from transformers import XLMRobertaForSequenceClassification, XLMRobertaTokenizer
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, f1_score
from preprocess import load_and_preprocess_data, create_train_val_test_split

model = XLMRobertaForSequenceClassification.from_pretrained('../model')
tokenizer = XLMRobertaTokenizer.from_pretrained('../model')
df = load_and_preprocess_data('data/stress_dataset.csv')
_, _, test_df = create_train_val_test_split(df)

def tokenize_function(examples):
    return tokenizer(examples, padding='max_length', truncation=True, max_length=128, return_tensors='pt')

preds, trues = [], []
model.eval()
with torch.no_grad():
    for _, row in test_df.iterrows():
        inp = tokenize_function([row['cleaned_text']])
        out = model(**inp)
        pred = torch.argmax(out.logits, dim=1).item()
        preds.append(pred)
        trues.append(row['label'])

print("\n=== Classification Report ===")
print(classification_report(trues, preds, target_names=['Normal','Mild Stress','High Stress']))
print("\nConfusion Matrix:\n", confusion_matrix(trues, preds))
print(f"\nAccuracy: {accuracy_score(trues, preds):.4f}")
print(f"Weighted F1: {f1_score(trues, preds, average='weighted'):.4f}")
