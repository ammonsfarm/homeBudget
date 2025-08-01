"""
SimpleFIN API Integration Service

Handles authentication and data retrieval from SimpleFIN Bridge API
according to the SimpleFIN protocol specification.
"""

import base64
import httpx
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from decimal import Decimal

logger = logging.getLogger(__name__)

class SimpleFINError(Exception):
    """Custom exception for SimpleFIN API errors"""
    pass

class SimpleFINService:
    """Service for integrating with SimpleFIN Bridge API"""
    
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    def decode_setup_token(self, setup_token: str) -> str:
        """
        Decode base64 setup token to get claim URL
        
        Args:
            setup_token: Base64 encoded setup token from SimpleFIN
            
        Returns:
            Decoded claim URL
        """
        try:
            claim_url = base64.b64decode(setup_token).decode('utf-8')
            return claim_url
        except Exception as e:
            raise SimpleFINError(f"Failed to decode setup token: {str(e)}")
    
    async def exchange_setup_token(self, setup_token: str) -> str:
        """
        Exchange setup token for access URL
        
        Args:
            setup_token: Base64 encoded setup token
            
        Returns:
            Access URL for future API calls
        """
        try:
            claim_url = self.decode_setup_token(setup_token)
            
            # POST to claim URL with empty body
            response = await self.client.post(
                claim_url,
                headers={"Content-Length": "0"}
            )
            
            if response.status_code != 200:
                raise SimpleFINError(f"Failed to claim token: {response.status_code} - {response.text}")
            
            access_url = response.text.strip()
            return access_url
            
        except httpx.RequestError as e:
            raise SimpleFINError(f"Network error during token exchange: {str(e)}")
        except Exception as e:
            raise SimpleFINError(f"Unexpected error during token exchange: {str(e)}")
    
    async def get_accounts(self, access_url: str) -> Dict[str, Any]:
        """
        Fetch account data from SimpleFIN API
        
        Args:
            access_url: Access URL obtained from token exchange
            
        Returns:
            Account data including transactions
        """
        try:
            accounts_url = f"{access_url}/accounts"
            
            response = await self.client.get(accounts_url)
            
            if response.status_code != 200:
                raise SimpleFINError(f"Failed to fetch accounts: {response.status_code} - {response.text}")
            
            data = response.json()
            
            if data.get('errors'):
                raise SimpleFINError(f"API returned errors: {data['errors']}")
            
            return data
            
        except httpx.RequestError as e:
            raise SimpleFINError(f"Network error fetching accounts: {str(e)}")
        except Exception as e:
            raise SimpleFINError(f"Unexpected error fetching accounts: {str(e)}")
    
    def parse_transactions(self, accounts_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Parse transactions from SimpleFIN accounts data
        
        Args:
            accounts_data: Raw accounts data from SimpleFIN API
            
        Returns:
            List of parsed transaction dictionaries
        """
        transactions = []
        
        for account in accounts_data.get('accounts', []):
            account_id = account.get('id')
            account_name = account.get('name')
            org_name = account.get('org', {}).get('name', account.get('org', {}).get('domain', ''))
            
            for txn in account.get('transactions', []):
                try:
                    # Parse transaction data
                    parsed_txn = {
                        'external_id': txn.get('id'),
                        'account_id': account_id,
                        'account_name': account_name,
                        'organization': org_name,
                        'description': txn.get('description', ''),
                        'amount': Decimal(str(txn.get('amount', '0'))),
                        'date': datetime.fromtimestamp(txn.get('posted', 0)),
                        'pending': txn.get('pending', False),
                        'category': txn.get('extra', {}).get('category'),
                        'raw_data': txn  # Store original data for reference
                    }
                    
                    transactions.append(parsed_txn)
                    
                except Exception as e:
                    logger.warning(f"Failed to parse transaction {txn.get('id', 'unknown')}: {str(e)}")
                    continue
        
        return transactions
    
    async def sync_user_transactions(self, access_url: str) -> List[Dict[str, Any]]:
        """
        Complete sync process: fetch accounts and parse transactions
        
        Args:
            access_url: Access URL for SimpleFIN API
            
        Returns:
            List of parsed transactions ready for database storage
        """
        try:
            # Fetch account data
            accounts_data = await self.get_accounts(access_url)
            
            # Parse transactions
            transactions = self.parse_transactions(accounts_data)
            
            logger.info(f"Successfully synced {len(transactions)} transactions from SimpleFIN")
            
            return transactions
            
        except Exception as e:
            logger.error(f"Failed to sync transactions: {str(e)}")
            raise

# Example usage and testing
async def test_simplefin_integration():
    """Test function for SimpleFIN integration"""
    
    # Demo token from SimpleFIN docs (refresh page to get new one)
    demo_token = "aHR0cHM6Ly9iZXRhLWJyaWRnZS5zaW1wbGVmaW4ub3JnL3NpbXBsZWZpbi9jbGFpbS9ERU1PLXYyLTYwMUM1QUVCN0RDNDNERjNGREI1"
    
    async with SimpleFINService() as service:
        try:
            # Exchange setup token for access URL
            access_url = await service.exchange_setup_token(demo_token)
            print(f"Access URL: {access_url}")
            
            # Fetch and parse transactions
            transactions = await service.sync_user_transactions(access_url)
            print(f"Found {len(transactions)} transactions")
            
            # Print first few transactions
            for txn in transactions[:3]:
                print(f"  {txn['date']}: {txn['description']} - ${txn['amount']}")
                
        except SimpleFINError as e:
            print(f"SimpleFIN Error: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_simplefin_integration())
