from fastapi import Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.base import BaseHTTPMiddleware
from starlette.middleware.base import RequestResponseEndpoint
from starlette.responses import Response
import time
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import json
from core.config import settings
from core.audit import audit_logger
from core.services.logging.logger import logger

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware."""
    
    def __init__(self, app):
        super().__init__(app)
        self.requests: Dict[str, List[float]] = {}
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Get client IP
        client_ip = request.client.host
        
        # Clean old requests
        now = time.time()
        if client_ip in self.requests:
            self.requests[client_ip] = [
                req_time for req_time in self.requests[client_ip]
                if now - req_time < settings.RATE_LIMIT_WINDOW
            ]
        
        # Check rate limit
        if client_ip in self.requests and len(self.requests[client_ip]) >= settings.RATE_LIMIT_REQUESTS:
            audit_logger.log_rate_limit_exceeded(client_ip, request.url.path)
            raise HTTPException(
                status_code=429,
                detail="Too many requests"
            )
        
        # Add request timestamp
        if client_ip not in self.requests:
            self.requests[client_ip] = []
        self.requests[client_ip].append(now)
        
        # Process request
        return await call_next(request)

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Security headers middleware."""
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        return response

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Request logging middleware."""
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Start timer
        start_time = time.time()
        
        # Get request details
        client_ip = request.client.host
        method = request.method
        url = str(request.url)
        
        try:
            # Process request
            response = await call_next(request)
            
            # Calculate processing time
            process_time = time.time() - start_time
            
            # Log request
            logger.info(
                f"Request: {method} {url} - Status: {response.status_code} - "
                f"Time: {process_time:.2f}s - IP: {client_ip}"
            )
            
            return response
            
        except Exception as e:
            # Log error
            logger.error(
                f"Request failed: {method} {url} - Error: {str(e)} - "
                f"IP: {client_ip}"
            )
            raise

class AuditLoggingMiddleware(BaseHTTPMiddleware):
    """Audit logging middleware."""
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Get request details
        client_ip = request.client.host
        method = request.method
        url = str(request.url)
        
        # Log sensitive operations
        if method in ["POST", "PUT", "DELETE"]:
            try:
                body = await request.json()
            except:
                body = {}
            
            # Log file operations
            if "/api/v1/policies" in url or "/api/v1/slos" in url:
                audit_logger.log_file_access(
                    username=request.state.user.username if hasattr(request.state, "user") else "anonymous",
                    file_path=url,
                    action=method
                )
            
            # Log API key operations
            if "/api/v1/api-keys" in url:
                if method == "POST":
                    audit_logger.log_api_key_creation(
                        key_name=body.get("name", "unknown"),
                        created_by=request.state.user.username if hasattr(request.state, "user") else "anonymous",
                        scopes=body.get("scopes", [])
                    )
                elif method == "DELETE":
                    audit_logger.log_api_key_revocation(
                        key_name=url.split("/")[-1],
                        revoked_by=request.state.user.username if hasattr(request.state, "user") else "anonymous"
                    )
        
        return await call_next(request)

def setup_middleware(app):
    """Setup all middleware."""
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Security headers middleware
    app.add_middleware(SecurityHeadersMiddleware)
    
    # Rate limiting middleware
    app.add_middleware(RateLimitMiddleware)
    
    # Request logging middleware
    app.add_middleware(RequestLoggingMiddleware)
    
    # Audit logging middleware
    app.add_middleware(AuditLoggingMiddleware) 