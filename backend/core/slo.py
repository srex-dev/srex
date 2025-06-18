"""Service Level Objective (SLO) management module."""

import yaml
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging
from pathlib import Path
import numpy as np
from scipy import stats

logger = logging.getLogger(__name__)

def load_slo(slo_path: str) -> Dict[str, Any]:
    """Load an SLO definition from a YAML file.
    
    Args:
        slo_path: Path to the SLO definition file
        
    Returns:
        SLO definition dictionary
    """
    try:
        with open(slo_path, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        logger.error(f"Error loading SLO file {slo_path}: {str(e)}")
        raise

def get_slo_history(slo_path: str, time_range: str = "7d", interval: str = "1h",
                   include_metadata: bool = True, adapter: str = None) -> Dict[str, Any]:
    """Get historical data for an SLO.
    
    Args:
        slo_path: Path to the SLO definition file
        time_range: Time range to query (e.g., "7d", "24h")
        interval: Data point interval (e.g., "1h", "5m")
        include_metadata: Whether to include metadata in the response
        adapter: Name of the metric adapter
        
    Returns:
        Dictionary containing historical data and optional metadata
    """
    try:
        # Load SLO definition
        slo_def = load_slo(slo_path)
        metric = slo_def['slo']['metric']['name'] if 'metric' in slo_def['slo'] and 'name' in slo_def['slo']['metric'] else 'unknown'
        
        # Parse time range
        range_value = int(time_range[:-1])
        range_unit = time_range[-1]
        if range_unit == 'd':
            end_time = datetime.now()
            start_time = end_time - timedelta(days=range_value)
        elif range_unit == 'h':
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=range_value)
        else:
            raise ValueError(f"Unsupported time range unit: {range_unit}")
        
        # Parse interval
        interval_value = int(interval[:-1])
        interval_unit = interval[-1]
        if interval_unit == 'h':
            step_hours = interval_value
        elif interval_unit == 'd':
            step_hours = interval_value * 24
        else:
            raise ValueError(f"Unsupported interval unit: {interval_unit}")
        
        # TODO: Query actual metric data from configured adapter
        # For now, generate synthetic data
        num_points = int((end_time - start_time).total_seconds() / 3600 // step_hours)
        timestamps = [start_time + timedelta(hours=i*step_hours) for i in range(num_points)]
        values = np.random.normal(0.95, 0.02, num_points)  # Mean 95%, std 2%
        values = np.clip(values, 0, 1)  # Clip to [0, 1] range
        
        history = [
            {
                'timestamp': ts.isoformat(),
                'value': float(val),
                'status': 'good' if val >= slo_def['slo']['target'] else 'bad',
                'metric': metric
            }
            for ts, val in zip(timestamps, values)
        ]
        
        result = {
            'status': 'success',
            'history': history
        }
        
        if include_metadata:
            result['metadata'] = {
                'slo_name': slo_def['slo']['name'],
                'target': slo_def['slo']['target'],
                'time_range': time_range,
                'interval': interval,
                'adapter': adapter
            }
        
        return result
        
    except Exception as e:
        logger.error(f"Error getting SLO history: {str(e)}")
        raise

def analyze_slo_trend(slo_path: str, time_range: str = "30d",
                     trend_type: str = "linear", window: str = "7d", adapter: str = None) -> Dict[str, Any]:
    """Analyze trends in SLO performance.
    
    Args:
        slo_path: Path to the SLO definition file
        time_range: Time range to analyze (e.g., "30d", "7d")
        trend_type: Type of trend analysis ("linear" or "moving_average")
        window: Window size for moving average (e.g., "7d", "24h")
        adapter: Name of the metric adapter
        
    Returns:
        Dictionary containing trend analysis results
    """
    try:
        # Get historical data
        history_data = get_slo_history(slo_path, time_range=time_range, adapter=adapter)
        values = [point['value'] for point in history_data['history']]
        timestamps = [datetime.fromisoformat(point['timestamp']) for point in history_data['history']]
        
        forecast = None
        if trend_type == "linear":
            # Perform linear regression
            x = np.array([(t - timestamps[0]).total_seconds() for t in timestamps])
            y = np.array(values)
            slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
            
            # Calculate trend line
            trend_line = slope * x + intercept
            
            # Calculate forecast (next 7 days)
            forecast_days = 7
            forecast_x = np.array([(timestamps[-1] + timedelta(days=i) - timestamps[0]).total_seconds()
                                 for i in range(1, forecast_days + 1)])
            forecast_y = slope * forecast_x + intercept
            
            forecast = {
                'timestamps': [(timestamps[-1] + timedelta(days=i)).isoformat()
                             for i in range(1, forecast_days + 1)],
                'values': [float(v) for v in forecast_y]
            }
            
            trend = {
                'type': 'linear',
                'slope': float(slope),
                'intercept': float(intercept),
                'r_squared': float(r_value ** 2),
                'p_value': float(p_value),
                'std_err': float(std_err),
                'trend_line': [float(v) for v in trend_line],
                'forecast': forecast
            }
            
        elif trend_type == "moving_average":
            # Parse window size
            window_value = int(window[:-1])
            window_unit = window[-1]
            if window_unit == 'd':
                window_size = window_value * 24  # Convert to hours
            elif window_unit == 'h':
                window_size = window_value
            else:
                raise ValueError(f"Unsupported window unit: {window_unit}")
            
            # Calculate moving average
            values_array = np.array(values)
            trend_line = np.convolve(values_array, np.ones(window_size)/window_size, mode='valid')
            
            # Pad the beginning with the first value
            trend_line = np.pad(trend_line, (window_size-1, 0), mode='edge')
            
            trend = {
                'type': 'moving_average',
                'window_size': window_size,
                'trend_line': [float(v) for v in trend_line]
            }
            
        else:
            raise ValueError(f"Unsupported trend type: {trend_type}")
        
        result = {
            'status': 'success',
            'trend': trend,
            'metadata': {
                'slo_name': history_data['metadata']['slo_name'],
                'target': history_data['metadata']['target'],
                'time_range': time_range,
                'trend_type': trend_type,
                'window': window,
                'adapter': adapter
            }
        }
        
        if forecast:
            result['forecast'] = forecast
        
        return result
        
    except Exception as e:
        logger.error(f"Error analyzing SLO trend: {str(e)}")
        raise 