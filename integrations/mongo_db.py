#!/usr/bin/env python3
"""
MongoDB Integration for Contracts
Handles all contract-related database operations
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from enum import Enum
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import DuplicateKeyError, ConnectionFailure
from bson import ObjectId
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ContractType(str, Enum):
    """Contract types"""
    BASIC = "basic"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"
    CUSTOM = "custom"


class ContractStatus(str, Enum):
    """Contract status"""
    ACTIVE = "active"
    EXPIRED = "expired"
    CANCELLED = "cancelled"
    PENDING_RENEWAL = "pending_renewal"
    DRAFT = "draft"


class MongoDBManager:
    """MongoDB connection and operations manager"""
    
    def __init__(self, connection_string: str, database_name: str = "contracts"):
        self.connection_string = connection_string
        self.database_name = database_name
        self.client: Optional[MongoClient] = None
        self.db = None
        self.contracts_collection = None
        
    async def connect(self) -> bool:
        """Connect to MongoDB Atlas"""
        try:
            logger.info("Connecting to MongoDB Atlas...")
            
            # Use the same connection approach that works with mongosh
            self.client = MongoClient(
                self.connection_string,
                serverSelectionTimeoutMS=30000,
                connectTimeoutMS=20000,
                socketTimeoutMS=20000,
                maxPoolSize=10,
                retryWrites=True,
                w='majority',
                # MongoDB Atlas specific settings
                tls=True,
                tlsAllowInvalidCertificates=True,
                tlsAllowInvalidHostnames=True
            )
            
            # Test connection
            self.client.admin.command('ping')
            logger.info("✅ Successfully connected to MongoDB Atlas")
            
            # Set up database and collection
            self.db = self.client[self.database_name]
            self.contracts_collection = self.db.contracts
            
            # Create indexes
            await self._create_indexes()
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to MongoDB: {e}")
            return False
    
    async def _create_indexes(self):
        """Create necessary indexes for optimal performance"""
        try:
            # Unique index on account_id
            self.contracts_collection.create_index("account_id", unique=True)
            
            # Index on status for filtering
            self.contracts_collection.create_index("status")
            
            # Index on end_date for renewal queries
            self.contracts_collection.create_index("end_date")
            
            # Compound index for status + end_date
            self.contracts_collection.create_index([("status", ASCENDING), ("end_date", ASCENDING)])
            
            # Index on contract_type for plan-based queries
            self.contracts_collection.create_index("contract_type")
            
            logger.info("✅ Database indexes created successfully")
            
        except Exception as e:
            logger.error(f"❌ Error creating indexes: {e}")
    
    async def disconnect(self):
        """Disconnect from MongoDB"""
        if self.client:
            self.client.close()
            logger.info("Disconnected from MongoDB")
    
    def _generate_contract_id(self) -> str:
        """Generate a unique contract ID"""
        return f"contract_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{ObjectId()}"
    
    async def create_contract(self, contract_data: Dict[str, Any]) -> Optional[str]:
        """Create a new contract"""
        try:
            # Generate contract ID if not provided
            if 'contract_id' not in contract_data:
                contract_data['contract_id'] = self._generate_contract_id()
            
            # Add timestamps
            now = datetime.utcnow()
            contract_data['created_at'] = now
            contract_data['updated_at'] = now
            
            # Insert contract
            result = self.contracts_collection.insert_one(contract_data)
            
            logger.info(f"✅ Contract created successfully: {contract_data['contract_id']}")
            return str(result.inserted_id)
            
        except DuplicateKeyError:
            logger.error(f"❌ Contract already exists for account: {contract_data.get('account_id')}")
            return None
        except Exception as e:
            logger.error(f"❌ Error creating contract: {e}")
            return None
    
    async def get_contract_by_account_id(self, account_id: str) -> Optional[Dict[str, Any]]:
        """Get contract by account ID"""
        try:
            contract = self.contracts_collection.find_one({"account_id": account_id})
            if contract:
                # Convert ObjectId to string for JSON serialization
                contract['_id'] = str(contract['_id'])
                return contract
            return None
            
        except Exception as e:
            logger.error(f"❌ Error retrieving contract for account {account_id}: {e}")
            return None
    
    async def get_contract_by_id(self, contract_id: str) -> Optional[Dict[str, Any]]:
        """Get contract by contract ID"""
        try:
            contract = self.contracts_collection.find_one({"contract_id": contract_id})
            if contract:
                contract['_id'] = str(contract['_id'])
                return contract
            return None
            
        except Exception as e:
            logger.error(f"❌ Error retrieving contract {contract_id}: {e}")
            return None
    
    async def update_contract(self, account_id: str, update_data: Dict[str, Any]) -> bool:
        """Update contract by account ID"""
        try:
            # Add updated timestamp
            update_data['updated_at'] = datetime.utcnow()
            
            result = self.contracts_collection.update_one(
                {"account_id": account_id},
                {"$set": update_data}
            )
            
            if result.modified_count > 0:
                logger.info(f"✅ Contract updated successfully for account: {account_id}")
                return True
            else:
                logger.warning(f"⚠️ No contract found to update for account: {account_id}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error updating contract for account {account_id}: {e}")
            return False
    
    async def get_contracts_by_status(self, status: ContractStatus) -> List[Dict[str, Any]]:
        """Get all contracts by status"""
        try:
            contracts = list(self.contracts_collection.find({"status": status}))
            
            # Convert ObjectIds to strings
            for contract in contracts:
                contract['_id'] = str(contract['_id'])
            
            logger.info(f"✅ Retrieved {len(contracts)} contracts with status: {status}")
            return contracts
            
        except Exception as e:
            logger.error(f"❌ Error retrieving contracts with status {status}: {e}")
            return []
    
    async def get_expiring_contracts(self, days_ahead: int = 30) -> List[Dict[str, Any]]:
        """Get contracts expiring within specified days"""
        try:
            future_date = datetime.utcnow() + timedelta(days=days_ahead)
            
            contracts = list(self.contracts_collection.find({
                "status": ContractStatus.ACTIVE,
                "end_date": {"$lte": future_date}
            }))
            
            # Convert ObjectIds to strings
            for contract in contracts:
                contract['_id'] = str(contract['_id'])
            
            logger.info(f"✅ Retrieved {len(contracts)} contracts expiring within {days_ahead} days")
            return contracts
            
        except Exception as e:
            logger.error(f"❌ Error retrieving expiring contracts: {e}")
            return []
    
    async def get_contracts_by_type(self, contract_type: ContractType) -> List[Dict[str, Any]]:
        """Get all contracts by type"""
        try:
            contracts = list(self.contracts_collection.find({"contract_type": contract_type}))
            
            # Convert ObjectIds to strings
            for contract in contracts:
                contract['_id'] = str(contract['_id'])
            
            logger.info(f"✅ Retrieved {len(contracts)} contracts of type: {contract_type}")
            return contracts
            
        except Exception as e:
            logger.error(f"❌ Error retrieving contracts of type {contract_type}: {e}")
            return []
    
    async def delete_contract(self, account_id: str) -> bool:
        """Delete contract by account ID"""
        try:
            result = self.contracts_collection.delete_one({"account_id": account_id})
            
            if result.deleted_count > 0:
                logger.info(f"✅ Contract deleted successfully for account: {account_id}")
                return True
            else:
                logger.warning(f"⚠️ No contract found to delete for account: {account_id}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error deleting contract for account {account_id}: {e}")
            return False
    
    async def get_contract_count(self) -> int:
        """Get total number of contracts"""
        try:
            count = self.contracts_collection.count_documents({})
            return count
        except Exception as e:
            logger.error(f"❌ Error getting contract count: {e}")
            return 0


# Contract schema templates
def create_basic_contract_template(account_id: str) -> Dict[str, Any]:
    """Create a basic contract template"""
    return {
        "contract_id": None,  # Will be generated
        "account_id": account_id,
        "contract_type": ContractType.BASIC,
        "status": ContractStatus.ACTIVE,
        
        # Contract Period
        "start_date": datetime.utcnow(),
        "end_date": datetime.utcnow() + timedelta(days=365),
        "renewal_date": datetime.utcnow() + timedelta(days=335),  # 30 days before end
        "auto_renewal": True,
        
        # Financial Terms
        "base_monthly_fee": 99.00,
        "usage_based_pricing": {
            "trade_volume_tiers": [
                {"min_trades": 0, "max_trades": 1000, "price_per_trade": 0.10},
                {"min_trades": 1001, "max_trades": 5000, "price_per_trade": 0.08},
                {"min_trades": 5001, "max_trades": None, "price_per_trade": 0.05}
            ],
            "trade_value_tiers": [
                {"min_value": 0, "max_value": 10000, "percentage_fee": 0.5},
                {"min_value": 10001, "max_value": 50000, "percentage_fee": 0.3},
                {"min_value": 50001, "max_value": None, "percentage_fee": 0.2}
            ]
        },
        
        # Usage Limits
        "usage_limits": {
            "max_monthly_trades": 10000,
            "max_trade_value": 100000,
            "max_concurrent_trades": 10,
            "sla_threshold_seconds": 23
        },
        
        # Contact Information
        "primary_contact": {
            "name": "Primary Contact",
            "email": f"contact@{account_id}.com",
            "phone": "+1-555-0123",
            "role": "Account Manager"
        },
        "billing_contact": {
            "name": "Billing Contact",
            "email": f"billing@{account_id}.com",
            "phone": "+1-555-0124"
        },
        
        # Features
        "features": ["basic_analytics", "email_support"],
        "add_ons": [],
        
        # SLA Terms
        "sla_terms": {
            "uptime_guarantee": 99.5,
            "response_time_guarantee": 23,
            "penalty_terms": "Service credits for SLA violations"
        },
        
        # Metadata
        "tags": ["basic", "new_customer"],
        "notes": "Basic plan for new customers",
        "version": 1
    }


def create_professional_contract_template(account_id: str) -> Dict[str, Any]:
    """Create a professional contract template"""
    template = create_basic_contract_template(account_id)
    template.update({
        "contract_type": ContractType.PROFESSIONAL,
        "base_monthly_fee": 299.00,
        "usage_based_pricing": {
            "trade_volume_tiers": [
                {"min_trades": 0, "max_trades": 5000, "price_per_trade": 0.08},
                {"min_trades": 5001, "max_trades": 20000, "price_per_trade": 0.06},
                {"min_trades": 20001, "max_trades": None, "price_per_trade": 0.04}
            ],
            "trade_value_tiers": [
                {"min_value": 0, "max_value": 50000, "percentage_fee": 0.3},
                {"min_value": 50001, "max_value": 200000, "percentage_fee": 0.2},
                {"min_value": 200001, "max_value": None, "percentage_fee": 0.15}
            ]
        },
        "usage_limits": {
            "max_monthly_trades": 50000,
            "max_trade_value": 500000,
            "max_concurrent_trades": 25,
            "sla_threshold_seconds": 20
        },
        "features": ["advanced_analytics", "priority_support", "custom_dashboards", "api_access"],
        "add_ons": [
            {"name": "dedicated_support", "monthly_fee": 100.00, "active": False},
            {"name": "custom_integrations", "monthly_fee": 200.00, "active": False}
        ],
        "sla_terms": {
            "uptime_guarantee": 99.8,
            "response_time_guarantee": 20,
            "penalty_terms": "Service credits and priority support for SLA violations"
        },
        "tags": ["professional", "growing_customer"],
        "notes": "Professional plan for growing businesses"
    })
    return template


def create_enterprise_contract_template(account_id: str) -> Dict[str, Any]:
    """Create an enterprise contract template"""
    template = create_basic_contract_template(account_id)
    template.update({
        "contract_type": ContractType.ENTERPRISE,
        "base_monthly_fee": 999.00,
        "usage_based_pricing": {
            "trade_volume_tiers": [
                {"min_trades": 0, "max_trades": 10000, "price_per_trade": 0.05},
                {"min_trades": 10001, "max_trades": 50000, "price_per_trade": 0.04},
                {"min_trades": 50001, "max_trades": None, "price_per_trade": 0.03}
            ],
            "trade_value_tiers": [
                {"min_value": 0, "max_value": 100000, "percentage_fee": 0.2},
                {"min_value": 100001, "max_value": 500000, "percentage_fee": 0.15},
                {"min_value": 500001, "max_value": None, "percentage_fee": 0.1}
            ]
        },
        "usage_limits": {
            "max_monthly_trades": 100000,
            "max_trade_value": 1000000,
            "max_concurrent_trades": 100,
            "sla_threshold_seconds": 15
        },
        "features": [
            "enterprise_analytics", 
            "dedicated_support", 
            "custom_integrations", 
            "api_access", 
            "white_label_solutions",
            "advanced_security",
            "compliance_reporting"
        ],
        "add_ons": [
            {"name": "custom_development", "monthly_fee": 500.00, "active": False},
            {"name": "on_premise_deployment", "monthly_fee": 1000.00, "active": False}
        ],
        "sla_terms": {
            "uptime_guarantee": 99.9,
            "response_time_guarantee": 15,
            "penalty_terms": "Service credits, dedicated support, and SLA guarantees"
        },
        "tags": ["enterprise", "high_value"],
        "notes": "Enterprise plan for high-volume traders"
    })
    return template


# Global MongoDB manager instance
mongo_manager: Optional[MongoDBManager] = None


async def initialize_mongodb(connection_string: str) -> bool:
    """Initialize MongoDB connection"""
    global mongo_manager
    
    mongo_manager = MongoDBManager(connection_string)
    return await mongo_manager.connect()


async def get_mongo_manager() -> Optional[MongoDBManager]:
    """Get the global MongoDB manager instance"""
    return mongo_manager


# Example usage functions
async def create_sample_contracts():
    """Create sample contracts for testing"""
    if not mongo_manager:
        logger.error("MongoDB not initialized")
        return
    
    # Create sample contracts
    sample_accounts = ["12345", "67890", "11111", "22222", "33333"]
    
    for i, account_id in enumerate(sample_accounts):
        if i == 0:
            template = create_basic_contract_template(account_id)
        elif i == 1:
            template = create_professional_contract_template(account_id)
        else:
            template = create_enterprise_contract_template(account_id)
        
        # Add some variation
        template["primary_contact"]["name"] = f"Contact {i+1}"
        template["primary_contact"]["email"] = f"contact{i+1}@company{i+1}.com"
        
        contract_id = await mongo_manager.create_contract(template)
        if contract_id:
            logger.info(f"Created sample contract for account {account_id}")


if __name__ == "__main__":
    # Test the MongoDB integration
    async def test_mongodb():
        # Initialize MongoDB
        connection_string = "mongodb+srv://pbanavara:XTOpPHXOfTmGCsgS@cluster0.bljn2lo.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
        
        success = await initialize_mongodb(connection_string)
        if not success:
            logger.error("Failed to initialize MongoDB")
            return
        
        # Create sample contracts
        await create_sample_contracts()
        
        # Test queries
        contracts = await mongo_manager.get_contracts_by_status(ContractStatus.ACTIVE)
        logger.info(f"Found {len(contracts)} active contracts")
        
        # Test getting specific contract
        contract = await mongo_manager.get_contract_by_account_id("12345")
        if contract:
            logger.info(f"Retrieved contract: {contract['contract_id']}")
        
        # Disconnect
        await mongo_manager.disconnect()
    
    # Run the test
    asyncio.run(test_mongodb())
