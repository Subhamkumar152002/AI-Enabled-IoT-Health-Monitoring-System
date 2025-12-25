import numpy as np

# Threshold values for fall detection (adjust as needed)
ACCELERATION_THRESHOLD = 2.5  # Sudden acceleration change (g-force)
IMPACT_THRESHOLD = 1.5        # High impact force
INACTIVITY_THRESHOLD = 0.3    # Low movement after fall

def detect_fall(accel_data):
    """
    Detects a fall based on accelerometer data.

    Args:
        accel_data (list): [accel_x, accel_y, accel_z] in g-force.

    Returns:
        bool: True if a fall is detected, False otherwise.
    """
    try:
        accel_x, accel_y, accel_z = accel_data
        total_accel = np.sqrt(accel_x**2 + accel_y**2 + accel_z**2)

        # Check for sudden acceleration change (possible free-fall)
        if total_accel < INACTIVITY_THRESHOLD:
            print("Possible free-fall detected!")

        # Check for impact force (hitting the ground)
        elif total_accel > IMPACT_THRESHOLD:
            print("High impact detected!")

        # If both conditions are met, it's likely a fall
        if total_accel > ACCELERATION_THRESHOLD:
            print("⚠️ Fall detected!")
            return True

        return False

    except Exception as e:
        print(f"Error in fall detection: {e}")
        return False
