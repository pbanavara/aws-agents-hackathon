#!/usr/bin/env python3
"""
Bulk Contract Creation Script
Creates 100 contracts with varied data for testing
"""

import asyncio
import random
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any
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

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def generate_company_names() -> List[str]:
    """Generate a list of company names"""
    companies = [
        "TechCorp", "DataFlow", "CloudSync", "DigitalEdge", "SmartTrade", "FutureTech", "InnovateLab",
        "CyberNet", "QuantumSoft", "ByteBridge", "NetFlow", "CodeCraft", "DevOps Inc", "AgileWorks",
        "Scalable Solutions", "MicroServices", "API Gateway", "Database Pro", "Security First", "Cloud Native",
        "Serverless Co", "Container Tech", "Kubernetes Pro", "Docker Solutions", "DevOps Pro", "CI/CD Experts",
        "Test Automation", "Quality Assurance", "Performance Lab", "Load Testing", "Stress Testing", "Security Testing",
        "Penetration Testing", "Vulnerability Assessment", "Risk Management", "Compliance Pro", "Audit Services",
        "Governance Tech", "Policy Management", "Access Control", "Identity Management", "Single Sign-On",
        "Multi-Factor Auth", "Zero Trust", "Network Security", "Firewall Pro", "Intrusion Detection", "Threat Intelligence",
        "Malware Analysis", "Forensic Services", "Incident Response", "Disaster Recovery", "Business Continuity",
        "Backup Solutions", "Data Recovery", "Archive Services", "Storage Management", "Capacity Planning",
        "Resource Optimization", "Cost Management", "Budget Control", "Financial Planning", "ROI Analysis",
        "Business Intelligence", "Data Analytics", "Machine Learning", "Artificial Intelligence", "Deep Learning",
        "Neural Networks", "Computer Vision", "Natural Language Processing", "Speech Recognition", "Text Analysis",
        "Sentiment Analysis", "Predictive Analytics", "Statistical Modeling", "Data Mining", "Pattern Recognition",
        "Anomaly Detection", "Fraud Detection", "Credit Scoring", "Risk Assessment", "Portfolio Management",
        "Trading Algorithms", "Market Analysis", "Financial Modeling", "Valuation Services", "Merger Analysis",
        "Acquisition Support", "Due Diligence", "Legal Tech", "Contract Management", "Document Processing",
        "Workflow Automation", "Process Optimization", "Business Process Management", "Enterprise Architecture",
        "System Integration", "API Development", "Web Services", "Mobile Development", "Cross-Platform Apps",
        "Native Development", "UI/UX Design", "User Experience", "Customer Journey", "Conversion Optimization",
        "A/B Testing", "Conversion Rate Optimization", "Search Engine Optimization", "Digital Marketing",
        "Content Marketing", "Social Media Management", "Email Marketing", "Marketing Automation", "Lead Generation"
    ]
    return companies


def generate_contact_names() -> List[str]:
    """Generate a list of contact names"""
    first_names = [
        "John", "Jane", "Michael", "Sarah", "David", "Emily", "Robert", "Jessica", "William", "Ashley",
        "James", "Amanda", "Christopher", "Stephanie", "Daniel", "Nicole", "Matthew", "Elizabeth", "Anthony", "Helen",
        "Mark", "Deborah", "Donald", "Lisa", "Steven", "Nancy", "Paul", "Karen", "Andrew", "Betty",
        "Joshua", "Sandra", "Kenneth", "Donna", "Kevin", "Carol", "Brian", "Ruth", "George", "Sharon",
        "Timothy", "Michelle", "Ronald", "Laura", "Jason", "Emily", "Edward", "Deborah", "Jeffrey", "Dorothy",
        "Ryan", "Lisa", "Jacob", "Nancy", "Gary", "Karen", "Nicholas", "Betty", "Eric", "Helen",
        "Jonathan", "Sandra", "Stephen", "Donna", "Larry", "Carol", "Justin", "Ruth", "Scott", "Julie",
        "Brandon", "Joyce", "Benjamin", "Virginia", "Samuel", "Victoria", "Frank", "Kelly", "Gregory", "Lauren",
        "Raymond", "Christine", "Alexander", "Amber", "Patrick", "Megan", "Jack", "Danielle", "Dennis", "Brittany",
        "Jerry", "Diana", "Tyler", "Natalie", "Aaron", "Samantha", "Jose", "Christina", "Adam", "Heather"
    ]
    
    last_names = [
        "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez",
        "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin",
        "Lee", "Perez", "Thompson", "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson",
        "Walker", "Young", "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores",
        "Green", "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell", "Carter", "Roberts",
        "Gomez", "Phillips", "Evans", "Turner", "Diaz", "Parker", "Cruz", "Edwards", "Collins", "Reyes",
        "Stewart", "Morris", "Morales", "Murphy", "Cook", "Rogers", "Gutierrez", "Ortiz", "Morgan", "Cooper",
        "Peterson", "Bailey", "Reed", "Kelly", "Howard", "Ramos", "Kim", "Cox", "Ward", "Richardson",
        "Watson", "Brooks", "Chavez", "Wood", "James", "Bennett", "Gray", "Mendoza", "Ruiz", "Hughes",
        "Price", "Alvarez", "Castillo", "Sanders", "Patel", "Myers", "Long", "Ross", "Foster", "Jimenez"
    ]
    
    contacts = []
    for first in first_names:
        for last in last_names:
            contacts.append(f"{first} {last}")
            if len(contacts) >= 100:
                return contacts
    return contacts


