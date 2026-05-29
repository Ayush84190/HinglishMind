from flask import Flask, request, jsonify
from flask_cors import CORS
import torch
from transformers import DistilBertForSequenceClassification, DistilBertTokenizer
import re

app = Flask(__name__)
CORS(app)

# Load your trained model
model_path = './model'
model = DistilBertForSequenceClassification.from_pretrained(model_path)
tokenizer = DistilBertTokenizer.from_pretrained(model_path)
model.eval()

TRIGGER_WORDS = {
    2: ['blank', 'fail', 'anxiety', 'tension', 'darr', 'hopeless', 'discouraged',
        'bhool gaya', 'kuch nahi aata', 'sharam', 'dread', 'khatam', 'rona', 
        'pressure', 'neend nahi', 'soye nahi', 'khana nahi', 'bhag jaun']
}

def highlight_triggers(text, label):
    if label != 2:
        return text
    for w in TRIGGER_WORDS[2]:
        text = re.sub(re.escape(w), f'**{w}**', text, flags=re.IGNORECASE)
    return text

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    text = data.get('text', '')
    if not text:
        return jsonify({'error': 'No text'}), 400
    
    inputs = tokenizer(text, return_tensors='pt', truncation=True, max_length=128)
    with torch.no_grad():
        outputs = model(**inputs)
        probs = torch.softmax(outputs.logits, dim=1)
        pred = torch.argmax(probs, dim=1).item()
        conf = probs[0][pred].item()
    
    label_map = {0: 'Normal', 1: 'Mild Stress', 2: 'High Stress'}
    return jsonify({
        'text': text,
        'highlighted_text': highlight_triggers(text, pred),
        'predicted_label': pred,
        'predicted_class': label_map[pred],
        'confidence': round(conf * 100, 2),
        'probabilities': {
            'Normal': round(probs[0][0].item() * 100, 2),
            'Mild Stress': round(probs[0][1].item() * 100, 2),
            'High Stress': round(probs[0][2].item() * 100, 2)
        }
    })

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'model_loaded': True})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
