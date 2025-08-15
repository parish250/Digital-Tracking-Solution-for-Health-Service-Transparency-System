import pandas as pd
import mysql.connector
from datetime import datetime
import csv

# Database connection
def get_db_connection():
    return mysql.connector.connect(
        host='localhost',
        port=3306,
        user='admin',
        password='securePass123',
        database='digital_aid_db'
    )

def create_food_aid_items():
    """Create food aid items first to satisfy foreign key constraints"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # First, let's see what columns exist in food_aid_items table
        cursor.execute("DESCRIBE food_aid_items")
        columns = cursor.fetchall()
        print("food_aid_items table structure:")
        for col in columns:
            print(f"  {col[0]} - {col[1]}")
        
        # Check if food aid items exist
        cursor.execute("SELECT COUNT(*) FROM food_aid_items")
        count = cursor.fetchone()[0]
        
        if count == 0:
            print("Creating food aid items...")
            
            # Insert common food aid items - using only 'name' column
            food_items = [
                ("Plumpy'Nut",),
                ("Rice",),
                ("Maize Flour",),
                ("Cooking Oil",),
                ("Beans",),
                ("Salt",),
                ("Sugar",)
            ]
            
            insert_query = "INSERT INTO food_aid_items (name) VALUES (%s)"
            
            cursor.executemany(insert_query, food_items)
            conn.commit()
            print(f"Created {len(food_items)} food aid items")
        else:
            print(f"Found {count} existing food aid items")
            
    except Exception as e:
        print(f"Error creating food aid items: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

def get_or_create_food_item_id(item_type):
    """Get food item ID, create if doesn't exist"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Try to find existing item
        cursor.execute("SELECT id FROM food_aid_items WHERE name = %s", (item_type,))
        result = cursor.fetchone()
        
        if result:
            return result[0]
        else:
            # Create new item with only name
            cursor.execute(
                "INSERT INTO food_aid_items (name) VALUES (%s)",
                (item_type,)
            )
            conn.commit()
            return cursor.lastrowid
            
    except Exception as e:
        print(f"Error getting/creating food item: {e}")
        return 1  # Default fallback
    finally:
        cursor.close()
        conn.close()