def generate_contract_data(account_id: str, company_name: str, contact_name: str, contract_type: ContractType) -> Dict[str, Any]:
    """Generate contract data with realistic variations"""
    
    # Base template based on contract type
    if contract_type == ContractType.BASIC:
        template = create_basic_contract_template(account_id)
    elif contract_type == ContractType.PROFESSIONAL:
        template = create_professional_contract_template(account_id)
    else:
        template = create_enterprise_contract_template(account_id)
    
    # Add company-specific data
    template["company_name"] = company_name
    template["account_id"] = account_id
    
    # Vary contract dates
    start_date = datetime.utcnow() - timedelta(days=random.randint(0, 365))
    end_date = start_date + timedelta(days=random.randint(180, 730))  # 6 months to 2 years
    renewal_date = end_date - timedelta(days=random.randint(15, 45))
    
    template["start_date"] = start_date
    template["end_date"] = end_date
    template["renewal_date"] = renewal_date
    
    # Vary status
    if random.random() < 0.8:  # 80% active
        template["status"] = ContractStatus.ACTIVE
    elif random.random() < 0.5:
        template["status"] = ContractStatus.PENDING_RENEWAL
    else:
        template["status"] = ContractStatus.EXPIRED
    
    # Vary pricing slightly
    price_variation = random.uniform(0.8, 1.2)  # ±20% variation
    template["base_monthly_fee"] = round(template["base_monthly_fee"] * price_variation, 2)
    
    # Update contact information
    template["primary_contact"]["name"] = contact_name
    template["primary_contact"]["email"] = f"{contact_name.lower().replace(' ', '.')}@{company_name.lower().replace(' ', '')}.com"
    template["primary_contact"]["phone"] = f"+1-555-{random.randint(100, 999)}-{random.randint(1000, 9999)}"
    
    template["billing_contact"]["name"] = f"Billing {contact_name.split()[0]}"
    template["billing_contact"]["email"] = f"billing@{company_name.lower().replace(' ', '')}.com"
    template["billing_contact"]["phone"] = f"+1-555-{random.randint(100, 999)}-{random.randint(1000, 9999)}"
    
    # Add some random features
    additional_features = [
        "custom_reporting", "data_export", "api_access", "webhook_integration", 
        "sso_integration", "audit_logs", "backup_services", "priority_support",
        "dedicated_account_manager", "custom_integrations", "white_labeling",
        "advanced_analytics", "predictive_modeling", "machine_learning", "ai_features"
    ]
    
    if contract_type != ContractType.BASIC:
        num_additional = random.randint(1, 3)
        selected_features = random.sample(additional_features, num_additional)
        template["features"].extend(selected_features)
    
    # Add tags
    template["tags"] = [
        contract_type.value,
        "bulk_created",
        f"created_{datetime.utcnow().strftime('%Y%m')}",
        random.choice(["new_customer", "existing_customer", "upgraded_customer"])
    ]
    
    # Add notes
    template["notes"] = f"Bulk created contract for {company_name}. Contact: {contact_name}"
    
    return template


