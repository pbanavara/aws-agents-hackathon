#!/usr/bin/env python3
"""
Simple MongoDB Connection Test
Helps diagnose connection issues
"""

import asyncio
import logging
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_basic_connection():
    """Test basic MongoDB connection"""
    print("🔍 Testing Basic MongoDB Connection")
    print("=" * 40)
    
    connection_string = "mongodb+srv://pbanavara:XTOpPHXOfTmGCsgS@cluster0.bljn2lo.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    
    try:
        print("Attempting connection...")
        client = MongoClient(connection_string)
        
        # Test connection
        client.admin.command('ping')
        print("✅ Basic connection successful!")
        
        # List databases
        databases = client.list_database_names()
        print(f"📊 Available databases: {databases}")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ Basic connection failed: {e}")
        return False


def test_ssl_connection():
    """Test MongoDB connection with SSL settings"""
    print("\n🔒 Testing SSL MongoDB Connection")
    print("=" * 40)
    
    connection_string = "mongodb+srv://pbanavara:XTOpPHXOfTmGCsgS@cluster0.bljn2lo.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    
    try:
        print("Attempting SSL connection...")
        client = MongoClient(
            connection_string,
            ssl=True,
            ssl_cert_reqs='CERT_NONE',
            serverSelectionTimeoutMS=30000,
            connectTimeoutMS=20000,
            socketTimeoutMS=20000
        )
        
        # Test connection
        client.admin.command('ping')
        print("✅ SSL connection successful!")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ SSL connection failed: {e}")
        return False


def test_connection_string_variations():
    """Test different connection string formats"""
    print("\n🔧 Testing Connection String Variations")
    print("=" * 40)
    
    base_connection = "mongodb+srv://pbanavara:XTOpPHXOfTmGCsgS@cluster0.bljn2lo.mongodb.net"
    
    variations = [
        f"{base_connection}/?retryWrites=true&w=majority",
        f"{base_connection}/?retryWrites=true&w=majority&ssl=true",
        f"{base_connection}/?retryWrites=true&w=majority&ssl=true&ssl_cert_reqs=CERT_NONE",
        f"{base_connection}/?retryWrites=true&w=majority&appName=Cluster0",
        f"{base_connection}/?retryWrites=true&w=majority&appName=Cluster0&ssl=true",
        f"{base_connection}/?retryWrites=true&w=majority&appName=Cluster0&ssl=true&ssl_cert_reqs=CERT_NONE"
    ]
    
    for i, conn_str in enumerate(variations, 1):
        try:
            print(f"Testing variation {i}...")
            client = MongoClient(conn_str, serverSelectionTimeoutMS=10000)
            client.admin.command('ping')
            print(f"✅ Variation {i} successful!")
            client.close()
            return conn_str
        except Exception as e:
            print(f"❌ Variation {i} failed: {str(e)[:100]}...")
            continue
    
    return None


def test_network_connectivity():
    """Test basic network connectivity"""
    print("\n🌐 Testing Network Connectivity")
    print("=" * 40)
    
    import socket
    
    # Test DNS resolution
    try:
        print("Testing DNS resolution...")
        ip = socket.gethostbyname("cluster0.bljn2lo.mongodb.net")
        print(f"✅ DNS resolution successful: {ip}")
    except Exception as e:
        print(f"❌ DNS resolution failed: {e}")
        return False
    
    # Test port connectivity
    try:
        print("Testing port connectivity...")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        result = sock.connect_ex(("cluster0.bljn2lo.mongodb.net", 27017))
        sock.close()
        
        if result == 0:
            print("✅ Port 27017 is reachable")
        else:
            print("❌ Port 27017 is not reachable")
            return False
    except Exception as e:
        print(f"❌ Port connectivity test failed: {e}")
        return False
    
    return True


def main():
    """Run all connection tests"""
    print("🧪 MongoDB Connection Diagnostic Tool")
    print("=" * 50)
    
    # Test network connectivity first
    if not test_network_connectivity():
        print("\n❌ Network connectivity issues detected. Please check your internet connection.")
        return
    
    # Test basic connection
    basic_success = test_basic_connection()
    
    # Test SSL connection
    ssl_success = test_ssl_connection()
    
    # Test connection string variations
    working_variation = test_connection_string_variations()
    
    # Summary
    print("\n📋 Connection Test Summary")
    print("=" * 30)
    print(f"Basic Connection: {'✅ Success' if basic_success else '❌ Failed'}")
    print(f"SSL Connection: {'✅ Success' if ssl_success else '❌ Failed'}")
    
    if working_variation:
        print(f"Working Variation: ✅ Found")
        print(f"Connection String: {working_variation}")
    else:
        print("Working Variation: ❌ None found")
    
    # Recommendations
    print("\n💡 Recommendations:")
    if basic_success:
        print("- Use the basic connection method")
    elif ssl_success:
        print("- Use the SSL connection method with CERT_NONE")
    elif working_variation:
        print(f"- Use the working connection string variation")
    else:
        print("- Check your MongoDB Atlas cluster status")
        print("- Verify your IP is whitelisted in MongoDB Atlas")
        print("- Check your network firewall settings")
        print("- Try using a VPN or different network")


if __name__ == "__main__":
    main() 