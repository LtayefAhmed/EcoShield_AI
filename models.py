import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import os

# --- Dataset Preparation ---

class TimeSeriesDataset(Dataset):
    def __init__(self, data, seq_length):
        self.data = data
        self.seq_length = seq_length

    def __len__(self):
        return len(self.data) - self.seq_length

    def __getitem__(self, index):
        x = self.data[index:index+self.seq_length]
        y = self.data[index+self.seq_length]
        return torch.tensor(x, dtype=torch.float32), torch.tensor(y, dtype=torch.float32)

class AutoencoderDataset(Dataset):
    def __init__(self, data, seq_length):
        self.data = data
        self.seq_length = seq_length

    def __len__(self):
        return len(self.data) - self.seq_length + 1

    def __getitem__(self, index):
        x = self.data[index:index+self.seq_length]
        return torch.tensor(x, dtype=torch.float32), torch.tensor(x, dtype=torch.float32)

def prepare_dataloaders(df, sequence_length=24, batch_size=32):
    """
    Prepares DataLoaders for LSTM (forecasting) and Autoencoder (anomaly detection).
    Assumes df has 'energy_consumption_kw' and 'water_consumption_m3'.
    """
    # Use both features for the model
    features = ['energy_consumption_kw', 'water_consumption_m3']
    data = df[features].values
    
    # Scale data
    scaler = MinMaxScaler()
    scaled_data = scaler.fit_transform(data)
    
    # Split into train and validation (80/20)
    train_size = int(len(scaled_data) * 0.8)
    train_data = scaled_data[:train_size]
    val_data = scaled_data[train_size:]
    
    # Create datasets
    train_lstm_dataset = TimeSeriesDataset(train_data, sequence_length)
    val_lstm_dataset = TimeSeriesDataset(val_data, sequence_length)
    
    train_ae_dataset = AutoencoderDataset(train_data, sequence_length)
    val_ae_dataset = AutoencoderDataset(val_data, sequence_length)
    
    # Create dataloaders
    train_lstm_loader = DataLoader(train_lstm_dataset, batch_size=batch_size, shuffle=True)
    val_lstm_loader = DataLoader(val_lstm_dataset, batch_size=batch_size, shuffle=False)
    
    train_ae_loader = DataLoader(train_ae_dataset, batch_size=batch_size, shuffle=True)
    val_ae_loader = DataLoader(val_ae_dataset, batch_size=batch_size, shuffle=False)
    
    return train_lstm_loader, val_lstm_loader, train_ae_loader, val_ae_loader, scaler

# --- LSTM Forecaster Model ---

class LSTMForescaster(nn.Module):
    def __init__(self, input_size=2, hidden_size=64, num_layers=2, output_size=2):
        super(LSTMForescaster, self).__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True, dropout=0.2)
        self.fc = nn.Linear(hidden_size, output_size)
        
    def forward(self, x):
        h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)
        c0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)
        
        out, _ = self.lstm(x, (h0, c0))
        # We only want the output of the last time step
        out = self.fc(out[:, -1, :])
        return out

# --- Autoencoder Anomaly Detector ---

class TimeSeriesAutoencoder(nn.Module):
    def __init__(self, input_size=2, sequence_length=24, hidden_size=32):
        super(TimeSeriesAutoencoder, self).__init__()
        self.sequence_length = sequence_length
        self.input_size = input_size
        self.hidden_size = hidden_size
        
        # Encoder
        self.encoder = nn.LSTM(input_size, hidden_size, batch_first=True)
        
        # Decoder
        self.decoder = nn.LSTM(hidden_size, input_size, batch_first=True)
        
    def forward(self, x):
        # Encode
        _, (hidden, _) = self.encoder(x)
        # Hidden state from last layer is (1, batch_size, hidden_size)
        
        # Repeat hidden state for sequence_length
        # hidden.squeeze(0) -> (batch_size, hidden_size)
        hidden = hidden.squeeze(0).unsqueeze(1).repeat(1, self.sequence_length, 1)
        # hidden -> (batch_size, seq_length, hidden_size)
        
        # Decode
        decoded, _ = self.decoder(hidden)
        # decoded -> (batch_size, seq_length, input_size)
        
        return decoded

