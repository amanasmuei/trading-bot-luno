"""
Database Manager
Comprehensive database management for historical data storage and retrieval
"""

import logging
import sqlite3
import pandas as pd
import json
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from pathlib import Path
import os

try:
    from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, Boolean
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy.orm import sessionmaker, Session
    SQLALCHEMY_AVAILABLE = True
except ImportError:
    SQLALCHEMY_AVAILABLE = False

logger = logging.getLogger(__name__)

Base = declarative_base() if SQLALCHEMY_AVAILABLE else None


@dataclass
class MarketDataRecord:
    """Market data record structure"""
    timestamp: datetime
    pair: str
    open_price: float
    high_price: float
    low_price: float
    close_price: float
    volume: float
    timeframe: str = "1h"


@dataclass
class TradeRecord:
    """Trade record structure"""
    trade_id: str
    timestamp: datetime
    pair: str
    action: str  # BUY/SELL
    volume: float
    price: float
    commission: float
    pnl: float
    strategy: str
    confidence: float
    metadata: Dict[str, Any] = None


@dataclass
class PerformanceRecord:
    """Performance metrics record"""
    timestamp: datetime
    portfolio_value: float
    total_pnl: float
    daily_pnl: float
    drawdown: float
    sharpe_ratio: float
    win_rate: float
    total_trades: int
    metadata: Dict[str, Any] = None


