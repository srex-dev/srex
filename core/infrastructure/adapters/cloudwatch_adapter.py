"""AWS CloudWatch metric adapter implementation."""

import boto3
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class CloudWatchAdapter:
    """Adapter for querying metrics from AWS CloudWatch."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the CloudWatch adapter.
        
        Args:
            config: Configuration dictionary containing:
                - region: AWS region
                - access_key: Optional AWS access key
                - secret_key: Optional AWS secret key
        """
        self.region = config['region']
        self.client = boto3.client(
            'cloudwatch',
            region_name=self.region,
            aws_access_key_id=config.get('access_key'),
            aws_secret_access_key=config.get('secret_key')
        )
    
    def query_metric(self, namespace: str, metric_name: str, dimensions: List[Dict[str, str]],
                    start_time: datetime, end_time: datetime, period: int = 60) -> List[Dict[str, Any]]:
        """Query a metric from CloudWatch.
        
        Args:
            namespace: CloudWatch namespace
            metric_name: Name of the metric
            dimensions: List of dimension dictionaries
            start_time: Start time for the query
            end_time: End time for the query
            period: Data point interval in seconds (default: 60)
            
        Returns:
            List of metric data points
        """
        try:
            response = self.client.get_metric_statistics(
                Namespace=namespace,
                MetricName=metric_name,
                Dimensions=dimensions,
                StartTime=start_time,
                EndTime=end_time,
                Period=period,
                Statistics=['Average', 'Sum', 'Minimum', 'Maximum', 'SampleCount']
            )
            
            return response['Datapoints']
            
        except Exception as e:
            logger.error(f"Error querying CloudWatch: {str(e)}")
            raise
    
    def get_metric_names(self, namespace: str) -> List[str]:
        """Get list of available metric names in a namespace.
        
        Args:
            namespace: CloudWatch namespace
            
        Returns:
            List of metric names
        """
        try:
            metrics = []
            paginator = self.client.get_paginator('list_metrics')
            
            for page in paginator.paginate(Namespace=namespace):
                for metric in page['Metrics']:
                    if metric['MetricName'] not in metrics:
                        metrics.append(metric['MetricName'])
            
            return sorted(metrics)
            
        except Exception as e:
            logger.error(f"Error getting metric names: {str(e)}")
            raise
    
    def get_namespaces(self) -> List[str]:
        """Get list of available CloudWatch namespaces.
        
        Returns:
            List of namespace names
        """
        try:
            namespaces = []
            paginator = self.client.get_paginator('list_metrics')
            
            for page in paginator.paginate():
                for metric in page['Metrics']:
                    if metric['Namespace'] not in namespaces:
                        namespaces.append(metric['Namespace'])
            
            return sorted(namespaces)
            
        except Exception as e:
            logger.error(f"Error getting namespaces: {str(e)}")
            raise
    
    def get_dimensions(self, namespace: str, metric_name: str) -> List[Dict[str, str]]:
        """Get available dimensions for a metric.
        
        Args:
            namespace: CloudWatch namespace
            metric_name: Name of the metric
            
        Returns:
            List of dimension dictionaries
        """
        try:
            dimensions = []
            paginator = self.client.get_paginator('list_metrics')
            
            for page in paginator.paginate(Namespace=namespace, MetricName=metric_name):
                for metric in page['Metrics']:
                    if metric['Dimensions'] not in dimensions:
                        dimensions.append(metric['Dimensions'])
            
            return dimensions
            
        except Exception as e:
            logger.error(f"Error getting dimensions: {str(e)}")
            raise 