async def create_bulk_contracts(num_contracts: int = 100):
    """Create bulk contracts"""
    print(f"🚀 Creating {num_contracts} contracts...")
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
    
    # Generate data
    companies = generate_company_names()
    contacts = generate_contact_names()
    
    # Contract type distribution
    contract_types = [ContractType.BASIC, ContractType.PROFESSIONAL, ContractType.ENTERPRISE]
    type_weights = [0.4, 0.4, 0.2]  # 40% basic, 40% professional, 20% enterprise
    
    created_count = 0
    failed_count = 0
    
    for i in range(num_contracts):
        try:
            # Generate account ID
            account_id = f"account_{i+1:06d}"
            
            # Select company and contact
            company_name = companies[i % len(companies)]
            contact_name = contacts[i % len(contacts)]
            
            # Select contract type based on weights
            contract_type = random.choices(contract_types, weights=type_weights)[0]
            
            # Generate contract data
            contract_data = generate_contract_data(account_id, company_name, contact_name, contract_type)
            
            # Create contract
            contract_id = await mongo_manager.create_contract(contract_data)
            
            if contract_id:
                created_count += 1
                if created_count % 10 == 0:
                    print(f"✅ Created {created_count} contracts...")
            else:
                failed_count += 1
                print(f"❌ Failed to create contract for {account_id}")
                
        except Exception as e:
            failed_count += 1
            print(f"❌ Error creating contract {i+1}: {e}")
    
    # Summary
    print("\n📊 Bulk Contract Creation Summary")
    print("=" * 40)
    print(f"✅ Successfully created: {created_count} contracts")
    print(f"❌ Failed to create: {failed_count} contracts")
    print(f"📈 Success rate: {(created_count / num_contracts) * 100:.1f}%")
    
    # Show some statistics
    if created_count > 0:
        print("\n📋 Contract Statistics:")
        
        # Count by type
        basic_contracts = await mongo_manager.get_contracts_by_type(ContractType.BASIC)
        professional_contracts = await mongo_manager.get_contracts_by_type(ContractType.PROFESSIONAL)
        enterprise_contracts = await mongo_manager.get_contracts_by_type(ContractType.ENTERPRISE)
        
        print(f"   Basic contracts: {len(basic_contracts)}")
        print(f"   Professional contracts: {len(professional_contracts)}")
        print(f"   Enterprise contracts: {len(enterprise_contracts)}")
        
        # Count by status
        active_contracts = await mongo_manager.get_contracts_by_status(ContractStatus.ACTIVE)
        pending_contracts = await mongo_manager.get_contracts_by_status(ContractStatus.PENDING_RENEWAL)
        expired_contracts = await mongo_manager.get_contracts_by_status(ContractStatus.EXPIRED)
        
        print(f"   Active contracts: {len(active_contracts)}")
        print(f"   Pending renewal: {len(pending_contracts)}")
        print(f"   Expired contracts: {len(expired_contracts)}")
        
        # Total contracts
        total_contracts = await mongo_manager.get_contract_count()
        print(f"   Total contracts in database: {total_contracts}")
    
    # Disconnect
    await mongo_manager.disconnect()
    print("\n✅ Bulk contract creation completed!")


async def cleanup_bulk_contracts():
    """Clean up bulk created contracts"""
    print("🧹 Cleaning up bulk created contracts...")
    
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
    
    # Get all contracts with bulk_created tag
    all_contracts = list(mongo_manager.contracts_collection.find({"tags": "bulk_created"}))
    
    deleted_count = 0
    for contract in all_contracts:
        try:
            account_id = contract.get('account_id')
            if account_id:
                success = await mongo_manager.delete_contract(account_id)
                if success:
                    deleted_count += 1
        except Exception as e:
            print(f"❌ Error deleting contract {contract.get('account_id')}: {e}")
    
    print(f"✅ Deleted {deleted_count} bulk created contracts")
    
    # Disconnect
    await mongo_manager.disconnect()


async def main():
    """Main function"""
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "create":
            num_contracts = int(sys.argv[2]) if len(sys.argv) > 2 else 100
            await create_bulk_contracts(num_contracts)
        elif command == "cleanup":
            await cleanup_bulk_contracts()
        else:
            print("Usage: python create_bulk_contracts.py [create|cleanup] [number]")
    else:
        # Default: create 100 contracts
        await create_bulk_contracts(100)


if __name__ == "__main__":
    asyncio.run(main()) 