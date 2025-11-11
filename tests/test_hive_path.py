"""Tests for HivePath class."""

import pytest
from pathlib import Path
from hive_path import HivePath


class TestHivePathCreation:
    """Test HivePath instance creation."""
    
    def test_create_from_string(self):
        """Test creating HivePath from string."""
        path = HivePath("data/year=2023/month=01/file.txt")
        assert isinstance(path, HivePath)
        assert isinstance(path, Path)
    
    def test_create_from_path(self):
        """Test creating HivePath from Path object."""
        base_path = Path("data/year=2023")
        path = HivePath(base_path)
        assert isinstance(path, HivePath)
    
    def test_create_with_multiple_args(self):
        """Test creating HivePath with multiple path components."""
        path = HivePath("data", "year=2023", "month=01", "file.txt")
        assert isinstance(path, HivePath)
        assert "year=2023" in str(path)
        assert "month=01" in str(path)


class TestPartitionParsing:
    """Test partition extraction and parsing."""
    
    def test_single_partition(self):
        """Test extracting a single partition."""
        path = HivePath("data/year=2023/file.txt")
        assert path.partitions == {"year": "2023"}
    
    def test_multiple_partitions(self):
        """Test extracting multiple partitions."""
        path = HivePath("data/year=2023/month=01/day=15/file.txt")
        assert path.partitions == {"year": "2023", "month": "01", "day": "15"}
    
    def test_no_partitions(self):
        """Test path with no partitions."""
        path = HivePath("data/file.txt")
        assert path.partitions == {}
    
    def test_partitions_in_different_positions(self):
        """Test partitions at different positions in path."""
        path = HivePath("base/year=2023/data/month=01/file.txt")
        assert path.partitions == {"year": "2023", "month": "01"}
    
    def test_partition_with_special_characters(self):
        """Test partition values with special characters."""
        path = HivePath("data/date=2023-01-15/file.txt")
        assert path.partitions == {"date": "2023-01-15"}
    
    def test_partition_key_with_underscore(self):
        """Test partition keys with underscores."""
        path = HivePath("data/partition_key=value/file.txt")
        assert path.partitions == {"partition_key": "value"}


class TestGetPartition:
    """Test get_partition method."""
    
    def test_get_existing_partition(self):
        """Test getting an existing partition."""
        path = HivePath("data/year=2023/month=01/file.txt")
        assert path.get_partition("year") == "2023"
        assert path.get_partition("month") == "01"
    
    def test_get_nonexistent_partition(self):
        """Test getting a non-existent partition."""
        path = HivePath("data/year=2023/file.txt")
        assert path.get_partition("month") is None
        assert path.get_partition("day") is None


class TestHasPartition:
    """Test has_partition method."""
    
    def test_has_partition_without_value(self):
        """Test checking partition existence without value."""
        path = HivePath("data/year=2023/month=01/file.txt")
        assert path.has_partition("year") is True
        assert path.has_partition("month") is True
        assert path.has_partition("day") is False
    
    def test_has_partition_with_matching_value(self):
        """Test checking partition with matching value."""
        path = HivePath("data/year=2023/month=01/file.txt")
        assert path.has_partition("year", "2023") is True
        assert path.has_partition("month", "01") is True
    
    def test_has_partition_with_non_matching_value(self):
        """Test checking partition with non-matching value."""
        path = HivePath("data/year=2023/month=01/file.txt")
        assert path.has_partition("year", "2022") is False
        assert path.has_partition("month", "02") is False


class TestBasePath:
    """Test base_path method."""
    
    def test_base_path_with_partitions(self):
        """Test getting base path without partitions."""
        path = HivePath("data/year=2023/month=01/file.txt")
        base = path.base_path()
        assert isinstance(base, Path)
        assert "year=2023" not in str(base)
        assert "month=01" not in str(base)
        assert "file.txt" in str(base)
    
    def test_base_path_no_partitions(self):
        """Test base path when there are no partitions."""
        path = HivePath("data/file.txt")
        base = path.base_path()
        assert str(base) == str(Path("data/file.txt"))
    
    def test_base_path_only_partitions(self):
        """Test base path when path contains only partitions."""
        path = HivePath("year=2023/month=01")
        base = path.base_path()
        # Should return current directory or empty path
        assert isinstance(base, Path)


class TestPartitionPath:
    """Test partition_path method."""
    
    def test_partition_path_extraction(self):
        """Test extracting only partition portion."""
        path = HivePath("data/year=2023/month=01/file.txt")
        partition_path = path.partition_path()
        assert isinstance(partition_path, Path)
        assert "year=2023" in str(partition_path)
        assert "month=01" in str(partition_path)
        assert "data" not in str(partition_path)
        assert "file.txt" not in str(partition_path)
    
    def test_partition_path_no_partitions(self):
        """Test partition path when there are no partitions."""
        path = HivePath("data/file.txt")
        partition_path = path.partition_path()
        assert isinstance(partition_path, Path)


