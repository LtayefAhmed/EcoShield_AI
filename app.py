import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objs as go
import time
import torch
from models import LSTMForescaster, TimeSeriesAutoencoder
from data_generation import generate_synthetic_data
from simulation import prepare_attack_scenario

# Set page config
st.set_page_config(
    page_title="EcoShield AI Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for the dashboard
st.markdown("""
<style>
    .metric-card {
        background-color: #1E1E1E;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        margin-bottom: 20px;
    }
    .metric-value {
        font-size: 2.5em;
        font-weight: bold;
        color: #4CAF50; /* Green for Eco */
    }
    .metric-label {
        font-size: 1em;
        color: #BDBDBD;
        text-transform: uppercase;
    }
    .alert-card {
        background-color: #ffebee;
        border-right: 5px solid #f44336;
        padding: 15px;
        border-radius: 5px;
        color: #d32f2f;
        font-weight: bold;
        margin-top: 10px;
        margin-bottom: 10px;
    }
    .safe-card {
        background-color: #e8f5e9;
        border-right: 5px solid #4caf50;
        padding: 15px;
        border-radius: 5px;
        color: #388e3c;
        font-weight: bold;
        margin-top: 10px;
        margin-bottom: 10px;
    }
    .status-dot-green {
        height: 15px;
        width: 15px;
        background-color: #4CAF50;
        border-radius: 50%;
        display: inline-block;
        margin-right: 10px;
        box-shadow: 0 0 10px #4CAF50;
        animation: blink 2s infinite;
    }
    .status-dot-red {
        height: 15px;
        width: 15px;
        background-color: #F44336;
        border-radius: 50%;
        display: inline-block;
        margin-right: 10px;
        box-shadow: 0 0 10px #F44336;
        animation: blink 0.5s infinite;
    }
    @keyframes blink {
        50% { opacity: 0.5; }
    }
    
    /* Global Styles */
    body {
        font-family: 'Inter', sans-serif;
        background-color: #121212;
        color: #e0e0e0;
    }
</style>
""", unsafe_allow_html=True)

st.title("🛡️ EcoShield AI : La Smart City sous Haute Protection")
st.markdown("### Optimisation énergétique (Green) & Détection d'attaques FDI (Cyber)")

# --- Load Models & Parameters ---
@st.cache_resource
def load_models_and_params(device_name='cpu'):
    device = torch.device(device_name)
    
    lstm_model = LSTMForescaster(input_size=2, hidden_size=64, num_layers=2, output_size=2).to(device)
    ae_model = TimeSeriesAutoencoder(input_size=2, sequence_length=24, hidden_size=32).to(device)
    
    try:
        lstm_model.load_state_dict(torch.load("lstm_forecaster.pth", map_location=device))
        ae_model.load_state_dict(torch.load("autoencoder.pth", map_location=device))
        
        # Load scaler params
        scaler_min = np.load("scaler_min.npy")
        scaler_max = np.load("scaler_max.npy")
        
        # Load Threshold
        with open("anomaly_threshold.txt", "r") as f:
            threshold = float(f.read())
            
        return lstm_model, ae_model, scaler_min, scaler_max, threshold
        
    except FileNotFoundError:
        st.error("Model files not found. Please run 'python models.py' first.")
        st.stop()

# Utility to scale/unscale data
def scale_data(data, d_min, d_max):
    # MinMax scaling: (X - min) / (max - min)
    return (data - d_min) / (d_max - d_min)

def unscale_data(data_scaled, d_min, d_max):
    # Inverse: X_scaled * (max - min) + min
    return data_scaled * (d_max - d_min) + d_min


device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
lstm_model, ae_model, scaler_min, scaler_max, threshold = load_models_and_params(device.type)

# Setup Sidebar
st.sidebar.header("Configuration de Simulation")
speed = st.sidebar.slider("Vitesse de Simulation (ms)", 10, 500, 100)

auto_start = st.sidebar.button("Démarrer la Simulation en Temps Réel", type="primary")

# Generate fresh data for demo
if 'df' not in st.session_state:
    clean_df = generate_synthetic_data(days=14)
    attacked_df = prepare_attack_scenario(clean_df)
    st.session_state.df = attacked_df
    st.session_state.clean_df = clean_df
    st.session_state.current_index = 24  # Start after first sequence
    st.session_state.history_raw = attacked_df.iloc[:24][['energy_consumption_kw', 'water_consumption_m3']].values.tolist()
    st.session_state.history_mitigated = attacked_df.iloc[:24][['energy_consumption_kw', 'water_consumption_m3']].values.tolist()
    
    st.session_state.energy_real = list(attacked_df['energy_consumption_kw'].values[:24])
    st.session_state.energy_mitigated = list(attacked_df['energy_consumption_kw'].values[:24])
    st.session_state.energy_optimized = [(val * 0.7) for val in st.session_state.energy_mitigated] # simulate 30% savings logic
    
    st.session_state.water_real = list(attacked_df['water_consumption_m3'].values[:24])
    st.session_state.water_mitigated = list(attacked_df['water_consumption_m3'].values[:24])
    
    st.session_state.anomalies = [False] * 24
    st.session_state.timestamps = list(attacked_df.index[:24])

    st.session_state.total_real_kwh = sum(st.session_state.energy_real)
    st.session_state.total_opt_kwh = sum(st.session_state.energy_optimized)
    
    st.session_state.true_positives = 0
    st.session_state.false_positives = 0
    st.session_state.false_negatives = 0
    st.session_state.true_negatives = 24
    
    st.session_state.incident_log = []

df = st.session_state.df

# Layout
col1, col2, col3, col4 = st.columns(4)
metric_energy_save = col1.empty()
metric_threat_lvl = col2.empty()
metric_precision = col3.empty()
metric_recall = col4.empty()

alert_box = st.empty()

st.subheader("Energie : Consommation Réelle (Injectée) vs Corrigée vs Optimisée")
graph_energy = st.empty()

st.subheader("Eau : Consommation Réelle vs Corrigée")
graph_water = st.empty()

st.subheader("📝 Journal des Incidents (Temps Réel)")
log_container = st.empty()


def update_metrics(opt_savings_pct, threat_level, precision_val, recall_val):
    with metric_energy_save:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Gain Énergétique (Cible 30%)</div>
            <div class="metric-value">{opt_savings_pct:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)
        
    with metric_threat_lvl:
        color = "#f44336" if threat_level > 50 else "#ff9800" if threat_level > 20 else "#4CAF50"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Niveau de Menace Cyber</div>
            <div class="metric-value" style="color:{color}">{threat_level:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)
    
    with metric_precision:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Précision Détection</div>
            <div class="metric-value" style="color:#2196F3">{precision_val:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)
        
    with metric_recall:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Rappel Détection</div>
            <div class="metric-value" style="color:#9C27B0">{recall_val:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)

def update_graphs():
    # Energy Plotly Figure
    fig_energy = go.Figure()
    
    fig_energy.add_trace(go.Scatter(
        x=st.session_state.timestamps, 
        y=st.session_state.energy_real, 
        mode='lines', name='Données Reçues (Capteurs)',
        line=dict(color='orange', width=2, dash='dash')
    ))
    
    fig_energy.add_trace(go.Scatter(
        x=st.session_state.timestamps, 
        y=st.session_state.energy_mitigated, 
        mode='lines', name='Signal Sécurisé (EcoShield)',
        line=dict(color='#2196F3', width=3)
    ))
    
    fig_energy.add_trace(go.Scatter(
        x=st.session_state.timestamps, 
        y=st.session_state.energy_optimized, 
        mode='lines', name='Cible Optimisée (-30%)',
        line=dict(color='#4CAF50', width=2)
    ))
    
    # Highlight anomalies dynamically
    anomaly_indices = [i for i, val in enumerate(st.session_state.anomalies) if val]
    if anomaly_indices:
        anomaly_x = [st.session_state.timestamps[i] for i in anomaly_indices]
        anomaly_y = [st.session_state.energy_real[i] for i in anomaly_indices]
        fig_energy.add_trace(go.Scatter(
            x=anomaly_x, y=anomaly_y,
            mode='markers', name='FDI Détectée',
            marker=dict(color='red', size=10, symbol='x')
        ))

    fig_energy.update_layout(
        template='plotly_dark', margin=dict(l=20, r=20, t=20, b=20),
        xaxis_title="Heure", yaxis_title="Consommation kW",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    graph_energy.plotly_chart(fig_energy, use_container_width=True)
    
    # Water Plotly Figure
    fig_water = go.Figure()
    fig_water.add_trace(go.Scatter(
        x=st.session_state.timestamps, 
        y=st.session_state.water_real, 
        mode='lines', name='Données Reçues',
        line=dict(color='orange', width=2, dash='dash')
    ))
    fig_water.add_trace(go.Scatter(
        x=st.session_state.timestamps, 
        y=st.session_state.water_mitigated, 
        mode='lines', name='Signal Sécurisé',
        line=dict(color='#00BCD4', width=3)
    ))
    
    if anomaly_indices:
        anomaly_xw = [st.session_state.timestamps[i] for i in anomaly_indices]
        anomaly_yw = [st.session_state.water_real[i] for i in anomaly_indices]
        fig_water.add_trace(go.Scatter(
            x=anomaly_xw, y=anomaly_yw,
            mode='markers', name='FDI Détectée',
            marker=dict(color='red', size=10, symbol='x')
        ))
        
    fig_water.update_layout(
        template='plotly_dark', margin=dict(l=20, r=20, t=20, b=20),
        xaxis_title="Heure", yaxis_title="Consommation m3",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    graph_water.plotly_chart(fig_water, use_container_width=True)


if auto_start:
    st.sidebar.success("Simulation en cours...")
    
    # Pre-calculate base display
    update_metrics(0, 0, 100, 100)
    update_graphs()
    
    for i in range(st.session_state.current_index, len(df)):
        # 1. Get incoming row
        row = df.iloc[i]
        incoming_raw = [row['energy_consumption_kw'], row['water_consumption_m3']]
        true_attack_flag = row['is_attack_ground_truth']
        
        # 2. Get past 24 mitigated history
        history_seq = np.array(st.session_state.history_mitigated[-24:])
        
        # Scale for models
        history_scaled = scale_data(history_seq, scaler_min, scaler_max)
        incoming_scaled = scale_data(np.array(incoming_raw), scaler_min, scaler_max)
        
        # 3. Anomaly Detection (Autoencoder)
        # Create full sequence including incoming point to test reconstruction
        seq_to_test = np.vstack((history_scaled[1:], incoming_scaled)) # 24 points ending in incoming
        seq_tensor = torch.tensor(seq_to_test, dtype=torch.float32).unsqueeze(0).to(device)
        
        with torch.no_grad():
            reconstructed = ae_model(seq_tensor)
            mse_loss = torch.nn.functional.mse_loss(reconstructed, seq_tensor, reduction='none')
            # Look at error on the final point we just received
            point_error = mse_loss[0, -1, :].mean().item()
        
        is_anomaly = float(point_error) > threshold
        
        # Determine mitigated value
        if is_anomaly:
            # Predict replacement using LSTM on past history
            hist_tensor = torch.tensor(history_scaled, dtype=torch.float32).unsqueeze(0).to(device)
            with torch.no_grad():
                pred_scaled = lstm_model(hist_tensor)
                
            pred_val = unscale_data(pred_scaled.cpu().numpy()[0], scaler_min, scaler_max)
            mitigated_val = pred_val
            
            alert_box.markdown(f"""
            <div class="alert-card">
                <span class="status-dot-red"></span>
                🚨 <b>Alerte Cyber:</b> Injection de Fausse Donnée (FDI) bloquée. 
                Erreur: {point_error:.4f} > Seuil: {threshold:.4f}.<br>
                📉 Valeur remplacée par la prédiction IA (Gardienne).
            </div>
            """, unsafe_allow_html=True)
            
            # Add to incident log
            current_time = df.index[i].strftime('%Y-%m-%d %H:%M:%S')
            log_msg = f"📍 **{current_time}** | 🚨 ALERTE FDI | Erreur: `{point_error:.4f}` | Valeur corrigée par IA Guardia."
            st.session_state.incident_log.insert(0, log_msg)
            
        else:
            mitigated_val = incoming_raw
            alert_box.markdown(f"""
            <div class="safe-card">
                <span class="status-dot-green"></span>
                ✅ <b>Système Normal:</b> Flux de données intègre.
            </div>
            """, unsafe_allow_html=True)

        # 4. Metrics Update
        if is_anomaly and true_attack_flag:
            st.session_state.true_positives += 1
        elif is_anomaly and not true_attack_flag:
            st.session_state.false_positives += 1
        elif not is_anomaly and true_attack_flag:
            st.session_state.false_negatives += 1
        else:
            st.session_state.true_negatives += 1
            
        # Update session
        st.session_state.history_raw.append(incoming_raw)
        st.session_state.history_mitigated.append(mitigated_val)
        
        st.session_state.energy_real.append(incoming_raw[0])
        st.session_state.energy_mitigated.append(mitigated_val[0])
        st.session_state.energy_optimized.append(mitigated_val[0] * 0.7) # applying 30% savings logic
        
        st.session_state.water_real.append(incoming_raw[1])
        st.session_state.water_mitigated.append(mitigated_val[1])
        
        st.session_state.anomalies.append(is_anomaly)
        st.session_state.timestamps.append(df.index[i])
        
        st.session_state.current_index = i + 1
        
        # Limit display window to last 72 hours
        display_window = min(72, len(st.session_state.energy_real))
        st.session_state.energy_real = st.session_state.energy_real[-display_window:]
        st.session_state.energy_mitigated = st.session_state.energy_mitigated[-display_window:]
        st.session_state.energy_optimized = st.session_state.energy_optimized[-display_window:]
        st.session_state.water_real = st.session_state.water_real[-display_window:]
        st.session_state.water_mitigated = st.session_state.water_mitigated[-display_window:]
        st.session_state.anomalies = st.session_state.anomalies[-display_window:]
        st.session_state.timestamps = st.session_state.timestamps[-display_window:]

        # Calculating dynamic metrics
        st.session_state.total_real_kwh += incoming_raw[0]
        st.session_state.total_opt_kwh += mitigated_val[0] * 0.7
        opt_savings = ((st.session_state.total_real_kwh - st.session_state.total_opt_kwh) / st.session_state.total_real_kwh) * 100
        
        tp = st.session_state.true_positives
        fp = st.session_state.false_positives
        fn = st.session_state.false_negatives
        
        precision = (tp / (tp + fp)) * 100 if (tp + fp) > 0 else 100.0
        recall = (tp / (tp + fn)) * 100 if (tp + fn) > 0 else 100.0
        
        # Moving window attack frequency
        recent_anomalies = sum(st.session_state.anomalies[-24:]) # attacks in last 24h
        threat_level = (recent_anomalies / 24.0) * 100
        
        # Update Screen
        update_metrics(opt_savings, threat_level, precision, recall)
        update_graphs()
        
        # Display Logs (keep only last 10 for clean UI)
        if len(st.session_state.incident_log) > 10:
            st.session_state.incident_log = st.session_state.incident_log[:10]
            
        if st.session_state.incident_log:
            log_text = "<br>".join(st.session_state.incident_log)
            log_container.markdown(f"""
            <div style="background-color: #1E1E1E; padding: 15px; border-radius: 5px; height: 200px; overflow-y: auto; font-family: monospace; font-size: 0.9em; border-left: 3px solid #f44336;">
                {log_text}
            </div>
            """, unsafe_allow_html=True)
        else:
            log_container.info("Le système est sécurisé. Aucun incident détecté.")
        
        time.sleep(speed / 1000.0)

else:
    update_metrics(0, 0, 100, 100)
    update_graphs()
    alert_box.markdown(f"""
    <div class="safe-card">
        <span class="status-dot-green"></span>
        ✅ <b>Système Prêt:</b> Cliquez sur Démarrer dans la barre latérale.
    </div>
    """, unsafe_allow_html=True)
