from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

@dataclass
class SLIResult:
    """Result of an SLI query."""
    value: float
    unit: str
    query: str
    source: str
    timestamp: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class MetricsAdapter(ABC):
    """Base class for metrics adapters."""
    
    @abstractmethod
    def query_sli(self, component: str, sli_type: str) -> Optional[SLIResult]:
        """
        Query an SLI for a component.
        
        Args:
            component: The component to query
            sli_type: The type of SLI to query (e.g., 'availability', 'latency', 'error_rate')
        
        Returns:
            SLIResult if successful, None otherwise
        """
        pass

    @abstractmethod
    def get_available_components(self) -> List[str]:
        """
        Get list of available components.
        
        Returns:
            List of component names
        """
        pass

    @abstractmethod
    def get_available_sli_types(self) -> List[str]:
        """
        Get list of available SLI types.
        
        Returns:
            List of SLI type names
        """
        pass

    @abstractmethod
    def validate_connection(self) -> bool:
        """
        Validate the connection to the metrics backend.
        
        Returns:
            True if connection is valid, False otherwise
        """
        pass 