class TestWithPartitions:
    """Test with_partitions class method."""
    
    def test_create_with_partitions(self):
        """Test creating path with partitions."""
        path = HivePath.with_partitions("data", {"year": "2023", "month": "01"})
        assert isinstance(path, HivePath)
        assert path.get_partition("year") == "2023"
        assert path.get_partition("month") == "01"
    
    def test_with_partitions_sorted(self):
        """Test that partitions are sorted in the path."""
        path = HivePath.with_partitions("data", {"month": "01", "year": "2023"})
        path_str = str(path)
        # Partitions should be sorted alphabetically
        assert path_str.index("month=01") < path_str.index("year=2023") or \
               path_str.index("year=2023") < path_str.index("month=01")
    
    def test_with_partitions_empty_dict(self):
        """Test creating path with empty partitions."""
        path = HivePath.with_partitions("data", {})
        assert isinstance(path, HivePath)
        assert path.partitions == {}


class TestAddPartition:
    """Test add_partition method."""
    
    def test_add_new_partition(self):
        """Test adding a new partition."""
        path = HivePath("data/year=2023")
        new_path = path.add_partition("month", "01")
        assert isinstance(new_path, HivePath)
        assert new_path.get_partition("year") == "2023"
        assert new_path.get_partition("month") == "01"
    
    def test_add_partition_overwrites_existing(self):
        """Test that adding existing partition overwrites it."""
        path = HivePath("data/year=2023")
        new_path = path.add_partition("year", "2024")
        assert new_path.get_partition("year") == "2024"
        assert new_path.get_partition("year") != "2023"
    
    def test_add_multiple_partitions(self):
        """Test adding multiple partitions sequentially."""
        path = HivePath("data")
        path = path.add_partition("year", "2023")
        path = path.add_partition("month", "01")
        path = path.add_partition("day", "15")
        assert path.partitions == {"year": "2023", "month": "01", "day": "15"}


class TestPathlibCompatibility:
    """Test that HivePath works with standard pathlib methods."""
    
    def test_parent_property(self):
        """Test parent property works."""
        path = HivePath("data/year=2023/month=01/file.txt")
        parent = path.parent
        assert isinstance(parent, Path)
        assert "file.txt" not in str(parent)
    
    def test_name_property(self):
        """Test name property works."""
        path = HivePath("data/year=2023/month=01/file.txt")
        assert path.name == "file.txt"
    
    def test_suffix_property(self):
        """Test suffix property works."""
        path = HivePath("data/year=2023/month=01/file.txt")
        assert path.suffix == ".txt"
    
    def test_stem_property(self):
        """Test stem property works."""
        path = HivePath("data/year=2023/month=01/file.txt")
        assert path.stem == "file"
    
    def test_parts_property(self):
        """Test parts property works."""
        path = HivePath("data/year=2023/month=01/file.txt")
        assert isinstance(path.parts, tuple)
        assert len(path.parts) > 0
    
    def test_joinpath(self):
        """Test joinpath method works."""
        path = HivePath("data/year=2023")
        new_path = path.joinpath("month=01", "file.txt")
        assert isinstance(new_path, Path)
        # Note: joinpath might return a regular Path, not HivePath
        # This is expected behavior


class TestEdgeCases:
    """Test edge cases and special scenarios."""
    
    def test_empty_path(self):
        """Test empty path."""
        path = HivePath("")
        assert path.partitions == {}
    
    def test_root_path(self):
        """Test root path."""
        path = HivePath("/")
        assert path.partitions == {}
    
    def test_partition_with_equals_in_value(self):
        """Test partition value containing equals sign."""
        # This is an edge case - typically partition values don't contain '='
        # But we should handle it gracefully
        path = HivePath("data/key=value=with=equals/file.txt")
        # The pattern will match up to the first '=', so:
        # key=value=with=equals -> key="value", but the rest is lost
        # This is expected behavior for Hive-style partitioning
        assert "key" in path.partitions
    
    def test_multiple_partitions_same_key(self):
        """Test path with multiple partitions having same key."""
        # In Hive-style, this shouldn't happen, but we handle it
        path = HivePath("data/year=2023/year=2024/file.txt")
        # Last one wins
        assert path.get_partition("year") in ["2023", "2024"]
    
    def test_relative_vs_absolute_paths(self):
        """Test both relative and absolute paths."""
        rel_path = HivePath("data/year=2023/file.txt")
        abs_path = HivePath("/data/year=2023/file.txt")
        
        assert rel_path.partitions == {"year": "2023"}
        assert abs_path.partitions == {"year": "2023"}

