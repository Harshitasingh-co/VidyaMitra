"""Response formatting utilities"""
from typing import Any, Optional
from datetime import datetime

class ResponseFormatter:
    """Format API responses consistently"""
    
    @staticmethod
    def success(data: Any, message: str = "Success") -> dict:
        """
        Format successful response
        
        Args:
            data: Response data
            message: Success message
            
        Returns:
            Formatted response
        """
        return {
            "success": True,
            "message": message,
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    @staticmethod
    def error(message: str, error_code: Optional[str] = None, details: Any = None) -> dict:
        """
        Format error response
        
        Args:
            message: Error message
            error_code: Optional error code
            details: Additional error details
            
        Returns:
            Formatted error response
        """
        response = {
            "success": False,
            "message": message,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if error_code:
            response["error_code"] = error_code
        
        if details:
            response["details"] = details
        
        return response
    
    @staticmethod
    def paginated(data: list, page: int, page_size: int, total: int) -> dict:
        """
        Format paginated response
        
        Args:
            data: Page data
            page: Current page number
            page_size: Items per page
            total: Total items
            
        Returns:
            Formatted paginated response
        """
        return {
            "success": True,
            "data": data,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total": total,
                "total_pages": (total + page_size - 1) // page_size
            },
            "timestamp": datetime.utcnow().isoformat()
        }

def get_response_formatter() -> ResponseFormatter:
    """Get ResponseFormatter instance"""
    return ResponseFormatter()
