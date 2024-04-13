import pandas as pd
import requests
import tkinter as tk
from tkinter import filedialog

'''
1. Read CSVs
2. Calculate total crypto amount + money spent
3. Get current price
'''


def main():
    root = tk.Tk()
    root.withdraw()  # Hide the root window

    coinbase_pro_files = filedialog.askopenfilenames(title="Select coinbase pro file(s)", filetypes=(("CSV files", "*.csv"), ("All files", "*.*")))
    coinbase_file = filedialog.askopenfilename(title="Select updated coinbase file", filetypes=(("CSV files", "*.csv"), ("All files", "*.*")))
    id_to_info = {}

    for file in coinbase_pro_files:
        try:
            df = pd.read_csv(file)
            for _, row in df.iterrows():
                type = row['type']
                if type == 'deposit' or type == 'fee' or type == 'withdrawal':
                      continue
                      
                id = row['trade id']
                if id not in id_to_info:
                      id_to_info[id] = {}


                amount = row['amount']
                unit = row['amount/balance unit']
                if unit == 'USD':
                      id_to_info[id]['cost'] = -amount
                else:
                      id_to_info[id]['unit'] = unit
                      id_to_info[id]['amount'] = amount 
        except Exception as e:
            print(f'Error processing: {e}')
      
    unit_to_info = {}
    for unit, info in id_to_info.items():
         amount = info['amount']
         cost = info['cost']
         unit = info['unit']

         if unit not in unit_to_info:
              unit_to_info[unit] = { 'amount': 0, 'cost': 0 }
         
         unit_to_info[unit]['amount'] += amount
         unit_to_info[unit]['cost'] += cost

    try:
         df = pd.read_csv(coinbase_file)
         for _, row in df.iterrows():
            type = row['Transaction Type']
            unit = row['Asset']
            amount = row['Quantity Transacted']
            cost = row['Subtotal']

            if unit == 'USD':
                 continue

            if unit not in unit_to_info:
                 unit_to_info[unit] = { 'amount': 0, 'cost': 0 }
            if type == 'Staking Income':
                 unit_to_info[unit]['amount'] += amount
                 continue
            
            if type == 'Advance Trade Buy':
                 unit_to_info[unit]['amount'] += amount
                 unit_to_info[unit]['cost'] += cost

    except Exception as e:
         print(f'Error processing: {e}')
              
    for unit, info in unit_to_info.items():
         print(unit)
         print(info['cost'])
         print(info['amount'])
         # print(f'{unit} - {info['amount']} - ${info['balance']}')

if __name__ == "__main__":
    main()
