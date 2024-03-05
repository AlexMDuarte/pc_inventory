import sqlite3
import csv
import os
import shutil
import logging
from datetime import datetime
import random

# Set up logging
log_folder = "Logs"
if not os.path.exists(log_folder):
    os.makedirs(log_folder)

log_filename = os.path.join(log_folder, f"log_{datetime.now().strftime('%Y-%m-%d')}.txt")
logging.basicConfig(filename=log_filename, level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')

# Function to create SQLite table
def create_table():
    conn = sqlite3.connect("computers.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS computers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            computer_id TEXT,
            component TEXT,
            serial_number TEXT,
            date_added TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Function to create the SQLite database
def create_database():
    conn = sqlite3.connect("computers.db")
    conn.close()
    
unique_ids = set()

# Function to generate a random computer ID
def generate_computer_id():
    while True:
        id = random.randint(100000, 999999)
        if id not in unique_ids:
            unique_ids.add(id)
            return id
        return str(unique_id = generate_computer_id())

# Function to insert data into SQLite database
def insert_data(computer_id, component, serial_number):
    conn = sqlite3.connect("computers.db")
    cursor = conn.cursor()
    date_added = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute('''
        INSERT INTO computers (computer_id, component, serial_number, date_added)
        VALUES (?, ?, ?, ?)
    ''', (computer_id, component, serial_number, date_added))
    conn.commit()
    conn.close()
    logging.info(f"Inserted data into database: Computer ID: {computer_id}, Component: {component}, Serial Number: {serial_number}")

# Function to process a CSV file
def process_csv_file(file_path):
    computer_id = generate_computer_id()
    with open(file_path, 'r') as csvfile:
        csv_reader = csv.DictReader(csvfile)
        for row in csv_reader:
            component = row['Component']
            serial_number = row['SerialNumber']
            insert_data(computer_id, component, serial_number)
    return computer_id

# Function to move the processed CSV file
def move_processed_file(file_path, computer_id):
    processed_folder = "CSVProcessed"
    if not os.path.exists(processed_folder):
        os.makedirs(processed_folder)
    now = datetime.now().strftime("%Y-%m-%d")
    new_file_name = f"{computer_id}-Processed_{now}.csv"
    new_file_path = os.path.join(processed_folder, new_file_name)
    shutil.move(file_path, new_file_path)

# Main function to process CSV files in the "CSVToBeProcessed" folder
def main():
    create_database()
    create_table()

    input_folder = "CSVToBeProcessed"
    for filename in os.listdir(input_folder):
        if filename.endswith(".csv"):
            file_path = os.path.join(input_folder, filename)
            try:
                computer_id = process_csv_file(file_path)
                move_processed_file(file_path, computer_id)
                logging.info(f"Processed and moved {filename}.")
            except Exception as e:
                logging.error(f"Error processing {filename}: {str(e)}")

if __name__ == "__main__":
    main()
