import pandas as pd
import requests
import tkinter as tk
from tkinter import filedialog
from constants import coin_gecko_api_key

api_url = 'https://api.coingecko.com/api/v3/simple/price'

unit_code_to_api_id = {
     'ETH': 'ethereum',
     'ADA': 'cardano',
     'BTC': 'bitcoin',
     'SOL': 'solana',
     'ALGO': 'algorand',
}

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
    
    unit_to_performance_info = {}

    for unit, info in unit_to_info.items():
         coin_id = unit_code_to_api_id[unit]
         params = { 'ids': coin_id, 'vs_currencies': 'USD' }
         response = requests.get(api_url, params = params)
         if response.status_code == 200:
              data = response.json()
              cur_price = data[coin_id]['usd']
              amount = info['amount']
              total_value = amount * cur_price
              cost = info['cost']
              performance = ((total_value - cost)/cost) * 100
              unit_to_performance_info[unit] = {
                   'amount': amount,
                   'total_value': total_value,
                   'performance': performance,
                   'cost': cost
              }
         else:
            print(f'Failed to retrieved data for: {unit}')
    
    overall_cost = 0
    overall_value = 0
    for unit, performance_info in unit_to_performance_info.items():
         overall_cost += performance_info['cost']
         overall_value += performance_info['total_value']
         print(unit)
         amount_formatted = "{:.2f}".format(performance_info['amount'])
         print(f"amount: {amount_formatted}")
         total_value = "{:.2f}".format(performance_info['total_value'])
         print(f"total value: ${total_value}")
         performance = "{:.2f}".format(performance_info['performance'])
         print(f"performance: {performance}%")
    
    overall_performance = ((overall_value - overall_cost) / overall_cost) * 100
    overall_value_formatted = "{:.2f}".format(overall_value)
    overall_performance_formatted = "{:.2f}".format(overall_performance)

    print(f'Your total value is ${overall_value_formatted} and your overall performance is {overall_performance_formatted}%')

if __name__ == "__main__":
    main()
