#!/usr/bin/env python3
"""
Export trend analysis and signal results to CSV files
"""

import os
import pg8000
import csv
from datetime import datetime
import json
import gzip

def get_db_connection():
    """Get database connection using environment variables"""
    return pg8000.connect(
        host=os.environ.get('DB_HOST'),
        database=os.environ.get('DB_NAME'),
        user=os.environ.get('DB_USERNAME'),
        password=os.environ.get('DB_PASSWORD'),
        port=int(os.environ.get('DB_PORT', 5432))
    )

def export_trends_to_csv():
    """Export trend analysis to CSV"""
    conn = get_db_connection()
    
    query = """
        SELECT 
            c.symbol,
            c.name,
            ta.timeframe,
            ta.trend_type,
            ta.confidence,
            ta.price_change_percent,
            ta.start_time,
            ta.end_time,
            ta.metadata,
            ta.created_at
        FROM trend_analysis ta
        JOIN cryptocurrencies c ON ta.crypto_id = c.id
        ORDER BY ta.created_at DESC, c.symbol
    """
    
    with conn.cursor() as cur:
        cur.execute(query)
        rows = cur.fetchall()
        
        # Get column names
        columns = ['symbol', 'name', 'timeframe', 'trend_type', 'confidence', 
                  'price_change_percent', 'start_time', 'end_time', 'metadata', 'created_at']
        
        # Write to CSV
        filename = f'trend_analysis_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(columns)
            
            for row in rows:
                # Convert metadata JSON to string
                row_data = list(row)
                if row_data[8]:  # metadata column
                    row_data[8] = json.dumps(row_data[8])
                writer.writerow(row_data)
        
        print(f"✅ Exported {len(rows)} trend records to {filename}")
        return filename

def export_signals_to_csv():
    """Export signal events to CSV"""
    conn = get_db_connection()
    
    query = """
        SELECT 
            c.symbol,
            c.name,
            se.signal_type,
            se.confidence,
            se.trigger_price,
            se.volume_spike_ratio,
            se.detected_at,
            se.metadata,
            se.created_at
        FROM signal_events se
        JOIN cryptocurrencies c ON se.crypto_id = c.id
        ORDER BY se.created_at DESC, c.symbol
    """
    
    with conn.cursor() as cur:
        cur.execute(query)
        rows = cur.fetchall()
        
        # Get column names
        columns = ['symbol', 'name', 'signal_type', 'confidence', 'trigger_price',
                  'volume_spike_ratio', 'detected_at', 'metadata', 'created_at']
        
        # Write to CSV
        filename = f'signal_events_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(columns)
            
            for row in rows:
                # Convert metadata JSON to string
                row_data = list(row)
                if row_data[7]:  # metadata column
                    row_data[7] = json.dumps(row_data[7])
                writer.writerow(row_data)
        
        print(f"✅ Exported {len(rows)} signal records to {filename}")
        return filename

def compress_files(files):
    """Compress CSV files into a single archive"""
    archive_name = f'vibecharting_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.tar.gz'
    
    import tarfile
    with tarfile.open(archive_name, 'w:gz') as tar:
        for file in files:
            tar.add(file)
    
    print(f"📦 Compressed files into {archive_name}")
    return archive_name

if __name__ == "__main__":
    print("🔄 Starting export process...")
    
    try:
        # Export data
        trend_file = export_trends_to_csv()
        signal_file = export_signals_to_csv()
        
        # Compress files
        archive = compress_files([trend_file, signal_file])
        
        print("\n✅ Export complete!")
        print(f"\nTo download the archive to your local machine, run:")
        print(f"scp -i ~/.ssh/your-key.pem ec2-user@your-ec2-ip:/home/ec2-user/{archive} ~/Downloads/")
        
    except Exception as e:
        print(f"❌ Export failed: {e}")
        import traceback
        traceback.print_exc()