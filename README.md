
# PC Inventory Management

This Python script allows you to manage PC inventory by loading data from CSV files into an SQLite database and providing a GUI interface to view the last 10 entries and search by serial number, memory serial, and board serial. Forked from https://github.com/foskasse/pc_inventory 

## Prerequisites

- Python 3.x
- SQLite

## Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/AlexMDuarte/pc_inventory.git
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. If needed create an SQLite database:

   ```bash
   python CreateDatabase.py
   ```

## Usage

1. Load PC inventory data from a CSV file to the CSVToBeProcessed Folder (you can run it manually or crontab):

   ```bash
   python ETLDatabase.py.py
   ```

2. Run the GUI application:

   ```bash
   python Interface.py
   ```

3. Run the Web Interface (http://127.0.0.1:5000/):

   ```bash
   python Web.py
   ```
## File Structure and CLI APPS

- `ShowDatabase.py`: Shows  `pc_inventory` table.
- `SearchDatabase.py`: Search Database.
- `EditEntity.py`: Edit Database via CLI.
- `DeleteDatabase.py`: Delete Database
- `CreateDatabase.py`: Create Database
- `ETLDatabase.py`: Transform the CSV's on the folder CSVToBeProcessed into the database and move to the CSVProcessed

## Additional Notes

- The database file (`computers.db`) will be created in the project directory.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.
```
