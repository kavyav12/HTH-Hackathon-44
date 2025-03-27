import streamlit as st
import tensorflow as tf
import tensorflow_federated as tff
import pandas as pd
import numpy as np

# Streamlit UI Header
st.set_page_config(page_title="Federated Learning App", layout="wide")
st.title("Federated Learning Demo with Streamlit 🚀")

# Upload Training Data
train_file = st.file_uploader("Upload Training Data (CSV/JSON)", type=["csv", "json"])

# Load Data Function
def load_training_data(train_file):
    if train_file is not None:
        file_extension = train_file.name.split(".")[-1]
        if file_extension == "csv":
            df = pd.read_csv(train_file)
        elif file_extension == "json":
            df = pd.read_json(train_file)
        else:
            st.error("Unsupported file format. Upload CSV or JSON.")
            return None
        return df
    return None

# Convert Data to Federated Dataset
def preprocess_federated_data(data):
    """Splits dataset into multiple clients and converts to federated dataset."""
    features = data.iloc[:, :-1].values  # All columns except last one
    labels = data.iloc[:, -1].values     # Last column as label

    # Normalize features
    features = features / np.max(features, axis=0)

    dataset = tf.data.Dataset.from_tensor_slices((features, labels))
    return dataset.batch(5)

# Create a Simple Keras Model
def create_keras_model(input_shape):
    model = tf.keras.Sequential([
        tf.keras.layers.Dense(10, activation='relu', input_shape=(input_shape,)),  
        tf.keras.layers.Dense(1, activation='sigmoid')
    ])
    return model

# Federated Learning Model Wrapper
def model_fn():
    keras_model = create_keras_model(input_shape=training_df.shape[1] - 1)  # Exclude label column
    return tff.learning.models.from_keras_model(
        keras_model,
        input_spec=preprocess_federated_data(training_df).element_spec,
        loss=tf.keras.losses.BinaryCrossentropy(),
        metrics=[tf.keras.metrics.BinaryAccuracy()]
    )

# Federated Learning Training Process
def train_federated_model(federated_train_data):
    iterative_process = tff.learning.algorithms.build_weighted_fed_avg(model_fn)
    state = iterative_process.initialize()

    for round_num in range(5):  # Train for 5 rounds
        state, metrics = iterative_process.next(state, federated_train_data)
        st.write(f"Round {round_num}, Metrics: {metrics}")

# Process Uploaded Data
if train_file:
    training_df = load_training_data(train_file)
    
    if training_df is not None:
        st.success("Training data loaded successfully!")

        # Split Data for Simulated Clients
        num_clients = 3  # Simulating 3 clients
        client_data = np.array_split(training_df, num_clients)
        federated_train_data = [preprocess_federated_data(client) for client in client_data]

        if st.button("Train Federated Model"):
            with st.spinner("Training Federated Model..."):
                train_federated_model(federated_train_data)
            st.success("Federated training completed! 🎉")
