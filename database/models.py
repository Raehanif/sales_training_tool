import sqlite3
import pandas as pd
from datetime import datetime
from typing import Optional, List, Dict, Any
import os

class DatabaseManager:
    """Database manager for NBP Sales Preparation Tool"""
    
    def __init__(self, db_path: str = 'nbp_sales.db'):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
        """Initialize database with required tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Prospects table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS prospects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                company_name TEXT NOT NULL,
                website TEXT,
                industry TEXT,
                company_size TEXT,
                business_category TEXT,
                meeting_objective TEXT,
                context TEXT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Additional contacts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS additional_contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prospect_id INTEGER,
                contact_name TEXT NOT NULL,
                title TEXT,
                linkedin_url TEXT,
                email TEXT,
                phone TEXT,
                is_primary BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (prospect_id) REFERENCES prospects (id)
            )
        ''')
        
        # Generated scripts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS generated_scripts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prospect_id INTEGER,
                user_id INTEGER,
                script_type TEXT NOT NULL,
                content TEXT NOT NULL,
                ai_model TEXT,
                tokens_used INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (prospect_id) REFERENCES prospects (id),
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Sales pitches table (existing)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sales_pitches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                industry TEXT,
                target_audience TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Feedback table (existing)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pitch_id INTEGER,
                feedback_text TEXT NOT NULL,
                score INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (pitch_id) REFERENCES sales_pitches (id)
            )
        ''')
        
        # Analytics table (existing)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analytics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                action_type TEXT NOT NULL,
                action_data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    # User operations
    def create_user(self, username: str, password_hash: str) -> bool:
        """Create a new user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                'INSERT INTO users (username, password_hash) VALUES (?, ?)',
                (username, password_hash)
            )
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()
    
    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user by username"""
        # For hardcoded auth, return hardcoded user data
        if username == "sales_rep":
            return {
                "id": 1,
                "username": "sales_rep",
                "created_at": "2024-01-01"
            }
        
        # Fallback to database lookup for other users
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            columns = [description[0] for description in cursor.description]
            return dict(zip(columns, result))
        return None
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        if user_id == 1:  # Hardcoded user
            return {
                "id": 1,
                "username": "sales_rep",
                "created_at": "2024-01-01"
            }
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            columns = [description[0] for description in cursor.description]
            return dict(zip(columns, result))
        return None
    
    # Prospect operations
    def create_prospect(self, user_id: int, prospect_data: Dict[str, Any]) -> int:
        """Create a new prospect"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO prospects (
                user_id, company_name, website, industry, company_size,
                business_category, meeting_objective, context, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id,
            prospect_data['company_name'],
            prospect_data.get('website'),
            prospect_data.get('industry'),
            prospect_data.get('company_size'),
            prospect_data.get('business_category'),
            prospect_data.get('meeting_objective'),
            prospect_data.get('context'),
            prospect_data.get('notes')
        ))
        
        prospect_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return prospect_id
    
    def get_user_prospects(self, user_id: int) -> pd.DataFrame:
        """Get all prospects for a user"""
        conn = self.get_connection()
        prospects = pd.read_sql_query(
            'SELECT * FROM prospects WHERE user_id = ? ORDER BY created_at DESC',
            conn, params=[user_id]
        )
        conn.close()
        return prospects
    
    def get_prospect_by_id(self, prospect_id: int) -> Optional[Dict[str, Any]]:
        """Get prospect by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM prospects WHERE id = ?', (prospect_id,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            columns = [description[0] for description in cursor.description]
            return dict(zip(columns, result))
        return None
    
    def update_prospect(self, prospect_id: int, prospect_data: Dict[str, Any]) -> bool:
        """Update a prospect"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE prospects 
            SET company_name = ?, website = ?, industry = ?, company_size = ?,
                business_category = ?, meeting_objective = ?, context = ?, notes = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (
            prospect_data['company_name'],
            prospect_data.get('website'),
            prospect_data.get('industry'),
            prospect_data.get('company_size'),
            prospect_data.get('business_category'),
            prospect_data.get('meeting_objective'),
            prospect_data.get('context'),
            prospect_data.get('notes'),
            prospect_id
        ))
        
        affected_rows = cursor.rowcount
        conn.commit()
        conn.close()
        
        return affected_rows > 0
    
    def delete_prospect(self, prospect_id: int) -> bool:
        """Delete a prospect"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM prospects WHERE id = ?', (prospect_id,))
        affected_rows = cursor.rowcount
        conn.commit()
        conn.close()
        
        return affected_rows > 0
    
    # Contact operations
    def create_contact(self, prospect_id: int, contact_data: Dict[str, Any]) -> int:
        """Create a new contact"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO additional_contacts (
                prospect_id, contact_name, title, linkedin_url, email, phone, is_primary
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            prospect_id,
            contact_data['contact_name'],
            contact_data.get('title'),
            contact_data.get('linkedin_url'),
            contact_data.get('email'),
            contact_data.get('phone'),
            contact_data.get('is_primary', False)
        ))
        
        contact_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return contact_id
    
    def get_prospect_contacts(self, prospect_id: int) -> pd.DataFrame:
        """Get all contacts for a prospect"""
        conn = self.get_connection()
        contacts = pd.read_sql_query(
            'SELECT * FROM additional_contacts WHERE prospect_id = ? ORDER BY is_primary DESC, created_at ASC',
            conn, params=[prospect_id]
        )
        conn.close()
        return contacts
    
    def update_contact(self, contact_id: int, contact_data: Dict[str, Any]) -> bool:
        """Update a contact"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE additional_contacts 
            SET contact_name = ?, title = ?, linkedin_url = ?, email = ?, phone = ?, is_primary = ?
            WHERE id = ?
        ''', (
            contact_data['contact_name'],
            contact_data.get('title'),
            contact_data.get('linkedin_url'),
            contact_data.get('email'),
            contact_data.get('phone'),
            contact_data.get('is_primary', False),
            contact_id
        ))
        
        affected_rows = cursor.rowcount
        conn.commit()
        conn.close()
        
        return affected_rows > 0
    
    def delete_contact(self, contact_id: int) -> bool:
        """Delete a contact"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM additional_contacts WHERE id = ?', (contact_id,))
        affected_rows = cursor.rowcount
        conn.commit()
        conn.close()
        
        return affected_rows > 0
    
    # Generated scripts operations
    def create_generated_script(self, prospect_id: int, user_id: int, script_data: Dict[str, Any]) -> int:
        """Create a new generated script"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO generated_scripts (
                prospect_id, user_id, script_type, content, ai_model, tokens_used
            ) VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            prospect_id,
            user_id,
            script_data['script_type'],
            script_data['content'],
            script_data.get('ai_model'),
            script_data.get('tokens_used')
        ))
        
        script_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return script_id
    
    def get_prospect_scripts(self, prospect_id: int) -> pd.DataFrame:
        """Get all generated scripts for a prospect"""
        conn = self.get_connection()
        scripts = pd.read_sql_query(
            'SELECT * FROM generated_scripts WHERE prospect_id = ? ORDER BY created_at DESC',
            conn, params=[prospect_id]
        )
        conn.close()
        return scripts
    
    def get_user_scripts(self, user_id: int) -> pd.DataFrame:
        """Get all generated scripts for a user"""
        conn = self.get_connection()
        scripts = pd.read_sql_query(
            'SELECT * FROM generated_scripts WHERE user_id = ? ORDER BY created_at DESC',
            conn, params=[user_id]
        )
        conn.close()
        return scripts
    
    # Analytics operations
    def log_analytics(self, user_id: int, action_type: str, action_data: Optional[str] = None):
        """Log user analytics"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO analytics (user_id, action_type, action_data)
            VALUES (?, ?, ?)
        ''', (user_id, action_type, action_data))
        
        conn.commit()
        conn.close()
    
    def get_user_analytics(self, user_id: int) -> pd.DataFrame:
        """Get analytics for a user"""
        conn = self.get_connection()
        analytics = pd.read_sql_query(
            'SELECT * FROM analytics WHERE user_id = ? ORDER BY created_at DESC',
            conn, params=[user_id]
        )
        conn.close()
        return analytics
    
    # Statistics operations
    def get_user_statistics(self, user_id: int) -> Dict[str, Any]:
        """Get comprehensive statistics for a user"""
        conn = self.get_connection()
        
        # Total prospects
        prospect_count = pd.read_sql_query(
            'SELECT COUNT(*) as count FROM prospects WHERE user_id = ?',
            conn, params=[user_id]
        ).iloc[0]['count']
        
        # Total contacts
        contact_count = pd.read_sql_query('''
            SELECT COUNT(*) as count 
            FROM additional_contacts ac
            JOIN prospects p ON ac.prospect_id = p.id
            WHERE p.user_id = ?
        ''', conn, params=[user_id]).iloc[0]['count']
        
        # Total scripts
        script_count = pd.read_sql_query(
            'SELECT COUNT(*) as count FROM generated_scripts WHERE user_id = ?',
            conn, params=[user_id]
        ).iloc[0]['count']
        
        # Recent prospects
        recent_prospects = pd.read_sql_query(
            'SELECT company_name, created_at FROM prospects WHERE user_id = ? ORDER BY created_at DESC LIMIT 5',
            conn, params=[user_id]
        )
        
        conn.close()
        
        return {
            'total_prospects': prospect_count,
            'total_contacts': contact_count,
            'total_scripts': script_count,
            'recent_prospects': recent_prospects.to_dict('records')
        }
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get overall database statistics"""
        conn = self.get_connection()
        
        # Total users
        total_users = pd.read_sql_query('SELECT COUNT(*) as count FROM users', conn).iloc[0]['count']
        
        # Total prospects
        total_prospects = pd.read_sql_query('SELECT COUNT(*) as count FROM prospects', conn).iloc[0]['count']
        
        # Total contacts
        total_contacts = pd.read_sql_query('SELECT COUNT(*) as count FROM additional_contacts', conn).iloc[0]['count']
        
        # Total scripts
        total_scripts = pd.read_sql_query('SELECT COUNT(*) as count FROM generated_scripts', conn).iloc[0]['count']
        
        conn.close()
        
        return {
            'total_users': total_users,
            'total_prospects': total_prospects,
            'total_contacts': total_contacts,
            'total_scripts': total_scripts
        }

# Global database instance
db = DatabaseManager()

# Additional functions for AI generation component
def save_generated_script(script_record: Dict[str, Any]) -> bool:
    """Save generated script to database"""
    try:
        return db.create_generated_script(
            prospect_id=script_record.get('prospect_id'),
            user_id=script_record.get('user_id', 1),  # Default to hardcoded user
            script_data={
                'script_type': script_record.get('script_type'),
                'content': script_record.get('generated_content'),
                'ai_model': script_record.get('model_used'),
                'tokens_used': script_record.get('tokens_used', 0)
            }
        ) > 0
    except Exception as e:
        print(f"Error saving generated script: {e}")
        return False

def get_generated_scripts() -> List[Dict[str, Any]]:
    """Get all generated scripts with prospect information"""
    try:
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                gs.*,
                p.company_name,
                p.industry,
                p.meeting_objective
            FROM generated_scripts gs
            LEFT JOIN prospects p ON gs.prospect_id = p.id
            ORDER BY gs.created_at DESC
        ''')
        
        results = cursor.fetchall()
        columns = [description[0] for description in cursor.description]
        
        scripts = []
        for row in results:
            script_dict = dict(zip(columns, row))
            scripts.append(script_dict)
        
        conn.close()
        return scripts
    except Exception as e:
        print(f"Error getting generated scripts: {e}")
        return [] 