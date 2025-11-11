"""
HivePath - A pathlib.Path subclass for Hive-style partitioning.
"""

import re
from pathlib import Path
from typing import Dict, Optional


class HivePath(Path):
    """
    A Path subclass that adds functionality for Hive-style partitioning.
    
    Hive-style partitioning uses directory names in the format: key=value
    For example: data/year=2023/month=01/day=15/file.parquet
    
    This class extends pathlib.Path with methods to:
    - Parse partition information from paths
    - Extract partition key-value pairs
    - Build paths with partitions
    """
    
    # Pattern to match Hive-style partition directories: key=value
    PARTITION_PATTERN = re.compile(r'^([^=]+)=(.+)$')
    
    def __new__(cls, *args):
        """Create a new HivePath instance."""
        if cls is HivePath:
            # Get the concrete Path class for this OS (WindowsPath or PosixPath)
            concrete_path = type(Path())
            # Create a concrete class that combines HivePath with the OS-specific Path class
            cls = type('HivePath', (HivePath, concrete_path), {})
        return Path.__new__(cls, *args)
    
    @property
    def partitions(self) -> Dict[str, str]:
        """
        Extract all partition key-value pairs from the path.
        
        Returns:
            Dictionary mapping partition keys to their values.
            
        Example:
            >>> path = HivePath("data/year=2023/month=01/file.txt")
            >>> path.partitions
            {'year': '2023', 'month': '01'}
        """
        partitions = {}
        for part in self.parts:
            match = self.PARTITION_PATTERN.match(part)
            if match:
                key, value = match.groups()
                partitions[key] = value
        return partitions
    
    def get_partition(self, key: str) -> Optional[str]:
        """
        Get the value of a specific partition key.
        
        Args:
            key: The partition key to look up.
            
        Returns:
            The partition value if found, None otherwise.
            
        Example:
            >>> path = HivePath("data/year=2023/month=01/file.txt")
            >>> path.get_partition("year")
            '2023'
        """
        return self.partitions.get(key)
    
    def has_partition(self, key: str, value: Optional[str] = None) -> bool:
        """
        Check if the path contains a specific partition.
        
        Args:
            key: The partition key to check.
            value: Optional value to match. If None, only checks for key existence.
            
        Returns:
            True if the partition exists (and matches value if provided).
            
        Example:
            >>> path = HivePath("data/year=2023/month=01/file.txt")
            >>> path.has_partition("year", "2023")
            True
            >>> path.has_partition("day")
            False
        """
        if value is None:
            return key in self.partitions
        return self.get_partition(key) == value
    
    def base_path(self) -> Path:
        """
        Get the base path without partition directories.
        
        Returns:
            A Path object with partition directories removed.
            
        Example:
            >>> path = HivePath("data/year=2023/month=01/file.txt")
            >>> path.base_path()
            Path('data/file.txt')
        """
        parts = []
        for part in self.parts:
            if not self.PARTITION_PATTERN.match(part):
                parts.append(part)
        return Path(*parts) if parts else Path('.')
    
    def partition_path(self) -> Path:
        """
        Get only the partition portion of the path.
        
        Returns:
            A Path object containing only partition directories.
            
        Example:
            >>> path = HivePath("data/year=2023/month=01/file.txt")
            >>> path.partition_path()
            Path('year=2023/month=01')
        """
        parts = []
        for part in self.parts:
            if self.PARTITION_PATTERN.match(part):
                parts.append(part)
        return Path(*parts) if parts else Path('.')
    
    @classmethod
    def with_partitions(cls, base: str, partitions: Dict[str, str]) -> 'HivePath':
        """
        Create a HivePath with specified partitions.
        
        Args:
            base: The base path (can include existing partitions).
            partitions: Dictionary of partition key-value pairs to add.
            
        Returns:
            A new HivePath with the partitions added.
            
        Example:
            >>> path = HivePath.with_partitions("data", {"year": "2023", "month": "01"})
            >>> str(path)
            'data/year=2023/month=01'
        """
        base_path = cls(base)
        partition_parts = [f"{k}={v}" for k, v in sorted(partitions.items())]
        return cls(base_path, *partition_parts)
    
    def add_partition(self, key: str, value: str) -> 'HivePath':
        """
        Create a new HivePath with an additional partition.
        
        Args:
            key: The partition key.
            value: The partition value.
            
        Returns:
            A new HivePath with the partition added.
            
        Example:
            >>> path = HivePath("data/year=2023")
            >>> path.add_partition("month", "01")
            HivePath('data/year=2023/month=01')
        """
        new_partitions = self.partitions.copy()
        new_partitions[key] = value
        return self.with_partitions(str(self.base_path()), new_partitions)

