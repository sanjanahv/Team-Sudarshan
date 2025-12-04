import sqlite3
import datetime

class FarmerKiosk:
    def __init__(self):
        self.db_path = 'farmer_subsidy.db'
    
    def search_farmer(self, search_input):
        """Search farmer by Aadhaar or Phone or Name"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
