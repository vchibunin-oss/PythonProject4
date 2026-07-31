from unittest.mock import Mock, patch

from src.external_api import convert_transaction_to_rub


def test_convert_transaction_to_rub_rub():
    transaction = {
        "operationAmount": {
            "amount": "1500",
            "currency": {
                "code": "RUB"
            }
        }
    }

    assert convert_transaction_to_rub(transaction) == 1500.0


@patch("src.external_api.requests.get")
def test_convert_transaction_to_rub_usd(mock_get):
    mock_response = Mock()
    mock_response.json.return_value = {"result": 9500}
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    transaction = {
        "operationAmount": {
            "amount": "100",
            "currency": {
                "code": "USD"
            }
        }
    }

    assert convert_transaction_to_rub(transaction) == 9500.0
    mock_get.assert_called_once()


@patch("src.external_api.requests.get")
def test_convert_transaction_to_rub_eur(mock_get):
    mock_response = Mock()
    mock_response.json.return_value = {"result": 10500}
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    transaction = {
        "operationAmount": {
            "amount": "100",
            "currency": {
                "code": "EUR"
            }
        }
    }

    assert convert_transaction_to_rub(transaction) == 10500.0
    mock_get.assert_called_once()
