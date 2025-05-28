"""
Data Collection Script using MAVLink and LiteVNA

This script listens for MAVLink CAMERA_TRIGGER messages, captures GPS data,
and coordinates with a LiteVNA device to store sweep data.

Author: Laahiri Adusumilli
Affiliation: In collaboration with Hochschule Offenburg

Note:
- Portions of this code are based on or integrate with the LiteVNA data collection system.
- LiteVNA-specific components have been redacted from this version.

"""



import csv
from pymavlink import mavutil
from datetime import datetime

## LiteVNA code
# Constants for LiteVNA



def save_data_to_csv(filename, data, frequencies, gps_data):
    with open(filename, "w", newline='') as file:
        csvwriter = csv.writer(file)
        # Write GPS data
        csvwriter.writerow(["Timestamp", "Latitude", "Longitude", "Altitude", "Satellites", "Yaw", "Velocity"])
        csvwriter.writerow(gps_data)
        # Insert a blank line
        csvwriter.writerow([])
        # Write LiteVNA data headers
        


## End of LiteVNA code
## GPS data Collection

def collect_data(filename, master):
    # Listen for 'GPS_RAW_INT' message
    gps_msg = master.recv_match(type='GPS_RAW_INT', blocking=True, timeout=1)
    if gps_msg:
        gps_data = gps_msg.to_dict()
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        latitude = gps_data['lat']
        longitude = gps_data['lon']
        altitude = gps_data['alt']
        satellites = gps_data['satellites_visible']
        yaw = gps_data.get('yaw', None)
        velocity = gps_data.get('vel', None)
        gps_row = [timestamp, latitude, longitude, altitude, satellites, yaw, velocity]
        ## Calling back to LiteVNA data collection
        data, frequencies = main()
        save_data_to_csv(filename, data, frequencies, gps_row)


# Establish connection to MAVLink device
master = mavutil.mavlink_connection('/dev/ttyACM0')
master.wait_heartbeat()
print('Heartbeat from system (system %u component %u)' % (master.target_system, master.target_system))

# Initialize sweep counter
sweep_counter = 0

##Listening fo CAMERA_TRIGGER
try:
    while True:
        msg = master.recv_match(type='CAMERA_TRIGGER', blocking=True, timeout=1)
        if msg:
            print(f"CAMERA_TRIGGER detected at {datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}")
            sweep_counter += 1
            filename = f'sweep_{sweep_counter}.csv'
            collect_data(filename, master)

except KeyboardInterrupt:
    print("Interrupted by user")

except Exception as e:
    print(f"An error occurred: {e}")

print("Finished writing to CSV.")