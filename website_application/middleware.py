"""
Security Monitoring Middleware
Tracks requests, detects threats, and logs security events
"""

import logging
import time
from django.utils.deprecation import MiddlewareMixin
from django.core.cache import cache
from django.http import HttpResponseForbidden
import re

logger = logging.getLogger('security')


class SecurityMonitoringMiddleware(MiddlewareMixin):
    """
    Middleware for monitoring security threats and suspicious activities
    """
    
    # SQL Injection patterns
    SQL_INJECTION_PATTERNS = [
        r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION)\b)",
        r"(--|;|\/\*|\*\/|xp_|sp_)",
        r"('|\"|;|--|\||`)",
    ]
    
    # XSS patterns
    XSS_PATTERNS = [
        r"<script[^>]*>.*?</script>",
        r"javascript:",
        r"onerror\s*=",
        r"onload\s*=",
    ]
    
    # Rate limiting settings
    RATE_LIMIT_REQUESTS = 100  # requests per window
    RATE_LIMIT_WINDOW = 60  # seconds
    
    def process_request(self, request):
        """Process incoming request for security threats"""
        
        # Start timing
        request.security_start_time = time.time()
        
        # Get client IP
        ip_address = self.get_client_ip(request)
        request.client_ip = ip_address
        
        # Check rate limiting
        if self.is_rate_limited(ip_address):
            logger.warning(f"Rate limit exceeded for IP: {ip_address}")
            return HttpResponseForbidden("Rate limit exceeded. Please try again later.")
        
        # Check for SQL injection attempts
        if self.detect_sql_injection(request):
            logger.critical(f"SQL injection attempt detected from {ip_address}: {request.path}")
            self.increment_threat_counter('sql_injection')
            # Optionally block the request
            # return HttpResponseForbidden("Suspicious activity detected")
        
        # Check for XSS attempts
        if self.detect_xss(request):
            logger.critical(f"XSS attempt detected from {ip_address}: {request.path}")
            self.increment_threat_counter('xss')
        
        # Check for suspicious user agents
        if self.is_suspicious_user_agent(request):
            logger.warning(f"Suspicious user agent from {ip_address}: {request.META.get('HTTP_USER_AGENT', '')}")
            self.increment_threat_counter('suspicious_agent')
        
        # Track page access
        self.track_page_access(request)
        
        return None
    
    def process_response(self, request, response):
        """Process response and log metrics"""
        
        # Calculate response time
        if hasattr(request, 'security_start_time'):
            response_time = (time.time() - request.security_start_time) * 1000  # ms
            
            # Log slow responses
            if response_time > 1000:  # More than 1 second
                logger.warning(f"Slow response: {request.path} took {response_time:.2f}ms")
            
            # Store response time for analytics
            self.store_response_time(response_time)
        
        # Add security headers if not present
        if 'X-Content-Type-Options' not in response:
            response['X-Content-Type-Options'] = 'nosniff'
        
        if 'X-Frame-Options' not in response:
            response['X-Frame-Options'] = 'DENY'
        
        if 'X-XSS-Protection' not in response:
            response['X-XSS-Protection'] = '1; mode=block'
        
        return response
    
    def get_client_ip(self, request):
        """Extract client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def is_rate_limited(self, ip_address):
        """Check if IP address is rate limited"""
        cache_key = f'rate_limit:{ip_address}'
        requests = cache.get(cache_key, 0)
        
        if requests >= self.RATE_LIMIT_REQUESTS:
            return True
        
        # Increment counter
        cache.set(cache_key, requests + 1, self.RATE_LIMIT_WINDOW)
        return False
    
    def detect_sql_injection(self, request):
        """Detect SQL injection attempts"""
        # Check GET parameters
        for key, value in request.GET.items():
            if self.matches_patterns(value, self.SQL_INJECTION_PATTERNS):
                return True
        
        # Check POST data
        if request.method == 'POST':
            for key, value in request.POST.items():
                if isinstance(value, str) and self.matches_patterns(value, self.SQL_INJECTION_PATTERNS):
                    return True
        
        return False
    
    def detect_xss(self, request):
        """Detect XSS attempts"""
        # Check GET parameters
        for key, value in request.GET.items():
            if self.matches_patterns(value, self.XSS_PATTERNS):
                return True
        
        # Check POST data
        if request.method == 'POST':
            for key, value in request.POST.items():
                if isinstance(value, str) and self.matches_patterns(value, self.XSS_PATTERNS):
                    return True
        
        return False
    
    def matches_patterns(self, text, patterns):
        """Check if text matches any of the given patterns"""
        if not isinstance(text, str):
            return False
        
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False
    
    def is_suspicious_user_agent(self, request):
        """Check for suspicious user agents"""
        user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
        
        suspicious_agents = [
            'bot', 'crawler', 'spider', 'scraper', 
            'wget', 'curl', 'python-requests'
        ]
        
        # Allow legitimate bots (Google, Bing, etc.)
        legitimate_bots = ['googlebot', 'bingbot', 'slackbot']
        
        for agent in legitimate_bots:
            if agent in user_agent:
                return False
        
        for agent in suspicious_agents:
            if agent in user_agent:
                return True
        
        return False
    
    def track_page_access(self, request):
        """Track page access for analytics"""
        cache_key = f'page_access:{request.path}'
        views = cache.get(cache_key, 0)
        cache.set(cache_key, views + 1, 3600)  # Store for 1 hour
    
    def increment_threat_counter(self, threat_type):
        """Increment threat counter"""
        cache_key = f'threat:{threat_type}'
        count = cache.get(cache_key, 0)
        cache.set(cache_key, count + 1, 86400)  # Store for 24 hours
    
    def store_response_time(self, response_time):
        """Store response time for performance monitoring"""
        cache_key = 'response_times'
        times = cache.get(cache_key, [])
        times.append(response_time)
        
        # Keep only last 100 response times
        if len(times) > 100:
            times = times[-100:]
        
        cache.set(cache_key, times, 3600)  # Store for 1 hour


class SessionSecurityMiddleware(MiddlewareMixin):
    """
    Enhanced session security
    """
    
    def process_request(self, request):
        """Track session security"""
        
        if request.user.is_authenticated:
            # Track active sessions
            cache_key = 'active_sessions'
            sessions = cache.get(cache_key, 0)
            cache.set(cache_key, sessions + 1, 300)  # 5 minutes
            
            # Check for session hijacking
            session_ip = request.session.get('ip_address')
            current_ip = self.get_client_ip(request)
            
            if session_ip and session_ip != current_ip:
                logger.warning(
                    f"Possible session hijacking: Session IP {session_ip} "
                    f"!= Current IP {current_ip} for user {request.user.username}"
                )
            
            # Store IP in session
            request.session['ip_address'] = current_ip
        
        return None
    
    def get_client_ip(self, request):
        """Extract client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


# Add to settings.py:
"""
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    
    # Add custom security middleware
    'website_application.middleware.SecurityMonitoringMiddleware',
    'website_application.middleware.SessionSecurityMiddleware',
]

# Security settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
CSRF_COOKIE_SECURE = True  # Only on HTTPS
SESSION_COOKIE_SECURE = True  # Only on HTTPS
SECURE_SSL_REDIRECT = True  # Redirect HTTP to HTTPS

# Cache configuration (for middleware)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'security_file': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': 'logs/security.log',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'security': {
            'handlers': ['security_file'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
}
"""