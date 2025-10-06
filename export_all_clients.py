#!/usr/bin/env python3
"""
Export ALL client configurations from multiple locations
to a backup file that can be imported into the Streamlit Cloud app.
"""

import json
import os
from datetime import datetime
from pathlib import Path

# Multiple possible client directories
CLIENT_DIRS = [
    Path(__file__).parent / 'clients',
    Path.home() / 'Documents' / 'Python Projects' / 'Dashboard' / 'clients',
    Path.home() / 'Documents' / 'Python Projects' / 'Campaign Creator' / 'clients',
    Path.home() / 'Documents' / 'AmazonDashboard' / 'clients',
    Path.home() / 'Library' / 'Application Support' / 'AmazonDashboard' / 'clients',
    Path.home() / 'Documents' / 'Analysis' / 'QBR Help' / 'clients',
]

def export_all_clients():
    """Export all client configurations from all known locations."""
    
    export_data = {
        'version': '1.0',
        'export_date': datetime.now().isoformat(),
        'clients': {}
    }
    
    all_clients = {}
    locations_found = []
    
    print("🔍 Searching for client files in multiple locations...\n")
    
    for client_dir in CLIENT_DIRS:
        if not client_dir.exists():
            continue
            
        client_files = list(client_dir.glob('*.json'))
        
        if client_files:
            print(f"📁 Found {len(client_files)} client(s) in: {client_dir}")
            locations_found.append(str(client_dir))
            
            for client_file in client_files:
                client_name = client_file.stem  # filename without .json extension
                
                try:
                    with open(client_file, 'r', encoding='utf-8') as f:
                        client_config = json.load(f)
                        
                        # Check if we already have this client
                        if client_name in all_clients:
                            # Compare modification times, keep the newer one
                            existing_mtime = all_clients[client_name]['mtime']
                            current_mtime = client_file.stat().st_mtime
                            
                            if current_mtime > existing_mtime:
                                print(f"  ✓ {client_name} (newer version)")
                                all_clients[client_name] = {
                                    'config': client_config,
                                    'mtime': current_mtime,
                                    'path': str(client_file)
                                }
                            else:
                                print(f"  - {client_name} (skipped, older version)")
                        else:
                            print(f"  ✓ {client_name}")
                            all_clients[client_name] = {
                                'config': client_config,
                                'mtime': client_file.stat().st_mtime,
                                'path': str(client_file)
                            }
                            
                except Exception as e:
                    print(f"  ⚠️  Warning: Could not read {client_name}: {e}")
            
            print()  # blank line
    
    if not all_clients:
        print("❌ No client files found in any location!")
        return
    
    # Add configs to export data
    for client_name, data in all_clients.items():
        export_data['clients'][client_name] = data['config']
    
    # Create output filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = Path(__file__).parent / f'amazon_dashboard_ALL_clients_{timestamp}.json'
    
    # Write export file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, indent=2)
    
    print("=" * 70)
    print(f"✅ Successfully exported {len(export_data['clients'])} unique client(s):")
    print()
    for client_name in sorted(export_data['clients'].keys()):
        print(f"  • {client_name}")
    print()
    print(f"📁 Backup file created: {output_file.name}")
    print(f"📊 File size: {output_file.stat().st_size / 1024 / 1024:.2f} MB")
    print()
    print("=" * 70)
    print(f"\n📋 Next steps:")
    print(f"1. Open your deployed Streamlit app in your browser")
    print(f"2. Select 'Import Client Data' from the Action menu")
    print(f"3. Upload this file: {output_file.name}")
    print(f"4. Choose 'Merge' or 'Replace' mode")
    print(f"5. Click 'Import Clients'")
    print(f"\n💡 Note: The data will be stored in YOUR browser's localStorage only.")
    print(f"   Other users won't see your clients unless they import this file too.")

if __name__ == '__main__':
    export_all_clients()
