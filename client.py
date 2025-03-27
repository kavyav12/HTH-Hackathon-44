import syft as sy
import torch
from transformers import pipeline, AutoModelForSeq2SeqLM, AutoTokenizer
import flwr as fl
import os

# Load Pre-trained Summarization Model
model_name = "facebook/bart-large-cnn"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

# Load legal document files
def load_legal_docs(folder):
    docs = []
    for file in os.listdir(folder):
        if file.endswith(".txt"):
            with open(os.path.join(folder, file), "r", encoding="utf-8") as f:
                docs.append(f.read())
    return docs

# Summarize documents locally
def summarize_documents(docs):
    summarizer = pipeline("summarization", model=model, tokenizer=tokenizer)
    return [summarizer(doc[:1024])[0]['summary_text'] for doc in docs]

# Local Training (Simulated)
class LegalClient(fl.client.NumPyClient):
    def __init__(self, model):
        self.model = model

    def get_parameters(self, config):
        return [val.cpu().numpy() for val in self.model.parameters()]

    def set_parameters(self, parameters):
        for p, new_p in zip(self.model.parameters(), parameters):
            p.data = torch.tensor(new_p)

    def fit(self, parameters, config):
        self.set_parameters(parameters)
        # Simulated Training (no fine-tuning for simplicity)
        return self.get_parameters(config), len(parameters), {}

# Connect to Server
if __name__ == "__main__":
    client = LegalClient(model)
    fl.client.start_numpy_client(server_address="127.0.0.1:8080", client=client)
