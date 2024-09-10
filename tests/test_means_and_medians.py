import indicatory.names as names

from polars import DataFrame

from indicatory.means_medians import (
    simple_moving_average,
    simple_moving_averages,
    moving_median,
)


def test_simple_moving_averages():
    test_data = DataFrame(
        {
            "A": [1.0, 2.0, 2.0, 3.0, 4.0],
            "B": [2.0, 3.0, 3.0, 4.0, 5.0],
            "C": [3.0, 4.0, 4.0, 5.0, 6.0],
        }
    )
    sma_column_name = names.sma("A", 3)
    expected = (None, None, 1.6666666666666667, 2.3333333333333335, 3.0)
    result = simple_moving_average(dataframe=test_data, window_size=3, column_name="A")
    assert tuple(result[sma_column_name]) == expected

    result = simple_moving_averages(
        dataframe=test_data, window_sizes=[2, 3], column_names=["A", "B"]
    )
    sma_a_2 = names.sma("A", 2)
    sma_a_3 = names.sma("A", 3)
    sma_b_2 = names.sma("B", 2)
    sma_b_3 = names.sma("B", 3)
    result_columns = set(result.columns)
    assert {sma_a_2, sma_a_3, sma_b_2, sma_b_3}.issubset(result_columns)
    assert names.sma("C", 2) not in result_columns
    assert names.sma("C", 3) not in result_columns

    assert tuple(result[sma_a_2]) == (None, 1.5, 2.0, 2.5, 3.5)
    assert tuple(result[sma_b_3]) == (
        None,
        None,
        2.6666666666666665,
        3.3333333333333335,
        4.0,
    )


def test_moving_median():
    test_data = DataFrame({"A": [1.0, 2.0, 2.0, 3.0, 4.0]})
    result_1 = moving_median(test_data, window_size=3, column_name="A")[
        names.mm("A", 3)
    ]
    result_2 = moving_median(test_data, window_size=4, column_name="A")[
        names.mm("A", 4)
    ]
    assert tuple(result_1) == (None, None, 2.0, 2.0, 3.0)
    assert tuple(result_2) == (None, None, None, 2.0, 2.5)
