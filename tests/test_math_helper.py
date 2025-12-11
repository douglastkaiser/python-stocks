
import unittest

from python_stocks.math_helper import (
    curvature,
    curvature_vectorized,
    moving_average_filter,
    moving_average_filter_vectorized,
    no_delay_moving_average_filter,
    no_delay_moving_average_filter_vectorized,
    no_delay_moving_average_filter_on_that_day_vectorized,
    percentage_difference,
    slope,
    slope_vectorized,
)

class TestMathHelper(unittest.TestCase):

    # all fcn names need test_**
    def test_maf_single(self):
        # Ensure that it can take a non list argument.
        self.assertEqual(1.5, moving_average_filter(1.5, 1))
        # Single element.
        self.assertEqual(1.5, moving_average_filter([1.5], -1))  # n < 1
        self.assertEqual(1.5, moving_average_filter([1.5], 0))  # n < 1
        self.assertEqual(1.5, moving_average_filter([1.5], 1))  # n == length
        self.assertEqual(1.5, moving_average_filter([1.5], 2))  # n > length
        # Multiple elements.
        self.assertEqual(5, moving_average_filter([2, 4, 6], 2))  # n < length
        self.assertEqual(4, moving_average_filter([2, 4, 6], 3))  # n == length
        self.assertEqual(4, moving_average_filter([2, 4, 6], 4))  # n > length


    def test_maf_vectorized(self):
        # Ensure that vectorized can take a non list argument.
        self.assertEqual([1.5], moving_average_filter_vectorized(1.5, 1))
        # Single element vectorized.
        self.assertEqual([1.5], moving_average_filter_vectorized([1.5], -1))  # n < 1
        self.assertEqual([1.5], moving_average_filter_vectorized([1.5], 0))  # n < 1
        self.assertEqual([1.5], moving_average_filter_vectorized([1.5], 1))  # n == length
        self.assertEqual([1.5], moving_average_filter_vectorized([1.5], 2))  # n > length
        # Multiple elements.
        # self.assertEqual([2, 4, 6], moving_average_filter_vectorized([2, 4, 6], 1))
        self.assertEqual([2, 3, 5], moving_average_filter_vectorized([2, 4, 6], 2))
        self.assertEqual([2, 3, 4], moving_average_filter_vectorized([2, 4, 6], 3))
        self.assertEqual([2, 3, 4], moving_average_filter_vectorized([2, 4, 6], 4))


    def test_no_delay_maf_single(self):
        # Ensure that it can take a non list argument.
        self.assertEqual(1.5, no_delay_moving_average_filter(1.5, 1))
        # Single element.
        self.assertEqual(1.5, no_delay_moving_average_filter([1.5], -1))  # n < 1
        self.assertEqual(1.5, no_delay_moving_average_filter([1.5], 0))  # n < 1
        self.assertEqual(1.5, no_delay_moving_average_filter([1.5], 1))  # n == length
        self.assertEqual(1.5, no_delay_moving_average_filter([1.5], 2))  # n > length
        # Multiple elements.
        self.assertEqual(6, no_delay_moving_average_filter([2, 4, 6], 2))  # n < length
        self.assertEqual(6, no_delay_moving_average_filter([2, 4, 6], 3))  # n == length
        self.assertEqual(6, no_delay_moving_average_filter([2, 4, 6], 4))  # n > length


    def test_no_delay_maf_vectorized(self):
        # Ensure that vectorized can take a non list argument.
        self.assertEqual([1.5], no_delay_moving_average_filter_vectorized(1.5, 1))
        # Single element vectorized.
        self.assertEqual([1.5], no_delay_moving_average_filter_vectorized([1.5], -1))  # n < 1
        self.assertEqual([1.5], no_delay_moving_average_filter_vectorized([1.5], 0))  # n < 1
        self.assertEqual([1.5], no_delay_moving_average_filter_vectorized([1.5], 1))  # n == length
        self.assertEqual([1.5], no_delay_moving_average_filter_vectorized([1.5], 2))  # n > length
        # Multiple elements.
        self.assertEqual([2, 4, 6], no_delay_moving_average_filter_vectorized([2, 4, 6], 1))
        self.assertEqual([2, 4, 6], no_delay_moving_average_filter_vectorized([2, 4, 6], 2))
        self.assertEqual([2, 4, 6], no_delay_moving_average_filter_vectorized([2, 4, 6], 3))
        self.assertEqual([2.5, 4, 5], no_delay_moving_average_filter_vectorized([2, 4, 6], 4))


    def test_percentage_difference(self):
        # No change.
        self.assertEqual(0, percentage_difference(10.5, 10.5))
        # Positive value up.
        self.assertEqual(50, percentage_difference(10, 15))
        self.assertEqual(100, percentage_difference(10, 20))
        self.assertEqual(200, percentage_difference(10, 30))
        # Positive value down and down passed 100%.
        self.assertEqual(-50, percentage_difference(20, 10))
        self.assertEqual(-100, percentage_difference(20, 0))
        self.assertEqual(-200, percentage_difference(20, -20))
        # Negative value up, down, and passed 100%.
        self.assertEqual(-50, percentage_difference(-10, -15))
        self.assertEqual(50, percentage_difference(-10, -5))
        self.assertEqual(100, percentage_difference(-10, 0))
        self.assertEqual(200, percentage_difference(-10, 10))


    def test_slope(self):
        # Single elements.
        self.assertEqual(0, slope(0, 2))
        self.assertEqual(0, slope(1.5, 2))
        # Single element vectors.
        self.assertEqual(0, slope([1.5], 2))
        # Multiple element vectors. Positive slope.
        self.assertEqual(0, slope([2, 3], -1))
        self.assertEqual(0, slope([2, 3], 0))
        self.assertEqual(0, slope([2, 3], 1))
        self.assertEqual(1, slope([2, 3], 2))
        self.assertEqual(1, slope([2, 3], 3))
        self.assertEqual(-1, slope([3, 2], 2))
        self.assertEqual(-1, slope([-2, -3], 2))
        self.assertEqual(1, slope([-3, -2], 2))
        self.assertEqual(0, slope([2, 2], 2))
        self.assertEqual(1, slope([10, 2, 3], 2))


    def test_slope_vectorized(self):
        self.assertEqual([0], slope_vectorized(1.5, 2))
        self.assertEqual([0], slope_vectorized([1.5], 2))
        self.assertEqual([0, 1], slope_vectorized([2, 3], 2))
        self.assertEqual([0, 1, 2], slope_vectorized([2, 3, 5], 2))


    def test_curvature(self):
        self.assertEqual(0, curvature(1.5))
        self.assertEqual(0, curvature([1.5]))
        self.assertEqual(0, curvature([1.5, 1.5]))
        self.assertEqual(0, curvature([1.5, 1.5, 1.5]))
        self.assertEqual(1, curvature([2, 1, 1]))
        self.assertEqual(-1, curvature([0, 1, 1]))
        self.assertEqual(1, curvature([10, 2, 1, 1]))


    def test_curvature_vectorized(self):
        self.assertEqual([0], curvature_vectorized(1.5))
        self.assertEqual([0], curvature_vectorized([1.5]))
        self.assertEqual([0, 0], curvature_vectorized([1.5, 1.5]))
        self.assertEqual([0, 0, 0], curvature_vectorized([1.5, 1.5, 1.5]))
        self.assertEqual([0, 0, 1], curvature_vectorized([2, 1, 1]))
        self.assertEqual([0, 0, -1], curvature_vectorized([0, 1, 1]))
        self.assertEqual([0, 0, -2, 2], curvature_vectorized([1, 2, 1, 2]))


if __name__ == "__main__":
    unittest.main()

