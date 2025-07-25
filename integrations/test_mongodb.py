#!/usr/bin/env python3
"""
Test script for MongoDB Contract Integration
Demonstrates all contract operations
"""

import asyncio
import json
from datetime import datetime, timedelta
from mongo_db import (
    MongoDBManager, 
    initialize_mongodb, 
    get_mongo_manager,
    ContractType, 
    ContractStatus,
    create_basic_contract_template,
    create_professional_contract_template,
    create_enterprise_contract_template
)


async def test_contract_operations():
    """Test all contract operations"""
    print("🧪 MongoDB Contract Integration Test")
    print("=" * 50)
    
    # Initialize MongoDB
    connection_string = "mongodb+srv://pbanavara:XTOpPHXOfTmGCsgS@cluster0.bljn2lo.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    
    success = await initialize_mongodb(connection_string)
    if not success:
        print("❌ Failed to initialize MongoDB")
        return
    
    mongo_manager = await get_mongo_manager()
    if not mongo_manager:
        print("❌ MongoDB manager not available")
        return
    
    print("✅ MongoDB connected successfully")
    
    # Test 1: Create contracts
    print("\n📝 Test 1: Creating Contracts")
    print("-" * 30)
    
    test_accounts = ["test_account_001", "test_account_002", "test_account_003"]
    contract_ids = []
    
    for i, account_id in enumerate(test_accounts):
        if i == 0:
            template = create_basic_contract_template(account_id)
        elif i == 1:
            template = create_professional_contract_template(account_id)
        else:
            template = create_enterprise_contract_template(account_id)
        
        # Customize contact info
        template["primary_contact"]["name"] = f"Test Contact {i+1}"
        template["primary_contact"]["email"] = f"contact{i+1}@testcompany{i+1}.com"
        
        contract_id = await mongo_manager.create_contract(template)
        if contract_id:
            contract_ids.append(contract_id)
            print(f"✅ Created {template['contract_type']} contract for {account_id}")
        else:
            print(f"❌ Failed to create contract for {account_id}")
    
    # Test 2: Retrieve contracts
    print("\n🔍 Test 2: Retrieving Contracts")
    print("-" * 30)
    
    for account_id in test_accounts:
        contract = await mongo_manager.get_contract_by_account_id(account_id)
        if contract:
            print(f"✅ Retrieved contract for {account_id}:")
            print(f"   Type: {contract['contract_type']}")
            print(f"   Status: {contract['status']}")
            print(f"   Monthly Fee: ${contract['base_monthly_fee']}")
            print(f"   Features: {len(contract['features'])} features")
        else:
            print(f"❌ No contract found for {account_id}")
    
    # Test 3: Update contract
    print("\n✏️ Test 3: Updating Contract")
    print("-" * 30)
    
    update_data = {
        "base_monthly_fee": 399.00,
        "features": ["advanced_analytics", "priority_support", "custom_dashboards", "api_access", "new_feature"],
        "notes": "Updated with new features and pricing"
    }
    
    success = await mongo_manager.update_contract("test_account_002", update_data)
    if success:
        print("✅ Contract updated successfully")
        
        # Verify update
        updated_contract = await mongo_manager.get_contract_by_account_id("test_account_002")
        if updated_contract:
            print(f"   New monthly fee: ${updated_contract['base_monthly_fee']}")
            print(f"   Updated features: {len(updated_contract['features'])} features")
    else:
        print("❌ Failed to update contract")
    
    # Test 4: Query by status
    print("\n📊 Test 4: Querying by Status")
    print("-" * 30)
    
    active_contracts = await mongo_manager.get_contracts_by_status(ContractStatus.ACTIVE)
    print(f"✅ Found {len(active_contracts)} active contracts")
    
    for contract in active_contracts:
        print(f"   {contract['account_id']}: {contract['contract_type']} - ${contract['base_monthly_fee']}")
    
    # Test 5: Query by type
    print("\n🏷️ Test 5: Querying by Type")
    print("-" * 30)
    
    enterprise_contracts = await mongo_manager.get_contracts_by_type(ContractType.ENTERPRISE)
    print(f"✅ Found {len(enterprise_contracts)} enterprise contracts")
    
    professional_contracts = await mongo_manager.get_contracts_by_type(ContractType.PROFESSIONAL)
    print(f"✅ Found {len(professional_contracts)} professional contracts")
    
    basic_contracts = await mongo_manager.get_contracts_by_type(ContractType.BASIC)
    print(f"✅ Found {len(basic_contracts)} basic contracts")
    
    # Test 6: Expiring contracts
    print("\n⏰ Test 6: Expiring Contracts")
    print("-" * 30)
    
    expiring_contracts = await mongo_manager.get_expiring_contracts(days_ahead=365)
    print(f"✅ Found {len(expiring_contracts)} contracts expiring within 365 days")
    
    for contract in expiring_contracts:
        end_date = contract['end_date']
        days_until_expiry = (end_date - datetime.utcnow()).days
        print(f"   {contract['account_id']}: expires in {days_until_expiry} days")
    
    # Test 7: Contract count
    print("\n📈 Test 7: Contract Statistics")
    print("-" * 30)
    
    total_contracts = await mongo_manager.get_contract_count()
    print(f"✅ Total contracts in database: {total_contracts}")
    
    # Test 8: Contract details
    print("\n📋 Test 8: Contract Details")
    print("-" * 30)
    
    contract = await mongo_manager.get_contract_by_account_id("test_account_003")
    if contract:
        print("Enterprise Contract Details:")
        print(f"   Contract ID: {contract['contract_id']}")
        print(f"   Account ID: {contract['account_id']}")
        print(f"   Type: {contract['contract_type']}")
        print(f"   Status: {contract['status']}")
        print(f"   Monthly Fee: ${contract['base_monthly_fee']}")
        print(f"   Start Date: {contract['start_date']}")
        print(f"   End Date: {contract['end_date']}")
        print(f"   Auto Renewal: {contract['auto_renewal']}")
        print(f"   Features: {', '.join(contract['features'])}")
        print(f"   SLA Threshold: {contract['usage_limits']['sla_threshold_seconds']} seconds")
        print(f"   Primary Contact: {contract['primary_contact']['name']} ({contract['primary_contact']['email']})")
    
    # Test 9: Cleanup (optional)
    print("\n🧹 Test 9: Cleanup")
    print("-" * 30)
    
    cleanup = input("Do you want to delete test contracts? (y/N): ").lower().strip()
    if cleanup == 'y':
        for account_id in test_accounts:
            success = await mongo_manager.delete_contract(account_id)
            if success:
                print(f"✅ Deleted contract for {account_id}")
            else:
                print(f"❌ Failed to delete contract for {account_id}")
    else:
        print("Skipping cleanup - test contracts remain in database")
    
    # Disconnect
    await mongo_manager.disconnect()
    print("\n✅ MongoDB integration test completed successfully!")


