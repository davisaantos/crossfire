from pytest import raises

from crossfire import NestedColumnError, flatten

DICT_DATA = [
    {
        "answer": 42,
        "contextInfo": {"context1": "info1", "context2": "info2"},
    }
]


def teste_flatten_wrong_nested_columns_value_error():
    with raises(NestedColumnError):
        flatten(DICT_DATA, nested_columns=["wrong"])


def teste_flatten_with_emptylist():
    assert flatten([]) == []


# test the flatten function with a dictionary mocking it to assert _flatten_dict function is being called
def test_flatten_dict():
    flattened_dict = flatten(
        DICT_DATA, nested_columns=["contextInfo", "neighborhood"]
    )
    assert flattened_dict == [
        {
            "answer": 42,
            "contextInfo_context1": "info1",
            "contextInfo_context2": "info2",
        }
    ]
