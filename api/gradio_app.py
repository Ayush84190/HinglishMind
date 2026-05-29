import gradio as gr
import torch
from transformers import DistilBertForSequenceClassification, DistilBertTokenizer

print("🔄 Loading HinglishMind model...")
model = DistilBertForSequenceClassification.from_pretrained('./model')
tokenizer = DistilBertTokenizer.from_pretrained('./model')
model.eval()
print("✅ Model loaded!")

def predict(text):
    if not text or text.strip() == "":
        return "⚠️ Please enter some text"
    
    inputs = tokenizer(text, return_tensors='pt', truncation=True, max_length=128)
    with torch.no_grad():
        outputs = model(**inputs)
        probs = torch.softmax(outputs.logits, dim=1)
        pred = torch.argmax(probs, dim=1).item()
        confidence = probs[0][pred].item() * 100
    
    if pred == 0:
        return f"😊 **NORMAL**\nConfidence: {confidence:.1f}%\n\n✅ No stress detected. Keep up your balanced routine!"
    elif pred == 1:
        return f"😐 **MILD STRESS**\nConfidence: {confidence:.1f}%\n\n⚠️ Manageable pressure. Take short breaks when needed."
    else:
        return f"😰 **HIGH STRESS**\nConfidence: {confidence:.1f}%\n\n💪 This level needs attention. Consider talking to someone or taking a proper break."

# Create the web interface
with gr.Blocks(title="HinglishMind") as demo:
    gr.Markdown("# 🧠 HinglishMind")
    gr.Markdown("### Stress Detection for Hinglish Text (Hindi + English)")
    
    with gr.Row():
        with gr.Column():
            text_input = gr.Textbox(
                label="📝 Enter your text",
                placeholder="Example: JEE prep chal rahi hai, it's tough but manageable",
                lines=4
            )
            submit_btn = gr.Button("🔍 Analyze Stress", variant="primary")
            
            gr.Markdown("### 📋 Examples:")
            gr.Examples(
                examples=[
                    ["JEE prep achhi chal rahi hai, confident hoon"],
                    ["Thoda tension hai but manage kar lunga"],
                    ["Raat bhar roya, kuch nahi ho raha mujhse"],
                    ["Neend nahi aa rahi tension se, 2 din se khana nahi khaya"],
                    ["Syllabus complete hai, revision chal rahi hai"],
                    ["Parents ne 95% laane ko bola, bahut pressure hai"]
                ],
                inputs=text_input
            )
        
        with gr.Column():
            output = gr.Textbox(label="🧠 Analysis Result", lines=6)
    
    submit_btn.click(fn=predict, inputs=text_input, outputs=output)

print("\n" + "="*50)
print("🚀 HINGLISHMIND WEB INTERFACE")
print("="*50)
print("Local URL: http://127.0.0.1:7860")
print("Public URL: Will be shown below after launch")
print("="*50 + "\n")

demo.launch(share=True, server_port=7860)
