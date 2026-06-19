# Inventory Management System

A simple desktop inventory application built with Python and Tkinter for managing products, tracking stock, and viewing deleted records.

## Features
- Add new products with code, name, quantity, and price
- Automatically calculate total price from quantity × unit price
- Search products by code or name
- Delete selected products and keep a deleted history
- View summary stats for current stock and deleted records

## Requirements
- Python 3.8 or newer
- Tkinter (usually included with Python)

## How to Run
1. Open a terminal in the project folder.
2. Run:
   ```bash
   python main.py
   ```
3. The app will create an `inventory.db` database automatically on first run.

## Project Files
- `main.py` — main GUI application
- `inventory.db` — SQLite database file created at runtime

## Notes
- The app uses SQLite for local storage.
- If you want to reset the inventory data, delete the `inventory.db` file and run the program again.
