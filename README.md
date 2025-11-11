# hive-path

A simple Python package that provides a `pathlib.Path` subclass with functionality for working with Hive-style partitioned paths.

## What is Hive-style Partitioning?

Hive-style partitioning organizes data using directory names in the format `key=value`. This is commonly used in data lakes and big data systems.

Example paths:
```
data/year=2023/month=01/day=15/file.parquet
logs/date=2024-01-01/hour=12/log.txt
```

## Installation

Install in development mode:

```bash
pip install -e .
```

Or install with development dependencies:

```bash
pip install -e ".[dev]"
```

This package uses modern Python packaging with `pyproject.toml` (PEP 518, PEP 621).

## Usage

### Basic Usage

```python
from hive_path import HivePath

# Create a HivePath from a string
path = HivePath("data/year=2023/month=01/day=15/file.parquet")

# Access partition information
print(path.partitions)
# {'year': '2023', 'month': '01', 'day': '15'}

# Get a specific partition value
print(path.get_partition("year"))
# '2023'

# Check if a partition exists
print(path.has_partition("year", "2023"))
# True
```

### Working with Partitions

```python
from hive_path import HivePath

# Create a path with partitions
path = HivePath.with_partitions("data", {"year": "2023", "month": "01"})
print(path)
# data/year=2023/month=01

# Add a partition to an existing path
new_path = path.add_partition("day", "15")
print(new_path)
# data/year=2023/month=01/day=15

# Check multiple partitions
path = HivePath("data/year=2023/month=01/day=15/file.txt")
print(path.has_partition("year", "2023") and path.has_partition("month", "01"))
# True
print(path.has_partition("year", "2022"))
# False
```

### Path Manipulation

```python
from hive_path import HivePath

path = HivePath("data/year=2023/month=01/file.txt")

# Get base path without partitions
base = path.base_path()
print(base)
# data/file.txt

# Get only the partition portion
partitions = path.partition_path()
print(partitions)
# year=2023/month=01
```

### All pathlib.Path Methods Still Work

Since `HivePath` is a subclass of `pathlib.Path`, all standard Path methods are available:

```python
from hive_path import HivePath

path = HivePath("data/year=2023/month=01/file.txt")

# Standard Path operations
print(path.parent)
# data/year=2023/month=01

print(path.name)
# file.txt

print(path.suffix)
# .txt

# Check if path exists (standard Path method)
print(path.exists())
```

## Testing

To run the test suite, first install the development dependencies:

```bash
pip install -r requirements-dev.txt
# or
pip install -e ".[dev]"
```

Then run pytest:

```bash
pytest
```

The test suite includes comprehensive tests for:
- Path creation and instantiation
- Partition parsing and extraction
- Path manipulation methods
- Partition building and filtering
- Compatibility with standard pathlib.Path methods
- Edge cases and special scenarios

## API Reference

### Properties

- `partitions` - Returns a dictionary of all partition key-value pairs

### Methods

- `get_partition(key)` - Get the value of a specific partition key
- `has_partition(key, value=None)` - Check if a partition exists (optionally with a specific value)
- `base_path()` - Get the path without partition directories
- `partition_path()` - Get only the partition portion of the path
- `with_partitions(base, partitions)` - Class method to create a path with partitions
- `add_partition(key, value)` - Create a new path with an additional partition

## License

MIT

