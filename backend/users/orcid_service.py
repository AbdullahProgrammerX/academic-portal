"""
ORCID OAuth2 integration service.

Handles ORCID authentication flow:
1. Authorization URL generation
2. Token exchange
3. User profile fetching
4. Token refresh
"""
import requests
from datetime import datetime, timedelta
from django.conf import settings
from django.utils import timezone
from urllib.parse import urlencode
import logging

logger = logging.getLogger(__name__)


class ORCIDService:
    """
    Service class for ORCID OAuth2 operations.
    """
    
    def __init__(self):
        self.client_id = settings.ORCID_CLIENT_ID
        self.client_secret = settings.ORCID_CLIENT_SECRET
        self.oauth_base_url = settings.ORCID_OAUTH_BASE_URL
        self.token_url = settings.ORCID_TOKEN_URL
        self.api_base_url = settings.ORCID_API_BASE_URL
        self.redirect_uri = f"{settings.FRONTEND_URL}/auth/orcid/callback"
    
    def get_authorization_url(self, state=None):
        """
        Generate ORCID authorization URL.
        
        Args:
            state: Optional state parameter for CSRF protection
            
        Returns:
            str: Authorization URL to redirect user to
        """
        params = {
            'client_id': self.client_id,
            'response_type': 'code',
            'scope': '/authenticate',  # Request authentication scope
            'redirect_uri': self.redirect_uri,
        }
        
        if state:
            params['state'] = state
        
        url = f"{self.oauth_base_url}?{urlencode(params)}"
        logger.info(f"Generated ORCID authorization URL for client_id={self.client_id}")
        return url
    
    def exchange_code_for_token(self, authorization_code):
        """
        Exchange authorization code for access token.
        
        Args:
            authorization_code: Authorization code from ORCID callback
            
        Returns:
            dict: Token response containing:
                - access_token: ORCID access token
                - token_type: Token type (usually 'bearer')
                - refresh_token: Refresh token for token renewal
                - expires_in: Token expiration time in seconds
                - scope: Granted scopes
                - name: User's name
                - orcid: User's ORCID iD
                
        Raises:
            requests.RequestException: If token exchange fails
        """
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'authorization_code',
            'code': authorization_code,
            'redirect_uri': self.redirect_uri,
        }
        
        headers = {
            'Accept': 'application/json',
        }
        
        try:
            response = requests.post(
                self.token_url,
                data=data,
                headers=headers,
                timeout=10
            )
            response.raise_for_status()
            
            token_data = response.json()
            logger.info(f"Successfully exchanged code for ORCID token: {token_data.get('orcid')}")
            return token_data
            
        except requests.RequestException as e:
            logger.error(f"ORCID token exchange failed: {str(e)}")
            raise
    
    def get_user_profile(self, orcid_id, access_token):
        """
        Fetch user profile from ORCID API.
        
        Args:
            orcid_id: User's ORCID iD
            access_token: ORCID access token
            
        Returns:
            dict: User profile data containing:
                - given-names: First name
                - family-name: Last name
                - emails: List of email addresses
                - biography: User biography
                - keywords: Research keywords
                - employment: Employment history
                - education: Education history
                
        Raises:
            requests.RequestException: If API request fails
        """
        url = f"{self.api_base_url}/{orcid_id}/person"
        
        headers = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {access_token}',
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            profile_data = response.json()
            logger.info(f"Successfully fetched ORCID profile: {orcid_id}")
            return profile_data
            
        except requests.RequestException as e:
            logger.error(f"ORCID profile fetch failed for {orcid_id}: {str(e)}")
            raise
    
    def refresh_access_token(self, refresh_token):
        """
        Refresh ORCID access token using refresh token.
        
        Args:
            refresh_token: ORCID refresh token
            
        Returns:
            dict: New token response
            
        Raises:
            requests.RequestException: If token refresh fails
        """
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token,
        }
        
        headers = {
            'Accept': 'application/json',
        }
        
        try:
            response = requests.post(
                self.token_url,
                data=data,
                headers=headers,
                timeout=10
            )
            response.raise_for_status()
            
            token_data = response.json()
            logger.info("Successfully refreshed ORCID access token")
            return token_data
            
        except requests.RequestException as e:
            logger.error(f"ORCID token refresh failed: {str(e)}")
            raise
    
    def parse_user_data(self, token_response, profile_data=None):
        """
        Parse ORCID response data into user model fields.
        
        Args:
            token_response: Token exchange response
            profile_data: Optional detailed profile data
            
        Returns:
            dict: Parsed user data ready for User model
        """
        user_data = {
            'orcid_id': token_response.get('orcid'),
            'orcid_access_token': token_response.get('access_token'),
            'orcid_refresh_token': token_response.get('refresh_token'),
            'orcid_verified': True,
        }
        
        # Calculate token expiration
        expires_in = token_response.get('expires_in', 631138518)  # ORCID default: 20 years
        user_data['orcid_token_expires_at'] = timezone.now() + timedelta(seconds=expires_in)
        
        # Extract name from token response
        if 'name' in token_response:
            user_data['full_name'] = token_response['name']
        
        # Extract additional data from detailed profile
        if profile_data:
            # Parse name
            name_data = profile_data.get('name', {})
            if name_data:
                given_names = name_data.get('given-names', {}).get('value', '')
                family_name = name_data.get('family-name', {}).get('value', '')
                if given_names or family_name:
                    user_data['full_name'] = f"{given_names} {family_name}".strip()
            
            # Parse biography
            bio_data = profile_data.get('biography', {})
            if bio_data and bio_data.get('content'):
                user_data['bio'] = bio_data['content']
            
            # Parse primary email
            emails_data = profile_data.get('emails', {}).get('email', [])
            if emails_data:
                primary_email = next(
                    (e['email'] for e in emails_data if e.get('primary')),
                    emails_data[0]['email'] if emails_data else None
                )
                if primary_email:
                    user_data['email'] = primary_email
                    user_data['email_verified'] = True
        
        return user_data


# Singleton instance
orcid_service = ORCIDService()
