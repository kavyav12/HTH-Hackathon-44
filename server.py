import flwr as fl
import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

# Load Global Model
model_name = "facebook/bart-large-cnn"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

# FedAvg Aggregation Strategy
def get_strategy():
    return fl.server.strategy.FedAvg()

# Start Federated Server
if __name__ == "__main__":
    fl.server.start_server(server_address="127.0.0.1:8080", strategy=get_strategy())
