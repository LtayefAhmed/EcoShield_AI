import pandas as pd
import numpy as np

def generate_synthetic_data(days=30):
    """
    Generates a synthetic IoT time-series dataset for energy and water consumption.
    Includes hourly patterns, peak demand periods, and seasonal variations.
    """
    # Create time index
    timestamps = pd.date_range(start="2023-01-01", periods=days*24, freq="H")
    
    # Base consumption
    base_energy = 500  # kW
    base_water = 100   # m3
    
    # Hourly multipliers (peak hours around 8-10 AM and 6-9 PM)
    hourly_pattern = np.array([
        0.6, 0.5, 0.5, 0.5, 0.6, 0.8, 1.2, 1.5, 1.8, 1.6, 1.4, 1.3,
        1.3, 1.3, 1.4, 1.5, 1.7, 1.9, 2.0, 1.9, 1.6, 1.3, 0.9, 0.7
    ])
    
    # Repeat hourly pattern for all days
    repeated_pattern = np.tile(hourly_pattern, days)
    
    # Add noise
    energy_noise = np.random.normal(0, 0.1, len(timestamps))
    water_noise = np.random.normal(0, 0.1, len(timestamps))
    
    # Seasonal variation (simplified, assuming start of year is winter)
    seasonal_variation = np.sin(np.linspace(0, 2 * np.pi, len(timestamps))) * 0.2 + 1.0
    
    # Calculate consumption
    energy_consumption = base_energy * repeated_pattern * seasonal_variation * (1 + energy_noise)
    water_consumption = base_water * repeated_pattern * seasonal_variation * (1 + water_noise)
    
    # Ensure no negative values
    energy_consumption = np.maximum(energy_consumption, 0)
    water_consumption = np.maximum(water_consumption, 0)
    
    df = pd.DataFrame({
        "timestamp": timestamps,
        "energy_consumption_kw": energy_consumption,
        "water_consumption_m3": water_consumption
    })
    
    df.set_index("timestamp", inplace=True)
    return df

if __name__ == "__main__":
    df = generate_synthetic_data(days=60)
    df.to_csv("sensor_data.csv")
    print("Synthetic dataset generated and saved to sensor_data.csv")
    print(df.head())
    print(f"Total records: {len(df)}")