class DatabaseManager:
    """Comprehensive database management system"""
    
    def __init__(self, db_path: str = "data/trading_bot.db", use_sqlite: bool = True):
        self.db_path = db_path
        self.use_sqlite = use_sqlite
        
        # Ensure data directory exists
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        if use_sqlite:
            self._init_sqlite()
        elif SQLALCHEMY_AVAILABLE:
            self._init_sqlalchemy()
        else:
            logger.warning("SQLAlchemy not available, falling back to SQLite")
            self._init_sqlite()
    
    def _init_sqlite(self):
        """Initialize SQLite database"""
        self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
        self.connection.row_factory = sqlite3.Row
        self._create_sqlite_tables()
        logger.info(f"SQLite database initialized: {self.db_path}")
    
    def _init_sqlalchemy(self):
        """Initialize SQLAlchemy database"""
        # For now, use SQLite with SQLAlchemy
        engine_url = f"sqlite:///{self.db_path}"
        self.engine = create_engine(engine_url, echo=False)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
        # Create tables
        Base.metadata.create_all(bind=self.engine)
        logger.info(f"SQLAlchemy database initialized: {self.db_path}")
    
    def _create_sqlite_tables(self):
        """Create SQLite tables"""
        cursor = self.connection.cursor()
        
        # Market data table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS market_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME NOT NULL,
                pair TEXT NOT NULL,
                open_price REAL NOT NULL,
                high_price REAL NOT NULL,
                low_price REAL NOT NULL,
                close_price REAL NOT NULL,
                volume REAL NOT NULL,
                timeframe TEXT DEFAULT '1h',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(timestamp, pair, timeframe)
            )
        """)
        
        # Trades table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                trade_id TEXT UNIQUE NOT NULL,
                timestamp DATETIME NOT NULL,
                pair TEXT NOT NULL,
                action TEXT NOT NULL,
                volume REAL NOT NULL,
                price REAL NOT NULL,
                commission REAL DEFAULT 0,
                pnl REAL DEFAULT 0,
                strategy TEXT,
                confidence REAL,
                metadata TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Performance table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME NOT NULL,
                portfolio_value REAL NOT NULL,
                total_pnl REAL DEFAULT 0,
                daily_pnl REAL DEFAULT 0,
                drawdown REAL DEFAULT 0,
                sharpe_ratio REAL DEFAULT 0,
                win_rate REAL DEFAULT 0,
                total_trades INTEGER DEFAULT 0,
                metadata TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Signals table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS signals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME NOT NULL,
                pair TEXT NOT NULL,
                signal_type TEXT NOT NULL,
                action TEXT NOT NULL,
                confidence REAL NOT NULL,
                price REAL NOT NULL,
                indicators TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Portfolio allocations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS portfolio_allocations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME NOT NULL,
                pair TEXT NOT NULL,
                target_weight REAL NOT NULL,
                current_weight REAL NOT NULL,
                position_size REAL NOT NULL,
                unrealized_pnl REAL DEFAULT 0,
                metadata TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create indexes for better performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_market_data_timestamp ON market_data(timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_market_data_pair ON market_data(pair)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_trades_timestamp ON trades(timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_trades_pair ON trades(pair)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_performance_timestamp ON performance(timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_signals_timestamp ON signals(timestamp)")
        
        self.connection.commit()
        logger.info("SQLite tables created successfully")
    
    def store_market_data(self, data: List[MarketDataRecord]) -> bool:
        """Store market data records"""
        try:
            cursor = self.connection.cursor()
            
            for record in data:
                cursor.execute("""
                    INSERT OR REPLACE INTO market_data 
                    (timestamp, pair, open_price, high_price, low_price, close_price, volume, timeframe)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    record.timestamp,
                    record.pair,
                    record.open_price,
                    record.high_price,
                    record.low_price,
                    record.close_price,
                    record.volume,
                    record.timeframe
                ))
            
            self.connection.commit()
            logger.debug(f"Stored {len(data)} market data records")
            return True
            
        except Exception as e:
            logger.error(f"Error storing market data: {e}")
            return False
    
    def store_trade(self, trade: TradeRecord) -> bool:
        """Store a trade record"""
        try:
            cursor = self.connection.cursor()
            
            metadata_json = json.dumps(trade.metadata) if trade.metadata else None
            
            cursor.execute("""
                INSERT OR REPLACE INTO trades 
                (trade_id, timestamp, pair, action, volume, price, commission, pnl, strategy, confidence, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                trade.trade_id,
                trade.timestamp,
                trade.pair,
                trade.action,
                trade.volume,
                trade.price,
                trade.commission,
                trade.pnl,
                trade.strategy,
                trade.confidence,
                metadata_json
            ))
            
            self.connection.commit()
            logger.debug(f"Stored trade record: {trade.trade_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error storing trade: {e}")
            return False
    
    def store_performance(self, performance: PerformanceRecord) -> bool:
        """Store performance metrics"""
        try:
            cursor = self.connection.cursor()
            
            metadata_json = json.dumps(performance.metadata) if performance.metadata else None
            
            cursor.execute("""
                INSERT INTO performance 
                (timestamp, portfolio_value, total_pnl, daily_pnl, drawdown, sharpe_ratio, win_rate, total_trades, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                performance.timestamp,
                performance.portfolio_value,
                performance.total_pnl,
                performance.daily_pnl,
                performance.drawdown,
                performance.sharpe_ratio,
                performance.win_rate,
                performance.total_trades,
                metadata_json
            ))
            
            self.connection.commit()
            logger.debug("Stored performance record")
            return True
            
        except Exception as e:
            logger.error(f"Error storing performance: {e}")
            return False
    
    def get_market_data(self, pair: str, start_time: datetime, end_time: datetime, 
                       timeframe: str = "1h") -> pd.DataFrame:
        """Retrieve market data for a specific pair and time range"""
        try:
            query = """
                SELECT timestamp, open_price, high_price, low_price, close_price, volume
                FROM market_data 
                WHERE pair = ? AND timeframe = ? AND timestamp BETWEEN ? AND ?
                ORDER BY timestamp
            """
            
            df = pd.read_sql_query(
                query, 
                self.connection, 
                params=(pair, timeframe, start_time, end_time),
                parse_dates=['timestamp']
            )
            
            return df
            
        except Exception as e:
            logger.error(f"Error retrieving market data: {e}")
            return pd.DataFrame()
    
    def get_trades(self, pair: Optional[str] = None, start_time: Optional[datetime] = None, 
                  end_time: Optional[datetime] = None) -> pd.DataFrame:
        """Retrieve trade records"""
        try:
            query = "SELECT * FROM trades WHERE 1=1"
            params = []
            
            if pair:
                query += " AND pair = ?"
                params.append(pair)
            
            if start_time:
                query += " AND timestamp >= ?"
                params.append(start_time)
            
            if end_time:
                query += " AND timestamp <= ?"
                params.append(end_time)
            
            query += " ORDER BY timestamp"
            
            df = pd.read_sql_query(
                query, 
                self.connection, 
                params=params,
                parse_dates=['timestamp', 'created_at']
            )
            
            # Parse metadata JSON
            if 'metadata' in df.columns:
                df['metadata'] = df['metadata'].apply(
                    lambda x: json.loads(x) if x else {}
                )
            
            return df
            
        except Exception as e:
            logger.error(f"Error retrieving trades: {e}")
            return pd.DataFrame()
    
    def get_performance_history(self, start_time: Optional[datetime] = None, 
                              end_time: Optional[datetime] = None) -> pd.DataFrame:
        """Retrieve performance history"""
        try:
            query = "SELECT * FROM performance WHERE 1=1"
            params = []
            
            if start_time:
                query += " AND timestamp >= ?"
                params.append(start_time)
            
            if end_time:
                query += " AND timestamp <= ?"
                params.append(end_time)
            
            query += " ORDER BY timestamp"
            
            df = pd.read_sql_query(
                query, 
                self.connection, 
                params=params,
                parse_dates=['timestamp', 'created_at']
            )
            
            return df
            
        except Exception as e:
            logger.error(f"Error retrieving performance history: {e}")
            return pd.DataFrame()
    
    def store_signal(self, timestamp: datetime, pair: str, signal_type: str, 
                    action: str, confidence: float, price: float, 
                    indicators: Dict[str, Any]) -> bool:
        """Store trading signal"""
        try:
            cursor = self.connection.cursor()
            
            indicators_json = json.dumps(indicators)
            
            cursor.execute("""
                INSERT INTO signals 
                (timestamp, pair, signal_type, action, confidence, price, indicators)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                timestamp, pair, signal_type, action, confidence, price, indicators_json
            ))
            
            self.connection.commit()
            return True
            
        except Exception as e:
            logger.error(f"Error storing signal: {e}")
            return False
    
    def get_latest_performance(self) -> Optional[Dict]:
        """Get the latest performance record"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT * FROM performance 
                ORDER BY timestamp DESC 
                LIMIT 1
            """)
            
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving latest performance: {e}")
            return None
    
    def calculate_trade_statistics(self, pair: Optional[str] = None, 
                                 days: int = 30) -> Dict[str, Any]:
        """Calculate trade statistics for the specified period"""
        try:
            start_time = datetime.now() - timedelta(days=days)
            trades_df = self.get_trades(pair=pair, start_time=start_time)
            
            if trades_df.empty:
                return {}
            
            # Calculate statistics
            total_trades = len(trades_df)
            winning_trades = len(trades_df[trades_df['pnl'] > 0])
            losing_trades = len(trades_df[trades_df['pnl'] < 0])
            
            win_rate = winning_trades / total_trades if total_trades > 0 else 0
            total_pnl = trades_df['pnl'].sum()
            avg_win = trades_df[trades_df['pnl'] > 0]['pnl'].mean() if winning_trades > 0 else 0
            avg_loss = trades_df[trades_df['pnl'] < 0]['pnl'].mean() if losing_trades > 0 else 0
            
            profit_factor = abs(avg_win * winning_trades / (avg_loss * losing_trades)) if avg_loss != 0 and losing_trades > 0 else 0
            
            return {
                'total_trades': total_trades,
                'winning_trades': winning_trades,
                'losing_trades': losing_trades,
                'win_rate': win_rate,
                'total_pnl': total_pnl,
                'avg_win': avg_win,
                'avg_loss': avg_loss,
                'profit_factor': profit_factor,
                'period_days': days
            }
            
        except Exception as e:
            logger.error(f"Error calculating trade statistics: {e}")
            return {}
    
    def cleanup_old_data(self, days_to_keep: int = 365):
        """Clean up old data to manage database size"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            cursor = self.connection.cursor()
            
            # Clean up old market data (keep more recent data)
            cursor.execute("DELETE FROM market_data WHERE timestamp < ?", (cutoff_date,))
            
            # Clean up old signals (keep less)
            signal_cutoff = datetime.now() - timedelta(days=90)
            cursor.execute("DELETE FROM signals WHERE timestamp < ?", (signal_cutoff,))
            
            # Keep all trades and performance data (important for analysis)
            
            self.connection.commit()
            logger.info(f"Cleaned up data older than {days_to_keep} days")
            
        except Exception as e:
            logger.error(f"Error cleaning up old data: {e}")
    
    def backup_database(self, backup_path: str) -> bool:
        """Create a backup of the database"""
        try:
            import shutil
            shutil.copy2(self.db_path, backup_path)
            logger.info(f"Database backed up to: {backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error backing up database: {e}")
            return False
    
    def close(self):
        """Close database connection"""
        if hasattr(self, 'connection'):
            self.connection.close()
            logger.info("Database connection closed")
