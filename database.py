import sqlite3
import pandas as pd
import json
import hashlib
import os
import pickle
import gzip
from datetime import datetime
from typing import Dict, Any, Optional, List
import streamlit as st

class DatabaseManager:
    """Manages SQLite database operations for caching processed data."""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            # Use a safe location for the database
            import platform
            from pathlib import Path
            
            try:
                system = platform.system()
                if system == "Windows":
                    if os.environ.get('APPDATA'):
                        user_dir = Path(os.environ['APPDATA']) / 'AmazonDashboard'
                    else:
                        user_dir = Path.home() / 'AppData' / 'Roaming' / 'AmazonDashboard'
                else:  # macOS and Linux
                    if system == "Darwin":  # macOS
                        user_dir = Path.home() / 'Library' / 'Application Support' / 'AmazonDashboard'
                    else:  # Linux
                        user_dir = Path.home() / '.AmazonDashboard'
                
                # Create directory if it doesn't exist
                user_dir.mkdir(parents=True, exist_ok=True)
                db_path = str(user_dir / "audit_cache.db")
            except Exception:
                # Fallback to current directory
                db_path = "audit_cache.db"
                
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create tables for caching different types of data
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS data_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cache_key TEXT UNIQUE NOT NULL,
                data_type TEXT NOT NULL,
                data_hash TEXT NOT NULL,
                compressed_data BLOB,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS client_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_name TEXT NOT NULL,
                data_type TEXT NOT NULL,
                file_hash TEXT NOT NULL,
                processed_data BLOB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(client_name, data_type, file_hash)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analysis_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_name TEXT NOT NULL,
                analysis_type TEXT NOT NULL,
                input_hash TEXT NOT NULL,
                result_data BLOB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(client_name, analysis_type, input_hash)
            )
        ''')
        
        # Client config cache table (per-user)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS client_config_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                client_name TEXT NOT NULL,
                config_data TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, client_name)
            )
        ''')
        
        # Client names cache table (per-user)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS client_names_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL UNIQUE,
                client_names TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Session metadata cache table (per-user, per-client)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS session_metadata_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                client_name TEXT NOT NULL,
                session_list TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, client_name)
            )
        ''')
        
        # Create indexes for better performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_cache_key ON data_cache(cache_key)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_client_data ON client_data(client_name, data_type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_analysis_cache ON analysis_cache(client_name, analysis_type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_client_config_cache ON client_config_cache(user_id, client_name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_client_names_cache ON client_names_cache(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_session_metadata_cache ON session_metadata_cache(user_id, client_name)')
        
        conn.commit()
        conn.close()
    
    def _calculate_hash(self, data: Any) -> str:
        """Calculate hash for data to detect changes."""
        if isinstance(data, pd.DataFrame):
            # For DataFrames, use a combination of shape, columns, and sample data
            hash_input = f"{data.shape}_{list(data.columns)}_{data.head().to_string()}"
        elif isinstance(data, dict):
            # For dictionaries, convert to JSON string
            hash_input = json.dumps(data, sort_keys=True, default=str)
        else:
            # For other types, convert to string
            hash_input = str(data)
        
        return hashlib.md5(hash_input.encode()).hexdigest()
    
    def _compress_data(self, data: Any) -> bytes:
        """Compress data for storage."""
        pickled_data = pickle.dumps(data)
        return gzip.compress(pickled_data)
    
    def _decompress_data(self, compressed_data: bytes) -> Any:
        """Decompress data from storage."""
        decompressed = gzip.decompress(compressed_data)
        return pickle.loads(decompressed)
    
    def cache_bulk_data(self, client_name: str, file_content: bytes, processed_data: Dict[str, pd.DataFrame]) -> bool:
        """Cache processed bulk data."""
        try:
            file_hash = hashlib.md5(file_content).hexdigest()
            compressed_data = self._compress_data(processed_data)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO client_data (client_name, data_type, file_hash, processed_data)
                VALUES (?, ?, ?, ?)
            ''', (client_name, 'bulk_data', file_hash, compressed_data))
            
            conn.commit()
            conn.close()
            
            if 'debug_messages' in st.session_state:
                st.session_state.debug_messages.append(f"[DB] Cached bulk data for {client_name} with hash {file_hash[:8]}")
            
            return True
        except Exception as e:
            if 'debug_messages' in st.session_state:
                st.session_state.debug_messages.append(f"[DB Error] Failed to cache bulk data: {str(e)}")
            return False
    
    def get_cached_bulk_data(self, client_name: str, file_content: bytes) -> Optional[Dict[str, pd.DataFrame]]:
        """Retrieve cached bulk data if it exists and matches the file hash."""
        try:
            file_hash = hashlib.md5(file_content).hexdigest()
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT processed_data FROM client_data 
                WHERE client_name = ? AND data_type = ? AND file_hash = ?
            ''', (client_name, 'bulk_data', file_hash))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                processed_data = self._decompress_data(result[0])
                if 'debug_messages' in st.session_state:
                    st.session_state.debug_messages.append(f"[DB] Retrieved cached bulk data for {client_name}")
                return processed_data
            
            return None
        except Exception as e:
            if 'debug_messages' in st.session_state:
                st.session_state.debug_messages.append(f"[DB Error] Failed to retrieve cached bulk data: {str(e)}")
            return None
    
    def cache_sales_report(self, client_name: str, file_content: bytes, processed_data: pd.DataFrame) -> bool:
        """Cache processed sales report data."""
        try:
            file_hash = hashlib.md5(file_content).hexdigest()
            compressed_data = self._compress_data(processed_data)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO client_data (client_name, data_type, file_hash, processed_data)
                VALUES (?, ?, ?, ?)
            ''', (client_name, 'sales_report', file_hash, compressed_data))
            
            conn.commit()
            conn.close()
            
            if 'debug_messages' in st.session_state:
                st.session_state.debug_messages.append(f"[DB] Cached sales report for {client_name} with hash {file_hash[:8]}")
            
            return True
        except Exception as e:
            if 'debug_messages' in st.session_state:
                st.session_state.debug_messages.append(f"[DB Error] Failed to cache sales report: {str(e)}")
            return False
    
    def get_cached_sales_report(self, client_name: str, file_content: bytes) -> Optional[pd.DataFrame]:
        """Retrieve cached sales report data if it exists and matches the file hash."""
        try:
            file_hash = hashlib.md5(file_content).hexdigest()
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT processed_data FROM client_data 
                WHERE client_name = ? AND data_type = ? AND file_hash = ?
            ''', (client_name, 'sales_report', file_hash))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                processed_data = self._decompress_data(result[0])
                if 'debug_messages' in st.session_state:
                    st.session_state.debug_messages.append(f"[DB] Retrieved cached sales report for {client_name}")
                return processed_data
            
            return None
        except Exception as e:
            if 'debug_messages' in st.session_state:
                st.session_state.debug_messages.append(f"[DB Error] Failed to retrieve cached sales report: {str(e)}")
            return None
    
    def cache_analysis_result(self, client_name: str, analysis_type: str, input_data: Any, result_data: Any) -> bool:
        """Cache analysis results."""
        try:
            input_hash = self._calculate_hash(input_data)
            compressed_data = self._compress_data(result_data)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO analysis_cache (client_name, analysis_type, input_hash, result_data)
                VALUES (?, ?, ?, ?)
            ''', (client_name, analysis_type, input_hash, compressed_data))
            
            conn.commit()
            conn.close()
            
            if 'debug_messages' in st.session_state:
                st.session_state.debug_messages.append(f"[DB] Cached {analysis_type} analysis for {client_name}")
            
            return True
        except Exception as e:
            if 'debug_messages' in st.session_state:
                st.session_state.debug_messages.append(f"[DB Error] Failed to cache analysis result: {str(e)}")
            return False
    
    def get_cached_analysis_result(self, client_name: str, analysis_type: str, input_data: Any) -> Optional[Any]:
        """Retrieve cached analysis result if it exists and matches the input hash."""
        try:
            input_hash = self._calculate_hash(input_data)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT result_data FROM analysis_cache 
                WHERE client_name = ? AND analysis_type = ? AND input_hash = ?
            ''', (client_name, analysis_type, input_hash))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                result_data = self._decompress_data(result[0])
                if 'debug_messages' in st.session_state:
                    st.session_state.debug_messages.append(f"[DB] Retrieved cached {analysis_type} analysis for {client_name}")
                return result_data
            
            return None
        except Exception as e:
            if 'debug_messages' in st.session_state:
                st.session_state.debug_messages.append(f"[DB Error] Failed to retrieve cached analysis result: {str(e)}")
            return None
    
    def clear_client_cache(self, client_name: str) -> bool:
        """Clear all cached data for a specific client."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM client_data WHERE client_name = ?', (client_name,))
            cursor.execute('DELETE FROM analysis_cache WHERE client_name = ?', (client_name,))
            
            conn.commit()
            conn.close()
            
            if 'debug_messages' in st.session_state:
                st.session_state.debug_messages.append(f"[DB] Cleared all cache for {client_name}")
            
            return True
        except Exception as e:
            if 'debug_messages' in st.session_state:
                st.session_state.debug_messages.append(f"[DB Error] Failed to clear client cache: {str(e)}")
            return False
    
    # ========== Client Config Caching Methods ==========
    
    def cache_client_names(self, user_id: str, client_names: List[str]) -> bool:
        """Cache list of client names for a user."""
        try:
            import time as _t
            _t0 = _t.perf_counter()
            
            names_json = json.dumps(client_names)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO client_names_cache (user_id, client_names, last_accessed)
                VALUES (?, ?, CURRENT_TIMESTAMP)
            ''', (user_id, names_json))
            
            conn.commit()
            conn.close()
            
            _elapsed = (_t.perf_counter() - _t0) * 1000
            if 'debug_messages' in st.session_state:
                st.session_state.debug_messages.append(f"[SQLite] Cached {len(client_names)} client names for user in {int(_elapsed)}ms")
            
            return True
        except Exception as e:
            if 'debug_messages' in st.session_state:
                st.session_state.debug_messages.append(f"[SQLite Error] Failed to cache client names: {str(e)}")
            return False
    
    def get_cached_client_names(self, user_id: str, max_age_seconds: int = 1800) -> Optional[List[str]]:
        """Retrieve cached client names for a user if not expired (default 30 min)."""
        try:
            import time as _t
            _t0 = _t.perf_counter()
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT client_names, 
                       (julianday('now') - julianday(last_accessed)) * 86400 as age_seconds
                FROM client_names_cache 
                WHERE user_id = ?
            ''', (user_id,))
            
            result = cursor.fetchone()
            
            if result:
                names_json, age = result
                if age <= max_age_seconds:
                    # Update last_accessed
                    cursor.execute('''
                        UPDATE client_names_cache 
                        SET last_accessed = CURRENT_TIMESTAMP 
                        WHERE user_id = ?
                    ''', (user_id,))
                    conn.commit()
                    conn.close()
                    
                    client_names = json.loads(names_json)
                    _elapsed = (_t.perf_counter() - _t0) * 1000
                    if 'debug_messages' in st.session_state:
                        st.session_state.debug_messages.append(f"[SQLite] Retrieved {len(client_names)} client names from cache in {int(_elapsed)}ms")
                    return client_names
            
            conn.close()
            return None
        except Exception as e:
            if 'debug_messages' in st.session_state:
                st.session_state.debug_messages.append(f"[SQLite Error] Failed to retrieve cached client names: {str(e)}")
            return None
    
    def cache_client_config(self, user_id: str, client_name: str, config_data: Dict[str, Any]) -> bool:
        """Cache a client config for a user."""
        try:
            import time as _t
            _t0 = _t.perf_counter()
            
            config_json = json.dumps(config_data)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO client_config_cache 
                (user_id, client_name, config_data, last_accessed)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            ''', (user_id, client_name, config_json))
            
            conn.commit()
            conn.close()
            
            _elapsed = (_t.perf_counter() - _t0) * 1000
            if 'debug_messages' in st.session_state:
                st.session_state.debug_messages.append(f"[SQLite] Cached config for {client_name} in {int(_elapsed)}ms")
            
            return True
        except Exception as e:
            if 'debug_messages' in st.session_state:
                st.session_state.debug_messages.append(f"[SQLite Error] Failed to cache client config: {str(e)}")
            return False
    
    def get_cached_client_config(self, user_id: str, client_name: str, max_age_seconds: int = 1800) -> Optional[Dict[str, Any]]:
        """Retrieve cached client config if not expired (default 30 min)."""
        try:
            import time as _t
            _t0 = _t.perf_counter()
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT config_data,
                       (julianday('now') - julianday(last_accessed)) * 86400 as age_seconds
                FROM client_config_cache 
                WHERE user_id = ? AND client_name = ?
            ''', (user_id, client_name))
            
            result = cursor.fetchone()
            
            if result:
                config_json, age = result
                if age <= max_age_seconds:
                    # Update last_accessed
                    cursor.execute('''
                        UPDATE client_config_cache 
                        SET last_accessed = CURRENT_TIMESTAMP 
                        WHERE user_id = ? AND client_name = ?
                    ''', (user_id, client_name))
                    conn.commit()
                    conn.close()
                    
                    config_data = json.loads(config_json)
                    _elapsed = (_t.perf_counter() - _t0) * 1000
                    if 'debug_messages' in st.session_state:
                        st.session_state.debug_messages.append(f"[SQLite] Retrieved config for {client_name} from cache in {int(_elapsed)}ms")
                    return config_data
            
            conn.close()
            return None
        except Exception as e:
            if 'debug_messages' in st.session_state:
                st.session_state.debug_messages.append(f"[SQLite Error] Failed to retrieve cached client config: {str(e)}")
            return None
    
    def cache_session_list(self, user_id: str, client_name: str, session_list: List[Dict[str, Any]]) -> bool:
        """Cache session list for a client."""
        try:
            import time as _t
            _t0 = _t.perf_counter()
            
            sessions_json = json.dumps(session_list)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO session_metadata_cache 
                (user_id, client_name, session_list, last_accessed)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            ''', (user_id, client_name, sessions_json))
            
            conn.commit()
            conn.close()
            
            _elapsed = (_t.perf_counter() - _t0) * 1000
            if 'debug_messages' in st.session_state:
                st.session_state.debug_messages.append(f"[SQLite] Cached {len(session_list)} sessions for {client_name} in {int(_elapsed)}ms")
            
            return True
        except Exception as e:
            if 'debug_messages' in st.session_state:
                st.session_state.debug_messages.append(f"[SQLite Error] Failed to cache session list: {str(e)}")
            return False
    
    def get_cached_session_list(self, user_id: str, client_name: str, max_age_seconds: int = 300) -> Optional[List[Dict[str, Any]]]:
        """Retrieve cached session list if not expired (default 5 min)."""
        try:
            import time as _t
            _t0 = _t.perf_counter()
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT session_list,
                       (julianday('now') - julianday(last_accessed)) * 86400 as age_seconds
                FROM session_metadata_cache 
                WHERE user_id = ? AND client_name = ?
            ''', (user_id, client_name))
            
            result = cursor.fetchone()
            
            if result:
                sessions_json, age = result
                if age <= max_age_seconds:
                    # Update last_accessed
                    cursor.execute('''
                        UPDATE session_metadata_cache 
                        SET last_accessed = CURRENT_TIMESTAMP 
                        WHERE user_id = ? AND client_name = ?
                    ''', (user_id, client_name))
                    conn.commit()
                    conn.close()
                    
                    session_list = json.loads(sessions_json)
                    _elapsed = (_t.perf_counter() - _t0) * 1000
                    if 'debug_messages' in st.session_state:
                        st.session_state.debug_messages.append(f"[SQLite] Retrieved {len(session_list)} sessions from cache in {int(_elapsed)}ms")
                    return session_list
            
            conn.close()
            return None
        except Exception as e:
            if 'debug_messages' in st.session_state:
                st.session_state.debug_messages.append(f"[SQLite Error] Failed to retrieve cached session list: {str(e)}")
            return None
    
    def invalidate_client_cache(self, user_id: str, client_name: str = None) -> bool:
        """Invalidate cached data for a user or specific client."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if client_name:
                # Invalidate specific client
                cursor.execute('DELETE FROM client_config_cache WHERE user_id = ? AND client_name = ?', 
                             (user_id, client_name))
                cursor.execute('DELETE FROM session_metadata_cache WHERE user_id = ? AND client_name = ?', 
                             (user_id, client_name))
                if 'debug_messages' in st.session_state:
                    st.session_state.debug_messages.append(f"[SQLite] Invalidated cache for {client_name}")
            else:
                # Invalidate all for user
                cursor.execute('DELETE FROM client_config_cache WHERE user_id = ?', (user_id,))
                cursor.execute('DELETE FROM client_names_cache WHERE user_id = ?', (user_id,))
                cursor.execute('DELETE FROM session_metadata_cache WHERE user_id = ?', (user_id,))
                if 'debug_messages' in st.session_state:
                    st.session_state.debug_messages.append(f"[SQLite] Invalidated all cache for user")
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            if 'debug_messages' in st.session_state:
                st.session_state.debug_messages.append(f"[SQLite Error] Failed to invalidate cache: {str(e)}")
            return False
    
    # ========== End Client Config Caching Methods ==========
    
    def cleanup_old_cache(self, days_old: int = 7) -> bool:
        """Remove cached data older than specified days."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                DELETE FROM data_cache 
                WHERE created_at < datetime('now', '-{} days')
            '''.format(days_old))
            
            cursor.execute('''
                DELETE FROM client_data 
                WHERE created_at < datetime('now', '-{} days')
            '''.format(days_old))
            
            cursor.execute('''
                DELETE FROM analysis_cache 
                WHERE created_at < datetime('now', '-{} days')
            '''.format(days_old))
            
            conn.commit()
            conn.close()
            
            if 'debug_messages' in st.session_state:
                st.session_state.debug_messages.append(f"[DB] Cleaned up cache older than {days_old} days")
            
            return True
        except Exception as e:
            if 'debug_messages' in st.session_state:
                st.session_state.debug_messages.append(f"[DB Error] Failed to cleanup old cache: {str(e)}")
            return False
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get total cache size
            cursor.execute('SELECT COUNT(*) FROM data_cache')
            total_cache_entries = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM client_data')
            total_client_entries = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM analysis_cache')
            total_analysis_entries = cursor.fetchone()[0]
            
            # Get database file size
            db_size = os.path.getsize(self.db_path) if os.path.exists(self.db_path) else 0
            
            conn.close()
            
            return {
                'total_cache_entries': total_cache_entries,
                'total_client_entries': total_client_entries,
                'total_analysis_entries': total_analysis_entries,
                'db_size_mb': db_size / (1024 * 1024),
                'db_path': self.db_path
            }
        except Exception as e:
            if 'debug_messages' in st.session_state:
                st.session_state.debug_messages.append(f"[DB Error] Failed to get cache stats: {str(e)}")
            return {}

# Global database manager instance
db_manager = DatabaseManager() 