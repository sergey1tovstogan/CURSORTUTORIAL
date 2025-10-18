"""
Frequency Table Generator Module

This module provides multiple implementations for creating frequency tables
from iterables, with comprehensive documentation and examples.

Author: Senior Developer
Version: 1.0.0
"""

from collections import Counter, defaultdict
from typing import Any, Dict, List, Hashable, Union
from functools import reduce
import operator


def frequency_table_simple(items: List[Hashable]) -> Dict[Hashable, int]:
    """
    Create a frequency table using a simple dictionary approach.
    
    Best for: Educational purposes, when you want explicit control.
    Time Complexity: O(n)
    Space Complexity: O(k) where k is number of unique items
    
    Args:
        items: A list of hashable items to count
        
    Returns:
        A dictionary with items as keys and their frequencies as values
        
    Raises:
        TypeError: If any item is not hashable
        
    Example:
        >>> frequency_table_simple(['a', 'b', 'a', 'c', 'a', 'b'])
        {'a': 3, 'b': 2, 'c': 1}
    """
    if not isinstance(items, (list, tuple)):
        raise TypeError(f"Expected list or tuple, got {type(items)}")
    
    freq_table: Dict[Hashable, int] = {}
    
    for item in items:
        # Use get() with default value for cleaner code
        freq_table[item] = freq_table.get(item, 0) + 1
    
    return freq_table


def frequency_table_defaultdict(items: List[Hashable]) -> Dict[Hashable, int]:
    """
    Create a frequency table using defaultdict.
    
    Best for: Cleaner code, avoiding KeyError exceptions.
    Time Complexity: O(n)
    Space Complexity: O(k) where k is number of unique items
    
    Args:
        items: A list of hashable items to count
        
    Returns:
        A dictionary with items as keys and their frequencies as values
        
    Example:
        >>> frequency_table_defaultdict(['a', 'b', 'a', 'c', 'a', 'b'])
        {'a': 3, 'b': 2, 'c': 1}
    """
    freq_table: Dict[Hashable, int] = defaultdict(int)
    
    for item in items:
        freq_table[item] += 1
    
    return dict(freq_table)  # Convert back to regular dict


def frequency_table_counter(items: List[Hashable]) -> Dict[Hashable, int]:
    """
    Create a frequency table using collections.Counter.
    
    Best for: Production code, most Pythonic, additional utility methods.
    Time Complexity: O(n)
    Space Complexity: O(k) where k is number of unique items
    
    Args:
        items: A list of hashable items to count
        
    Returns:
        A dictionary with items as keys and their frequencies as values
        
    Example:
        >>> frequency_table_counter(['a', 'b', 'a', 'c', 'a', 'b'])
        {'a': 3, 'b': 2, 'c': 1}
    """
    return dict(Counter(items))


def frequency_table_advanced(
    items: List[Hashable],
    sort_by: str = "frequency",
    reverse: bool = True,
    min_frequency: int = 1
) -> Dict[Hashable, int]:
    """
    Create a frequency table with advanced features.
    
    Best for: Production scenarios requiring filtering and sorting.
    
    Args:
        items: A list of hashable items to count
        sort_by: 'frequency' (default) or 'item' to sort results
        reverse: Whether to sort in reverse order (default: True)
        min_frequency: Minimum frequency threshold (default: 1)
        
    Returns:
        A dictionary with items as keys and their frequencies as values,
        optionally sorted and filtered
        
    Raises:
        ValueError: If sort_by is not 'frequency' or 'item'
        
    Example:
        >>> frequency_table_advanced(['a', 'b', 'a', 'c', 'a', 'b'], 
        ...                          sort_by='frequency', reverse=True)
        {'a': 3, 'b': 2, 'c': 1}
    """
    if sort_by not in ("frequency", "item"):
        raise ValueError(f"sort_by must be 'frequency' or 'item', got {sort_by}")
    
    # Create base frequency table
    freq_table = Counter(items)
    
    # Filter by minimum frequency
    freq_table = {
        item: count for item, count in freq_table.items()
        if count >= min_frequency
    }
    
    # Sort if requested
    if sort_by == "frequency":
        freq_table = dict(
            sorted(freq_table.items(), key=operator.itemgetter(1), reverse=reverse)
        )
    elif sort_by == "item":
        freq_table = dict(sorted(freq_table.items(), key=operator.itemgetter(0), reverse=reverse))
    
    return freq_table