# --- Training Functions ---

def train_model(model, train_loader, val_loader, num_epochs=20, learning_rate=0.001, model_path="model.pth"):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)
    
    best_val_loss = float('inf')
    
    for epoch in range(num_epochs):
        model.train()
        train_loss = 0.0
        for x_batch, y_batch in train_loader:
            x_batch, y_batch = x_batch.to(device), y_batch.to(device)
            
            optimizer.zero_grad()
            outputs = model(x_batch)
            loss = criterion(outputs, y_batch)
            loss.backward()
            optimizer.step()
            
            train_loss += loss.item()
            
        model.eval()
        val_loss = 0.0
        with torch.no_grad():
            for x_batch, y_batch in val_loader:
                x_batch, y_batch = x_batch.to(device), y_batch.to(device)
                outputs = model(x_batch)
                loss = criterion(outputs, y_batch)
                val_loss += loss.item()
                
        train_loss /= len(train_loader)
        val_loss /= len(val_loader)
        
        print(f"Epoch [{epoch+1}/{num_epochs}], Train Loss: {train_loss:.6f}, Val Loss: {val_loss:.6f}")
        
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            torch.save(model.state_dict(), model_path)
            print(f"  -> Saved best model ({best_val_loss:.6f})")
            
    return model

def calculate_anomaly_threshold(autoencoder, train_loader, percentile=99.0):
    """
    Calculates the dynamic threshold for anomaly detection based on reconstruction error
    of normal training data.
    """
    device = next(autoencoder.parameters()).device
    autoencoder.eval()
    errors = []
    
    criterion = nn.MSELoss(reduction='none')
    
    with torch.no_grad():
        for x_batch, _ in train_loader:
            x_batch = x_batch.to(device)
            reconstructed = autoencoder(x_batch)
            
            # Calculate mean squared error per sequence
            batch_errors = criterion(reconstructed, x_batch).mean(dim=(1, 2)).cpu().numpy()
            errors.extend(batch_errors)
            
    threshold = np.percentile(errors, percentile)
    return threshold

if __name__ == "__main__":
    from data_generation import generate_synthetic_data
    
    print("Generating data for training...")
    df = generate_synthetic_data(days=60)
    
    sequence_length = 24 # 24 hours of history
    print(f"Preparing data loaders with sequence length {sequence_length}...")
    train_lstm, val_lstm, train_ae, val_ae, scaler = prepare_dataloaders(df, sequence_length)
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")
    
    # Train LSTM
    print("\n--- Training LSTM Forecaster ---")
    lstm_model = LSTMForescaster(input_size=2, hidden_size=64, num_layers=2, output_size=2)
    train_model(lstm_model, train_lstm, val_lstm, num_epochs=15, model_path="lstm_forecaster.pth")
    
    # Train Autoencoder
    print("\n--- Training Autoencoder Anomaly Detector ---")
    ae_model = TimeSeriesAutoencoder(input_size=2, sequence_length=sequence_length, hidden_size=32)
    train_model(ae_model, train_ae, val_ae, num_epochs=15, model_path="autoencoder.pth")
    
    # Calculate threshold
    ae_model.load_state_dict(torch.load("autoencoder.pth", map_location=device))
    ae_model.to(device)
    threshold = calculate_anomaly_threshold(ae_model, train_ae)
    print(f"\nCalculated Anomaly Threshold (99th percentile): {threshold:.6f}")
    
    # Save the threshold and scaler parameters
    np.save("scaler_min.npy", scaler.data_min_)
    np.save("scaler_max.npy", scaler.data_max_)
    with open("anomaly_threshold.txt", "w") as f:
        f.write(str(threshold))
        
    print("Training complete. Models and parameters saved.")
