"""
Universal Data Cleaner for Sales Analytics
Works with ANY sales data - just map your columns!
"""

import pandas as pd
import os
import sys

class SalesDataCleaner:
    """
    Universal ETL pipeline for sales data
    
    How to use with YOUR data:
    1. Put your CSV/Excel file in 'data/your_data/'
    2. Create a column mapping (see example below)
    3. Run this script
    """
    
    def __init__(self, input_dir='data', output_dir='data/cleaned_data'):
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.create_output_directory()
    
    def create_output_directory(self):
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def detect_input_file(self):
        """Auto-detect what data source to use"""
        # Check for user's data first
        user_data_path = f'{self.input_dir}/your_data'
        sample_data_path = f'{self.input_dir}/sample_data'
        
        if os.path.exists(user_data_path) and any(f.endswith(('.csv', '.xlsx')) for f in os.listdir(user_data_path)):
            return user_data_path, "YOUR_DATA"
        elif os.path.exists(sample_data_path):
            return sample_data_path, "SAMPLE_DATA"
        else:
            return None, None
    
    def load_data(self, file_path):
        """Load data from CSV or Excel"""
        if file_path.endswith('.csv'):
            return pd.read_csv(file_path)
        elif file_path.endswith(('.xlsx', '.xls')):
            return pd.read_excel(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_path}")
    
    def clean_sales_data(self, df, column_mapping=None):
        """Clean transaction/invoice data (has dates)"""
        
        # Step 1: Apply column mapping if provided
        if column_mapping:
            df = df.rename(columns=column_mapping)
            print("✅ Applied column mapping")
        
        # Step 2: Check for required columns
        if 'date' not in df.columns:
            print(f"⚠️ This file doesn't have a 'date' column. Skipping time-based cleaning.")
            print(f"   Available columns: {list(df.columns)[:5]}...")
            return df
        
        # Step 3: Convert date to datetime
        df['date'] = pd.to_datetime(df['date'])
        
        # Step 4: Remove invalid data (only for sales data)
        if 'amount' in df.columns:
            initial_count = len(df)
            df = df.dropna(subset=['date', 'amount'])
            df = df[df['amount'] > 0]
            print(f"🧹 Removed {initial_count - len(df)} invalid rows")
        
        # Step 5: Add time dimensions
        df['year'] = df['date'].dt.year
        df['month'] = df['date'].dt.strftime('%B')
        df['month_num'] = df['date'].dt.month
        df['quarter'] = df['date'].dt.quarter
        df['weekday'] = df['date'].dt.day_name()
        
        # Step 6: Calculate derived metrics
        if 'quantity' in df.columns and 'unit_price' in df.columns:
            df['calculated_amount'] = df['quantity'] * df['unit_price']
        
        if 'cost' in df.columns and 'amount' in df.columns:
            df['profit'] = df['amount'] - df['cost']
            df['margin'] = (df['profit'] / df['amount']) * 100
        
        print(f"✅ Cleaned data: {len(df)} rows")
        
        return df
    
    def generate_aggregations(self, sales_df):
        """Create aggregated views for dashboard (only for sales data)"""
        
        # Check if this is sales data (has date column)
        if 'date' not in sales_df.columns:
            print("⚠️ No date column found - skipping aggregations")
            return
        
        # Monthly sales
        monthly = sales_df.groupby(['year', 'month', 'month_num']).agg({
            'amount': 'sum',
            'invoice_id': 'count' if 'invoice_id' in sales_df.columns else 'amount'
        }).rename(columns={'invoice_id': 'order_count' if 'invoice_id' in sales_df.columns else 'transaction_count'})
        monthly = monthly.sort_values(['year', 'month_num'])
        monthly.to_csv(f'{self.output_dir}/monthly_sales.csv')
        print(f"✅ Created monthly_sales.csv")
        
        # Category performance (if category exists)
        if 'category' in sales_df.columns:
            category = sales_df.groupby('category').agg({
                'amount': 'sum',
                'profit': 'sum' if 'profit' in sales_df.columns else 'amount'
            }).sort_values('amount', ascending=False)
            category.to_csv(f'{self.output_dir}/category_performance.csv')
            print(f"✅ Created category_performance.csv")
        
        # City performance (if city exists)
        if 'city' in sales_df.columns:
            city = sales_df.groupby('city').agg({
                'amount': 'sum'
            }).sort_values('amount', ascending=False)
            city.to_csv(f'{self.output_dir}/city_performance.csv')
            print(f"✅ Created city_performance.csv")
        
        # Product performance (if product_name exists)
        if 'product_name' in sales_df.columns:
            products = sales_df.groupby('product_name').agg({
                'amount': 'sum',
                'quantity': 'sum' if 'quantity' in sales_df.columns else 'amount'
            }).sort_values('amount', ascending=False).head(10)
            products.to_csv(f'{self.output_dir}/top_products.csv')
            print(f"✅ Created top_products.csv")
    
    def run(self, column_mapping=None):
        """Run the complete cleaning pipeline"""
        
        print("\n" + "="*60)
        print("SALES DATA CLEANING PIPELINE")
        print("="*60)
        
        # Detect data source
        data_path, data_type = self.detect_input_file()
        
        if not data_path:
            print("\n❌ No data found!")
            print("\nOptions:")
            print("   1. Generate sample data: python src/data_generator.py")
            print("   2. Or put your data in 'data/your_data/' folder")
            return None
        
        print(f"\n📂 Data source: {data_type}")
        print(f"📍 Path: {data_path}")
        
        # Find ALL CSV/Excel files
        files = [f for f in os.listdir(data_path) if f.endswith(('.csv', '.xlsx'))]
        if not files:
            print("❌ No CSV/Excel files found")
            return None
        
        print(f"\n📄 Found {len(files)} files: {', '.join(files)}")
        
        # Process each file
        all_data = {}
        sales_df = None
        
        for file in files:
            file_path = os.path.join(data_path, file)
            print(f"\n📄 Processing: {file}")
            
            # Load data
            df = self.load_data(file_path)
            print(f"   Loaded {len(df)} rows")
            
            # Determine file type and clean accordingly
            if 'invoice_id' in df.columns or 'amount' in df.columns:
                # This is likely sales/transaction data
                print("   📊 Identified as SALES data")
                sales_df = self.clean_sales_data(df, column_mapping)
                if sales_df is not None:
                    # Save cleaned sales data
                    sales_df.to_csv(f'{self.output_dir}/cleaned_sales_data.csv', index=False)
                    print(f"   💾 Saved to: cleaned_sales_data.csv")
            elif 'customer_id' in df.columns:
                # This is customer data - just copy as-is
                print("   👥 Identified as CUSTOMER data")
                df.to_csv(f'{self.output_dir}/customers.csv', index=False)
                print(f"   💾 Saved to: customers.csv")
            elif 'product_id' in df.columns:
                # This is product data - just copy as-is
                print("   📦 Identified as PRODUCT data")
                df.to_csv(f'{self.output_dir}/products.csv', index=False)
                print(f"   💾 Saved to: products.csv")
            elif 'lead_id' in df.columns:
                # This is lead data - just copy as-is
                print("   🎯 Identified as LEAD data")
                df.to_csv(f'{self.output_dir}/leads.csv', index=False)
                print(f"   💾 Saved to: leads.csv")
            else:
                # Unknown file - save as is with warning
                print("   ⚠️ Unknown file type - saving as-is")
                base_name = os.path.splitext(file)[0]
                df.to_csv(f'{self.output_dir}/{base_name}_cleaned.csv', index=False)
        
        # Generate aggregations from sales data
        if sales_df is not None:
            print("\n📊 Generating aggregated reports...")
            self.generate_aggregations(sales_df)
        
        print("\n" + "="*60)
        print("✅ PIPELINE COMPLETE!")
        print("="*60)
        print(f"\n📁 All cleaned data saved to: {self.output_dir}/")
        print("\n📋 Files created:")
        for f in os.listdir(self.output_dir):
            print(f"   - {f}")
        print("\n🎯 Next: Import these files into Power BI")
        print("="*60)
        
        return sales_df

# ============================================
# EXAMPLE: HOW TO USE WITH YOUR OWN DATA
# ============================================

if __name__ == "__main__":
    
    # CREATE A COLUMN MAPPING FOR YOUR DATA
    # ======================================
    # Uncomment and modify this section for YOUR data
    
    column_mapping = {
        # 'Your Column Name': 'Standard Name'
        # 'Invoice Date': 'date',
        # 'Total Amount': 'amount', 
        # 'Product Category': 'category',
        # 'Customer City': 'city',
        # 'Quantity': 'quantity',
        # 'Unit Price': 'unit_price',
        # 'Customer Segment': 'customer_segment',
    }
    
    # Run the cleaner
    cleaner = SalesDataCleaner()
    
    # For sample data (no mapping needed):
    cleaner.run()
    
    # For your own data, pass the column mapping:
    # cleaner.run(column_mapping=column_mapping)
