# metrics/adapters/base_adapter.py

from abc import ABC, abstractmethod

class MetricAdapter(ABC):
    @abstractmethod
    def fetch_sli_metrics(self, config):
        pass