# MongoDB Contract Integration

## Overview

The MongoDB integration provides a comprehensive contract management system for the EasyTrade platform. It stores all contract information in a MongoDB Atlas cluster and integrates seamlessly with the upsell workflow system.

## Architecture

```
Upsell Workflow → MongoDB Manager → MongoDB Atlas → Contracts Collection
```

## Database Schema

### Contracts Collection

The `contracts` collection stores all contract information with the following structure:

```json
{
  "_id": "ObjectId",
  "contract_id": "string",           // Unique contract identifier
  "account_id": "string",            // Account ID from usage metrics
  "contract_type": "enum",           // "basic", "professional", "enterprise", "custom"
  "status": "enum",                  // "active", "expired", "cancelled", "pending_renewal", "draft"
  
  // Contract Period
  "start_date": "ISODate",
  "end_date": "ISODate", 
  "renewal_date": "ISODate",
  "auto_renewal": "boolean",
  
  // Financial Terms
  "base_monthly_fee": "number",
  "usage_based_pricing": {
    "trade_volume_tiers": [
      {
        "min_trades": "number",
        "max_trades": "number", 
        "price_per_trade": "number"
      }
    ],
    "trade_value_tiers": [
      {
        "min_value": "number",
        "max_value": "number",
        "percentage_fee": "number"
      }
    ]
  },
  
  // Usage Limits & Thresholds
  "usage_limits": {
    "max_monthly_trades": "number",
    "max_trade_value": "number",
    "max_concurrent_trades": "number",
    "sla_threshold_seconds": "number"
  },
  
  // Contact Information
  "primary_contact": {
    "name": "string",
    "email": "string",
    "phone": "string",
    "role": "string"
  },
  "billing_contact": {
    "name": "string", 
    "email": "string",
    "phone": "string"
  },
  
  // Features & Add-ons
  "features": ["string"],
  "add_ons": [
    {
      "name": "string",
      "monthly_fee": "number",
      "active": "boolean"
    }
  ],
  
  // Performance & SLA
  "sla_terms": {
    "uptime_guarantee": "number",
    "response_time_guarantee": "number",
    "penalty_terms": "string"
  },
  
  // Audit Trail
  "created_at": "ISODate",
  "updated_at": "ISODate",
  "created_by": "string",
  "last_modified_by": "string",
  
  // Metadata
  "tags": ["string"],
  "notes": "string",
  "version": "number"
}
```

## Contract Types

### 1. Basic Contract
- **Monthly Fee**: $99.00
- **Features**: Basic analytics, email support
- **SLA Threshold**: 23 seconds
- **Usage Limits**: 10,000 trades/month, $100,000 max trade value

### 2. Professional Contract
- **Monthly Fee**: $299.00
- **Features**: Advanced analytics, priority support, custom dashboards, API access
- **SLA Threshold**: 20 seconds
- **Usage Limits**: 50,000 trades/month, $500,000 max trade value

### 3. Enterprise Contract
- **Monthly Fee**: $999.00
- **Features**: Enterprise analytics, dedicated support, custom integrations, white label solutions
- **SLA Threshold**: 15 seconds
- **Usage Limits**: 100,000 trades/month, $1,000,000 max trade value

## Usage

### 1. Installation

```bash
# Install dependencies
cd integrations
pip install -r requirements.txt
```

### 2. Initialize MongoDB Connection

```python
from mongo_db import initialize_mongodb, get_mongo_manager

# Initialize connection
connection_string = "mongodb+srv://pbanavara:XTOpPHXOfTmGCsgS@cluster0.bljn2lo.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
success = await initialize_mongodb(connection_string)

# Get manager instance
mongo_manager = await get_mongo_manager()
```

### 3. Create Contracts

```python
from mongo_db import create_basic_contract_template, create_professional_contract_template

# Create basic contract
basic_template = create_basic_contract_template("account_12345")
contract_id = await mongo_manager.create_contract(basic_template)

# Create professional contract
professional_template = create_professional_contract_template("account_67890")
contract_id = await mongo_manager.create_contract(professional_template)
```

### 4. Retrieve Contracts

```python
# Get contract by account ID
contract = await mongo_manager.get_contract_by_account_id("account_12345")

# Get contract by contract ID
contract = await mongo_manager.get_contract_by_id("contract_20240115_140000_abc123")

# Get contracts by status
active_contracts = await mongo_manager.get_contracts_by_status(ContractStatus.ACTIVE)

# Get contracts by type
enterprise_contracts = await mongo_manager.get_contracts_by_type(ContractType.ENTERPRISE)
```

### 5. Update Contracts

```python
# Update contract information
update_data = {
    "base_monthly_fee": 399.00,
    "features": ["advanced_analytics", "priority_support", "new_feature"],
    "notes": "Upgraded with new features"
}

success = await mongo_manager.update_contract("account_12345", update_data)
```

