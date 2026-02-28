import numpy as np
import pandas as pd

class AttackSimulator:
    def __init__(self):
        pass

    def inject_spike_attack(self, data, indices, feature='energy_consumption_kw', multiplier=3.0):
        """
        Injects a sudden high spike into the chosen feature at specific indices.
        """
        attacked_data = data.copy()
        for idx in indices:
            if idx < len(attacked_data):
                attacked_data.at[attacked_data.index[idx], feature] *= multiplier
        return attacked_data

    def inject_stealth_attack(self, data, start_idx, duration, feature='water_consumption_m3', increment=0.05):
        """
        Gradually increases the consumption values over time to evade simple threshold detection.
        """
        attacked_data = data.copy()
        for i in range(duration):
            idx = start_idx + i
            if idx < len(attacked_data):
                # Gradual increase: base + 5%, + 10%, + 15%...
                multiplier = 1.0 + (increment * (i + 1))
                attacked_data.at[attacked_data.index[idx], feature] *= multiplier
        return attacked_data

    def inject_targeted_outage(self, data, start_idx, duration, feature='energy_consumption_kw'):
        """
        Simulates a targeted blackout (values drop to near 0).
        """
        attacked_data = data.copy()
        for i in range(duration):
            idx = start_idx + i
            if idx < len(attacked_data):
                # Injects a value very close to 0 to simulate outage or sensor drop
                attacked_data.at[attacked_data.index[idx], feature] = np.random.uniform(0, 5)
        return attacked_data

def prepare_attack_scenario(df):
    """
    Takes a clean dataset and injects various real-world FDI scenarios 
    Returns the compromised dataset and a boolean mask of truth.
    """
    simulator = AttackSimulator()
    attacked_df = df.copy()
    
    # Truth array to know exactly which points are attacked
    # False = Normal, True = Attacked
    is_attacked = np.zeros(len(df), dtype=bool)
    
    # 1. Spike Attack (Energy) at index 100, 101, 150
    spike_indices = [100, 101, 150]
    attacked_df = simulator.inject_spike_attack(attacked_df, spike_indices, 'energy_consumption_kw')
    is_attacked[spike_indices] = True
    
    # 2. Stealth Attack (Water) starting at index 300 for 48 hours
    stealth_start = 300
    stealth_duration = 48
    attacked_df = simulator.inject_stealth_attack(attacked_df, stealth_start, stealth_duration, 'water_consumption_m3')
    is_attacked[stealth_start : stealth_start + stealth_duration] = True
    
    # 3. Targeted Outage (Energy) starting at index 500 for 5 hours
    outage_start = 500
    outage_duration = 5
    attacked_df = simulator.inject_targeted_outage(attacked_df, outage_start, outage_duration, 'energy_consumption_kw')
    is_attacked[outage_start : outage_start + outage_duration] = True
    
    attacked_df['is_attack_ground_truth'] = is_attacked
    
    return attacked_df

if __name__ == "__main__":
    from data_generation import generate_synthetic_data
    df = generate_synthetic_data(days=30)
    attacked_df = prepare_attack_scenario(df)
    
    print(f"Total points: {len(attacked_df)}")
    print(f"Attacked points: {attacked_df['is_attack_ground_truth'].sum()}")
    
    attacked_df.to_csv("attacked_sensor_data.csv")
    print("Saved attacked scenario to attacked_sensor_data.csv")
