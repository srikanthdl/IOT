import pymongo
import matplotlib.dates as mdates  # Import mdates module for date formatting
import matplotlib.pyplot as plt
# Query data from MongoDB
import pandas as pd
import io
import urllib, base64
from datetime import datetime, timedelta
import matplotlib.patches as patches

import altair as alt
from bson import ObjectId  # Import ObjectId from pymongo
import seaborn as sns

# Connect to MongoDB Atlas
client = pymongo.MongoClient("mongodb+srv://kiran:Kiran0612@udaydata.13epd97.mongodb.net/?retryWrites=true&w=majority&appName=udaydata")
db = client["motionclassify"]
collection = db["anything"]
collection_gps = db['gps']



def calling_func():
    
    data = collection.find()

    # Convert data to DataFrame
    df = pd.DataFrame(data)

    # Convert "Time" column to datetime (assuming it's a string in ISO 8601 format)
    df["Time"] = pd.to_datetime(df["Time"])

    # Sort by "Time"
    df = df.sort_values(by="Time")

    # Create the plot
    plt.figure(figsize=(10, 6))

    # Plot each acceleration component with clear labels
    plt.plot(df["Time"], df["accel_x"], label="X-axis Acceleration")
    plt.plot(df["Time"], df["accel_y"], label="Y-axis Acceleration")
    plt.plot(df["Time"], df["accel_z"], label="Z-axis Acceleration")

    plt.xlabel("Time")
    plt.ylabel("Acceleration")
    plt.title("Acceleration over Time (X, Y, and Z Components)")

    # Rotate x-axis labels and format dates
    plt.xticks(rotation=45)
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M:%S'))

    plt.legend()
    plt.tight_layout()

    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plt.close()

    img_str1 = base64.b64encode(buffer.getvalue()).decode()

    return img_str1



def plot_pie_chart():
    device_statuses,active_count,total_count = get_device_statuses()
    status_counts = {'Active': list(device_statuses.values()).count('Active'), 'Inactive': list(device_statuses.values()).count('Inactive')}

        # Plot donut chart with desired colors and labels, adding border
    labels = list(status_counts.keys())
    sizes = list(status_counts.values())
    colors = ['lime', 'cyan']  # Set colors to lime for Active and cyan for Inactive
    wedgeprops = {'linewidth': 1, 'edgecolor': 'black'}  # Define border properties for wedges

    fig1, ax1 = plt.subplots()

    # Create pie chart wedges
    ax1.pie(sizes, colors=colors, labels=labels, autopct='%1.1f%%', startangle=90, wedgeprops=wedgeprops)

        # Create inner circle patch with desired color and border
    outer_circle = patches.Circle((0, 0), 0.70, facecolor='white', linewidth=1, edgecolor='black')  # Outer circle

    # Add inner circle patch to the figure
    fig = plt.gcf()
    ax1.add_patch(outer_circle)
    ax1.axis('equal')
    plt.legend(labels=labels)  # Explicitly add legend with labels
    plt.tight_layout()
    plt.show()
    
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plt.close()

    img_str2 = base64.b64encode(buffer.getvalue()).decode()

    return img_str2
 


def get_device_statuses():

    # Find the latest document for each device
    latest_docs = collection.aggregate([
        {"$sort": {"Device": 1, "Time": -1}},
        {"$group": {"_id": "$Device", "latest_doc": {"$first": "$$ROOT"}}}
    ])

    statuses = {}
    current_time = datetime.now()
    time_threshold = timedelta(minutes=5)
    
    for doc in latest_docs:
        latest_timestamp_str = doc['latest_doc']['Time']
        latest_timestamp = datetime.strptime(latest_timestamp_str, '%Y-%m-%d %H:%M:%S')
        device_status = 'Active' if current_time - latest_timestamp <= time_threshold else 'Inactive'
        device_name = doc['_id']
        statuses[device_name] = device_status

    active_count = 0
    total_count = 0
    print(type(statuses))
    for key,value in statuses.items():
        total_count +=1
        if value == 'Active':
            active_count += 1
        print(key,value)

    return statuses,active_count,total_count

def devices():
    # Query data from MongoDB
    data = collection.find()

    # Convert data to DataFrame
    df = pd.DataFrame(data)

    # Convert "Time" column to datetime
    df["Time"] = pd.to_datetime(df["Time"])

    # Get unique devices
    devicest = df["Device"].unique().tolist()

    return devicest


# def single_device_plot(device):
#     data = collection.find()
#     df = pd.DataFrame(data)
#     device_data = df[df["Device"] == device]

#     # # Create the plot
#     plt.figure(figsize=(10, 6))
#     # Plot each acceleration component with clear labels
#     plt.plot(device_data["Time"], device_data["accel_x"], label="X-axis Acceleration")
#     plt.plot(device_data["Time"], device_data["accel_y"], label="Y-axis Acceleration")
#     plt.plot(device_data["Time"], device_data["accel_z"], label="Z-axis Acceleration")
#     plt.xlabel("Time")
#     plt.ylabel("Acceleration")
#     plt.title(f"Acceleration over Time (Device: {device})")

#     plt.xticks(rotation=90)
#     # plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M:%S'))
#     plt.legend()
#     plt.tight_layout()

    
#     buffer = io.BytesIO()
#     plt.savefig(buffer, format='png')
#     buffer.seek(0)
#     plt.close()

#     img_str4 = base64.b64encode(buffer.getvalue()).decode()

   

#     return img_str4


# def temperature_and_single(device):
def single_device_plot(device):
    devices = collection.distinct("Device")
    gps_devices = collection_gps.distinct("Device")
    accel_data = collection.find({"Device": device})
    temp_data = collection.find({"Device": device}, {"temperature": 1, "Time": 1})
    # Convert data to DataFrames
    df_accel = pd.DataFrame(accel_data)
    df_temp = pd.DataFrame(temp_data)
    gps_data = collection_gps.find({"Device": device}, {"latitude": 1, "longitude": 1})
    # Convert 'Time' column to datetime
    df_accel['Time'] = pd.to_datetime(df_accel['Time'])
    df_temp['Time'] = pd.to_datetime(df_temp['Time'])
    df_gps = pd.DataFrame(gps_data)
    print(gps_data)
    # Plot acceleration components
    plt.figure(figsize=(12, 6))
    plt.plot(df_accel['Time'], df_accel['accel_x'], color='blue',label='X-axis Acceleration')
    plt.plot(df_accel['Time'], df_accel['accel_y'], color='red',label='Y-axis Acceleration')
    plt.plot(df_accel['Time'], df_accel['accel_z'], color='green',label='Z-axis Acceleration')
    plt.xlabel('Time')
    plt.ylabel('Acceleration')
    plt.title(f'Acceleration over Time for Device: {device}')
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plt.close()

    single_linechart = base64.b64encode(buffer.getvalue()).decode()

    # Plot temperature
    plt.figure(figsize=(6, 3))
    sns.lineplot(data=df_temp, x='Time', y='temperature')
    plt.xlabel('Time')
    plt.ylabel('Temperature (°C)')
    plt.title(f'Temperature over Time for Device: {device}')
    plt.xticks(rotation=45)
    plt.tight_layout()

    buffer1 = io.BytesIO()
    plt.savefig(buffer1, format='png')
    buffer1.seek(0)
    plt.close()

    temperature_chart = base64.b64encode(buffer1.getvalue()).decode()

    latt = df_gps['latitude'].iloc[-1]
    long = df_gps['longitude'].iloc[-1]
    print(latt,long)
    return single_linechart,temperature_chart,latt,long