### 6. Query Operations

```python
# Get expiring contracts
expiring_contracts = await mongo_manager.get_expiring_contracts(days_ahead=30)

# Get contract count
total_contracts = await mongo_manager.get_contract_count()

# Delete contract
success = await mongo_manager.delete_contract("account_12345")
```

## Integration with Upsell Workflow

The MongoDB integration is automatically used by the upsell workflow:

```python
# In upsell_workflow.py - fetch_contract activity
@activity.defn
async def fetch_contract(account_id: str) -> ContractData:
    """Fetch current contract information for the account from MongoDB"""
    mongo_manager = await get_mongo_manager()
    contract = await mongo_manager.get_contract_by_account_id(account_id)
    
    if contract:
        # Convert MongoDB contract to ContractData
        return ContractData(
            account_id=contract.get('account_id'),
            current_plan=contract.get('contract_type'),
            contract_end_date=contract.get('end_date').isoformat(),
            # ... other fields
        )
```

## Database Indexes

The following indexes are automatically created for optimal performance:

1. **Unique Index**: `account_id` - Ensures one contract per account
2. **Index**: `status` - For filtering by contract status
3. **Index**: `end_date` - For renewal queries
4. **Compound Index**: `status + end_date` - For expiring contract queries
5. **Index**: `contract_type` - For plan-based queries

## Testing

### Run the Test Suite

```bash
cd integrations
python test_mongodb.py
```

The test suite covers:
- Contract creation with different templates
- Contract retrieval and updates
- Query operations by status and type
- Expiring contract detection
- Contract statistics
- Cleanup operations

### Test Output Example

```
🧪 MongoDB Contract Integration Test
==================================================
✅ MongoDB connected successfully

📝 Test 1: Creating Contracts
------------------------------
✅ Created basic contract for test_account_001
✅ Created professional contract for test_account_002
✅ Created enterprise contract for test_account_003

🔍 Test 2: Retrieving Contracts
------------------------------
✅ Retrieved contract for test_account_001:
   Type: basic
   Status: active
   Monthly Fee: $99.0
   Features: 2 features

📊 Test 4: Querying by Status
------------------------------
✅ Found 3 active contracts
   test_account_001: basic - $99.0
   test_account_002: professional - $299.0
   test_account_003: enterprise - $999.0
```

## Error Handling

The MongoDB integration includes comprehensive error handling:

- **Connection Failures**: Graceful fallback to mock data
- **Duplicate Keys**: Prevents duplicate contracts per account
- **Missing Data**: Provides default values for missing fields
- **Query Errors**: Logs errors and returns empty results

## Monitoring

### Logs
All operations are logged with appropriate levels:
- `INFO`: Successful operations
- `WARNING`: Non-critical issues (e.g., no contracts found)
- `ERROR`: Critical failures

### Metrics
- Contract count by type and status
- Expiring contracts within specified timeframes
- Database operation success rates

## Security

- **Connection String**: Uses MongoDB Atlas with SSL/TLS
- **Authentication**: Username/password authentication
- **Network Access**: IP whitelist recommended for production
- **Data Validation**: Input validation and sanitization

## Production Considerations

1. **Connection Pooling**: Configure appropriate connection pool size
2. **Index Optimization**: Monitor query performance and adjust indexes
3. **Backup Strategy**: Implement regular database backups
4. **Monitoring**: Set up alerts for connection failures and performance issues
5. **Scaling**: Consider read replicas for high-traffic scenarios

## Troubleshooting

### Common Issues

1. **Connection Failed**
   - Check network connectivity
   - Verify connection string
   - Ensure IP is whitelisted in MongoDB Atlas

2. **Duplicate Key Error**
   - Check if contract already exists for account
   - Use update operation instead of create

3. **Query Performance Issues**
   - Verify indexes are created
   - Check query patterns
   - Monitor database performance

### Debug Commands

```python
# Test connection
mongo_manager = await get_mongo_manager()
if mongo_manager:
    print("✅ MongoDB connected")
else:
    print("❌ MongoDB not available")

# Check contract count
count = await mongo_manager.get_contract_count()
print(f"Total contracts: {count}")

# List all active contracts
contracts = await mongo_manager.get_contracts_by_status(ContractStatus.ACTIVE)
for contract in contracts:
    print(f"{contract['account_id']}: {contract['contract_type']}")
```

## Future Enhancements

1. **Contract Versioning**: Track contract changes over time
2. **Bulk Operations**: Support for bulk contract creation/updates
3. **Advanced Queries**: Complex aggregation queries for analytics
4. **Caching**: Redis integration for frequently accessed contracts
5. **Audit Trail**: Detailed change tracking and history 