class FrequencyTableBuilder:
    """
    A builder class for creating frequency tables with fluent interface.
    
    Useful for complex scenarios or multiple operations on the same data.
    
    Example:
        >>> builder = FrequencyTableBuilder(['a', 'b', 'a', 'c'])
        >>> result = builder.min_frequency(2).sort_by_frequency().build()
        >>> result
        {'a': 2}
    """
    
    def __init__(self, items: List[Hashable]):
        """Initialize builder with items."""
        self.items = items
        self._min_freq = 1
        self._sort_method = None
        self._reverse = True
    
    def min_frequency(self, min_freq: int) -> "FrequencyTableBuilder":
        """Set minimum frequency threshold."""
        self._min_freq = min_freq
        return self
    
    def sort_by_frequency(self, reverse: bool = True) -> "FrequencyTableBuilder":
        """Sort by frequency."""
        self._sort_method = "frequency"
        self._reverse = reverse
        return self
    
    def sort_by_item(self, reverse: bool = False) -> "FrequencyTableBuilder":
        """Sort by item."""
        self._sort_method = "item"
        self._reverse = reverse
        return self
    
    def build(self) -> Dict[Hashable, int]:
        """Build and return the frequency table."""
        return frequency_table_advanced(
            self.items,
            sort_by=self._sort_method or "frequency",
            reverse=self._reverse,
            min_frequency=self._min_freq
        )


# ============================================================================
# EXAMPLES AND DEMONSTRATIONS
# ============================================================================

def run_examples():
    """Run comprehensive examples demonstrating all implementations."""
    
    print("=" * 70)
    print("FREQUENCY TABLE EXAMPLES")
    print("=" * 70)
    
    # Test data
    sample_list = ['apple', 'banana', 'apple', 'cherry', 'banana', 'apple', 'date']
    numbers = [1, 2, 1, 3, 2, 1, 4, 2]
    
    print("\n1. SIMPLE APPROACH (Manual Dictionary)")
    print("-" * 70)
    print(f"Input: {sample_list}")
    result = frequency_table_simple(sample_list)
    print(f"Output: {result}")
    print(f"Method: Explicit loop with .get()")
    
    print("\n2. DEFAULTDICT APPROACH")
    print("-" * 70)
    print(f"Input: {numbers}")
    result = frequency_table_defaultdict(numbers)
    print(f"Output: {result}")
    print(f"Method: defaultdict(int)")
    
    print("\n3. COUNTER APPROACH (Recommended for Production)")
    print("-" * 70)
    print(f"Input: {sample_list}")
    result = frequency_table_counter(sample_list)
    print(f"Output: {result}")
    print(f"Method: collections.Counter")
    
    print("\n4. ADVANCED APPROACH - Sorted by Frequency (Descending)")
    print("-" * 70)
    print(f"Input: {sample_list}")
    result = frequency_table_advanced(sample_list, sort_by="frequency", reverse=True)
    print(f"Output: {result}")
    
    print("\n5. ADVANCED APPROACH - Minimum Frequency Filter")
    print("-" * 70)
    print(f"Input: {sample_list}")
    result = frequency_table_advanced(sample_list, min_frequency=2)
    print(f"Output: {result}")
    print(f"Note: Only items with frequency >= 2 are included")
    
    print("\n6. BUILDER PATTERN (Fluent Interface)")
    print("-" * 70)
    print(f"Input: {sample_list}")
    result = (
        FrequencyTableBuilder(sample_list)
        .min_frequency(2)
        .sort_by_frequency(reverse=True)
        .build()
    )
    print(f"Output: {result}")
    print(f"Note: Only items with frequency >= 2, sorted descending")
    
    print("\n7. EDGE CASES")
    print("-" * 70)
    
    # Empty list
    print(f"Empty list: {frequency_table_counter([])}")
    
    # Single item
    print(f"Single item: {frequency_table_counter(['a'])}")
    
    # All same items
    print(f"All same: {frequency_table_counter(['x', 'x', 'x', 'x'])}")
    
    print("\n" + "=" * 70)
    print("END OF EXAMPLES")
    print("=" * 70)


if __name__ == "__main__":
    run_examples()