def import_bulk_data(csv_file_path):
    # First, ensure food aid items exist
    create_food_aid_items()
    
    # Read the CSV file and handle missing values
    df = pd.read_csv(csv_file_path)
    
    # Fill missing values with appropriate defaults
    df = df.fillna({
        'item_type': 'Unknown',
        'quantity_kg': 0,
        'origin_warehouse': 'Unknown',
        'destination_checkpoint': 'Unknown',
        'checkpoint_type': 'Unknown',
        'checkpoint_lat': 0,
        'checkpoint_lon': 0,
        'responsible_personnel_id': 'Unknown',
        'status': 'Unknown',
        'Province': 'Unknown',
        'District': 'Unknown',
        'malnutrition_rate': 0,
        'priority_level': 'Medium',
        'beneficiary_confirmation': 'No',
        'issue_reported': 'No',
        'issue_type': 'None',
        'report_timestamp': 'No Report',
        'anonymous_report': 'No'
    })
    
    print(f"Found {len(df)} rows to import")
    print("Sample of first row:")
    print(df.iloc[0].to_dict())
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Process each row
        for index, row in df.iterrows():
            print(f"Processing row {index + 1} of {len(df)}")
            
            # Debug: Print problematic values
            if index < 3:  # Print first 3 rows for debugging
                print(f"Row {index + 1} data:")
                for col, val in row.items():
                    if pd.isna(val) or str(val) == 'nan':
                        print(f"  {col}: MISSING/NAN -> using default")
                    else:
                        print(f"  {col}: {val}")
            
            # Get or create food aid item ID
            aid_item_id = get_or_create_food_item_id(str(row['item_type']))
            
            # 1. Insert into shipments table
            shipment_query = """
            INSERT INTO shipments (aid_item_id, item_type, quantity_kg, origin_id, destination_id, status, priority_level, timestamp) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            # Convert timestamp - handle missing values
            try:
                if pd.isna(row['timestamp_scan']) or str(row['timestamp_scan']) == 'nan':
                    timestamp_scan = '2025-01-01 00:00:00'  # Default timestamp
                else:
                    timestamp_scan = pd.to_datetime(row['timestamp_scan']).strftime('%Y-%m-%d %H:%M:%S')
            except:
                timestamp_scan = '2025-01-01 00:00:00'  # Fallback timestamp
            
            # Handle quantity_kg
            try:
                quantity_kg = float(row['quantity_kg']) if not pd.isna(row['quantity_kg']) else 0.0
            except:
                quantity_kg = 0.0
            
            shipment_values = (
                aid_item_id,  # Now uses proper foreign key
                str(row['item_type']),
                quantity_kg,
                None,  # origin_id - you can map warehouse names to IDs later
                None,  # destination_id
                str(row['status']),
                str(row['priority_level']),
                timestamp_scan
            )
            
            cursor.execute(shipment_query, shipment_values)
            shipment_id = cursor.lastrowid
            
            # 2. Insert into scan_logs
            scan_query = """
            INSERT INTO scan_logs (shipment_id, destination_checkpoint, checkpoint_type, checkpoint_lat, checkpoint_lon, location, scanned_at, scanned_by, responsible_personnel_id) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            # Handle lat/lon safely
            try:
                checkpoint_lat = float(row['checkpoint_lat']) if not pd.isna(row['checkpoint_lat']) else 0.0
                checkpoint_lon = float(row['checkpoint_lon']) if not pd.isna(row['checkpoint_lon']) else 0.0
            except:
                checkpoint_lat = 0.0
                checkpoint_lon = 0.0
            
            scan_values = (
                shipment_id,
                str(row['destination_checkpoint']),
                str(row['checkpoint_type']),
                checkpoint_lat,
                checkpoint_lon,
                str(row['destination_checkpoint']),  # Using checkpoint as location
                timestamp_scan,
                f"Personnel {str(row['responsible_personnel_id'])}",
                str(row['responsible_personnel_id'])
            )
            
            cursor.execute(scan_query, scan_values)
            
            # 3. Insert into geographic_health
            geo_query = """
            INSERT INTO geographic_health (shipment_id, province, district, malnutrition_rate, beneficiary_confirmation) 
            VALUES (%s, %s, %s, %s, %s)
            """
            
            beneficiary_confirmation = 1 if str(row['beneficiary_confirmation']).lower() == 'yes' else 0
            
            # Handle malnutrition_rate safely
            try:
                malnutrition_rate = float(row['malnutrition_rate']) if not pd.isna(row['malnutrition_rate']) else 0.0
            except:
                malnutrition_rate = 0.0
            
            geo_values = (
                shipment_id,
                str(row['Province']),
                str(row['District']),
                malnutrition_rate,
                beneficiary_confirmation
            )
            
            cursor.execute(geo_query, geo_values)
            
            # 4. Insert into issues
            issue_query = """
            INSERT INTO issues (shipment_id, issue_reported, issue_type, report_timestamp, anonymous_report) 
            VALUES (%s, %s, %s, %s, %s)
            """
            
            issue_reported = 1 if str(row['issue_reported']).lower() == 'yes' else 0
            anonymous_report = 1 if str(row['anonymous_report']).lower() == 'yes' else 0
            
            # Handle report_timestamp
            report_timestamp = None
            if pd.notna(row['report_timestamp']) and str(row['report_timestamp']) != 'No Report':
                try:
                    report_timestamp = pd.to_datetime(row['report_timestamp']).strftime('%Y-%m-%d %H:%M:%S')
                except:
                    report_timestamp = None
            
            issue_values = (
                shipment_id,
                issue_reported,
                row['issue_type'] if str(row['issue_type']) != 'None' else None,
                report_timestamp,
                anonymous_report
            )
            
            cursor.execute(issue_query, issue_values)
            
            # Commit every 100 rows for better performance
            if (index + 1) % 100 == 0:
                conn.commit()
                print(f"Committed {index + 1} rows")
        
        # Final commit
        conn.commit()
        print(f"Successfully imported {len(df)} records!")
        
        # Show summary
        cursor.execute("SELECT COUNT(*) FROM shipments")
        shipment_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM scan_logs")
        scan_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM geographic_health")
        geo_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM issues")
        issue_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM food_aid_items")
        food_items_count = cursor.fetchone()[0]
        
        print("\nImport Summary:")
        print(f"Total food aid items: {food_items_count}")
        print(f"Total shipments: {shipment_count}")
        print(f"Total scan logs: {scan_count}")
        print(f"Total geographic records: {geo_count}")
        print(f"Total issue records: {issue_count}")
        
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    
    finally:
        cursor.close()
        conn.close()

# Main execution
if __name__ == "__main__":
    csv_file_path = r"C:\Users\YC\digital-aid-tracker\food_aid_tracking_dataset_cleaned.csv"
    import_bulk_data(csv_file_path)