async def test_contract_templates():
    """Test contract template creation"""
    print("\n📄 Contract Template Test")
    print("=" * 30)
    
    account_id = "template_test_account"
    
    # Test Basic template
    basic_template = create_basic_contract_template(account_id)
    print("✅ Basic Contract Template:")
    print(f"   Monthly Fee: ${basic_template['base_monthly_fee']}")
    print(f"   Features: {', '.join(basic_template['features'])}")
    print(f"   SLA Threshold: {basic_template['usage_limits']['sla_threshold_seconds']} seconds")
    
    # Test Professional template
    professional_template = create_professional_contract_template(account_id)
    print("\n✅ Professional Contract Template:")
    print(f"   Monthly Fee: ${professional_template['base_monthly_fee']}")
    print(f"   Features: {', '.join(professional_template['features'])}")
    print(f"   SLA Threshold: {professional_template['usage_limits']['sla_threshold_seconds']} seconds")
    
    # Test Enterprise template
    enterprise_template = create_enterprise_contract_template(account_id)
    print("\n✅ Enterprise Contract Template:")
    print(f"   Monthly Fee: ${enterprise_template['base_monthly_fee']}")
    print(f"   Features: {', '.join(enterprise_template['features'])}")
    print(f"   SLA Threshold: {enterprise_template['usage_limits']['sla_threshold_seconds']} seconds")


async def main():
    """Run all tests"""
    try:
        await test_contract_templates()
        await test_contract_operations()
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main()) 