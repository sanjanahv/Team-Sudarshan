import sqlite3
import datetime

class FarmerKiosk:
    def __init__(self):
        self.db_path = 'farmer_subsidy.db'
    
    def search_farmer(self, search_input):
        """Search farmer by Aadhaar or Phone or Name"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
    
        # Try Aadhaar first
        cursor.execute('SELECT * FROM farmers WHERE aadhaar = ?', (search_input,))
        farmer = cursor.fetchone()
        
        if not farmer:
            # Try phone
            cursor.execute('SELECT * FROM farmers WHERE phone = ?', (search_input,))
            farmer = cursor.fetchone()
        
        if not farmer:
            # Try name (partial match)
            cursor.execute('SELECT * FROM farmers WHERE name LIKE ?', (f'%{search_input}%',))
            farmer = cursor.fetchone()
        
        if farmer:
            # Get transactions
            cursor.execute('''
                SELECT * FROM transactions 
                WHERE farmer_aadhaar = ? 
                ORDER BY date DESC
            ''', (farmer[1],))
            
            transactions = cursor.fetchall()
            conn.close()
            
            return {
                'found': True,
                'farmer_id': farmer[0],
                'aadhaar': farmer[1],
                'name': farmer[2],
                'phone': farmer[3],
                'village': farmer[4],
                'district': farmer[5],
                'transactions': transactions
            }
        
        conn.close()
        return {'found': False, 'message': 'Farmer not found'}
    
    def generate_receipt(self, transaction_id):
        """Generate a receipt for a transaction"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT t.*, f.name, f.village, f.district 
            FROM transactions t
            JOIN farmers f ON t.farmer_aadhaar = f.aadhaar
            WHERE t.transaction_id = ?
        ''', (transaction_id,))
        
        txn = cursor.fetchone()
        conn.close()
        
        if txn:
            receipt = f"""
╔══════════════════════════════════════════════════════╗
║            🌾 SUBSIDY RECEIPT 🌾                    ║
╠══════════════════════════════════════════════════════╣
║ Farmer: {txn[7]:<40} ║
║ Village: {txn[8]}, {txn[9]:<30} ║
╠══════════════════════════════════════════════════════╣
║ Date: {txn[2]:<42} ║
║ Transaction ID: {txn[0]:<33} ║
╠══════════════════════════════════════════════════════╣
║ Fertilizer: {txn[3]:<36} ║
║ Quantity: {txn[4]} kg{'':<31} ║
║ Subsidy Amount: ₹{txn[5]:<30,.0f} ║
║ Dealer: {txn[6]:<37} ║
╠══════════════════════════════════════════════════════╣
║            ✅ VERIFIED & APPROVED                    ║
║     Government of India - Fertilizer Scheme          ║
╚══════════════════════════════════════════════════════╝
"""
            return receipt
        return None
    
