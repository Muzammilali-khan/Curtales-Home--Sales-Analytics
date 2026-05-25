"""
Sample Data Generator for Curtales Sales Analytics
Creates realistic-looking sample data for demonstration purposes.
Users can skip this and use their own data.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os

class SalesDataGenerator:
    """Generate realistic sales data for demonstration"""
    
    def __init__(self, output_dir='data/sample_data'):
        self.output_dir = output_dir
        self.create_output_directory()
        
    def create_output_directory(self):
        """Create directory for sample data"""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            print(f"📁 Created: {self.output_dir}")
    
    def generate_all_data(self):
        """Generate complete dataset"""
        print("🔄 Generating sample sales data...")
        
        # Generate each component
        customers = self._generate_customers()
        products = self._generate_products()
        transactions = self._generate_transactions(customers, products)
        leads = self._generate_leads()
        
        # Save to CSV
        self._save_data(customers, products, transactions, leads)
        
        # Print summary
        self._print_summary(transactions)
        
        return {
            'customers': customers,
            'products': products,
            'transactions': transactions,
            'leads': leads
        }
    
    def _generate_products(self):
        """Generate product catalog"""
        products = pd.DataFrame([
            # Curtains
            {'product_id': 'CUR001', 'product_name': 'Luxury Velvet Curtains', 'category': 'Curtains', 'price': 15000, 'cost': 8000},
            {'product_id': 'CUR002', 'product_name': 'Sheer Linen Curtains', 'category': 'Curtains', 'price': 8500, 'cost': 4500},
            {'product_id': 'CUR003', 'product_name': 'Blackout Curtains', 'category': 'Curtains', 'price': 12000, 'cost': 6500},
            # Blinds
            {'product_id': 'BLD001', 'product_name': 'Wooden Venetian Blinds', 'category': 'Blinds', 'price': 18000, 'cost': 9500},
            {'product_id': 'BLD002', 'product_name': 'Aluminum Blinds', 'category': 'Blinds', 'price': 9500, 'cost': 5000},
            {'product_id': 'BLD003', 'product_name': 'Roller Blinds', 'category': 'Blinds', 'price': 11000, 'cost': 5800},
            # Upholstery
            {'product_id': 'UPH001', 'product_name': 'Sofa Upholstery', 'category': 'Upholstery', 'price': 35000, 'cost': 18000},
            {'product_id': 'UPH002', 'product_name': 'Chair Reupholstery', 'category': 'Upholstery', 'price': 12000, 'cost': 6000},
            {'product_id': 'UPH003', 'product_name': 'Headboard Upholstery', 'category': 'Upholstery', 'price': 22000, 'cost': 11000},
            # Decor
            {'product_id': 'DEC001', 'product_name': 'Decorative Cushions', 'category': 'Decor', 'price': 4500, 'cost': 2000},
            {'product_id': 'DEC002', 'product_name': 'Wall Art', 'category': 'Decor', 'price': 3500, 'cost': 1500},
            {'product_id': 'DEC003', 'product_name': 'Luxury Vases', 'category': 'Decor', 'price': 2800, 'cost': 1200},
        ])
        return products
    
    def _generate_customers(self, num_customers=500):
        """Generate customer data"""
        segments = ['New Homeowner', 'Renovation', 'Commercial', 'Interior Designer', 'Repeat Customer']
        cities = ['Hyderabad', 'Secunderabad', 'Gachibowli', 'Hitech City', 'Banjara Hills', 'Jubilee Hills']
        
        customers = []
        for i in range(num_customers):
            segment = random.choice(segments)
            customers.append({
                'customer_id': f'CUST{i+1:04d}',
                'segment': segment,
                'city': random.choice(cities),
                'registration_date': self._random_date(datetime(2021, 1, 1), datetime(2024, 12, 31))
            })
        return pd.DataFrame(customers)
    
    def _generate_transactions(self, customers, products, num_transactions=5000):
        """Generate transaction data"""
        transactions = []
        start_date = datetime(2021, 3, 1)
        end_date = datetime(2024, 12, 31)
        
        for i in range(num_transactions):
            product = products.sample(1).iloc[0]
            customer = customers.sample(1).iloc[0]
            quantity = random.randint(1, 5)
            date = self._random_date(start_date, end_date)
            
            # Seasonality effect
            if date.month in [10, 11, 12, 1, 2, 3]:
                quantity = int(quantity * random.uniform(1.2, 1.8))
            
            amount = product['price'] * quantity
            cost = product['cost'] * quantity
            
            transactions.append({
                'invoice_id': f'INV{i+1:05d}',
                'date': date.strftime('%Y-%m-%d'),
                'product_id': product['product_id'],
                'product_name': product['product_name'],
                'category': product['category'],
                'quantity': quantity,
                'unit_price': product['price'],
                'amount': amount,
                'cost': cost,
                'profit': amount - cost,
                'customer_id': customer['customer_id'],
                'customer_segment': customer['segment'],
                'city': customer['city'],
                'status': random.choices(['Completed', 'Pending'], weights=[0.95, 0.05])[0]
            })
        
        return pd.DataFrame(transactions)
    
    def _generate_leads(self, num_leads=1000):
        """Generate lead tracking data"""
        sources = ['Instagram', 'Walk-in', 'Referral', 'Google Search', 'Facebook']
        
        leads = []
        for i in range(num_leads):
            converted = random.random() < 0.35  # 35% conversion rate
            
            leads.append({
                'lead_id': f'LEAD{i+1:05d}',
                'date': self._random_date(datetime(2023, 1, 1), datetime(2024, 12, 31)),
                'source': random.choice(sources),
                'converted': converted,
                'estimated_value': random.uniform(5000, 150000)
            })
        return pd.DataFrame(leads)
    
    def _random_date(self, start, end):
        """Generate random date between start and end"""
        return start + timedelta(days=random.randint(0, (end - start).days))
    
    def _save_data(self, customers, products, transactions, leads):
        """Save data to CSV files"""
        transactions.to_csv(f'{self.output_dir}/invoices.csv', index=False)
        customers.to_csv(f'{self.output_dir}/customers.csv', index=False)
        products.to_csv(f'{self.output_dir}/products.csv', index=False)
        leads.to_csv(f'{self.output_dir}/leads.csv', index=False)
        print(f"💾 Data saved to {self.output_dir}/")
    
    def _print_summary(self, transactions):
        """Print data summary"""
        print("\n" + "="*50)
        print("SAMPLE DATA GENERATED SUCCESSFULLY")
        print("="*50)
        print(f"📊 Total Sales: ₹{transactions['amount'].sum():,.2f}")
        print(f"📈 Total Profit: ₹{transactions['profit'].sum():,.2f}")
        print(f"💰 Avg Order Value: ₹{transactions['amount'].mean():,.2f}")
        print(f"🏆 Top Category: {transactions.groupby('category')['amount'].sum().idxmax()}")
        print(f"📅 Date Range: {transactions['date'].min()} to {transactions['date'].max()}")
        print("="*50)
        print("\n💡 Next steps:")
        print("   1. Run: python src/data_cleaner.py")
        print("   2. Then open Power BI and load the cleaned data")
        print("="*50)

if __name__ == "__main__":
    generator = SalesDataGenerator()
    generator.generate_all_data()