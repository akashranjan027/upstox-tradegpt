import unittest
from unittest.mock import patch, Mock, call
import json # For json.JSONDecodeError and json.dumps
import requests # For requests.exceptions types

# Adjust import path for src.gemini
# This try-except block attempts to handle different execution contexts
try:
    from src import gemini
except ImportError:
    import sys
    import os
    # Add the parent directory of 'src' to sys.path to allow 'from src import gemini'
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
    from src import gemini


class TestGeminiMCPCalls(unittest.TestCase):

    # --- Tests for get_market_data_wrapper ---
    @patch('src.gemini.requests.get')
    def test_get_market_data_success(self, mock_get):
        mock_response = Mock(spec=requests.Response)
        mock_response.status_code = 200
        expected_data = [{"ts": "123", "o": 100, "h": 101, "l": 99, "c": 100, "v": 1000}]
        mock_response.json.return_value = expected_data
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        result = gemini.get_market_data_wrapper(symbol="TESTSYM", days=10, timeframe="5min")
        
        mock_get.assert_called_once_with(
            "http://localhost:5001/mcp/market/get_historical_data",
            params={"symbol": "TESTSYM", "days": 10, "timeframe": "5min"},
            timeout=15
        )
        self.assertEqual(result, expected_data)

    @patch('src.gemini.requests.get')
    def test_get_market_data_http_error(self, mock_get):
        mock_response = Mock(spec=requests.Response)
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        http_error_instance = requests.exceptions.HTTPError(response=mock_response)
        mock_response.raise_for_status.side_effect = http_error_instance
        mock_get.return_value = mock_response

        result = gemini.get_market_data_wrapper(symbol="TESTSYM", days=10)
        
        self.assertIn("error", result)
        self.assertIn("HTTP error calling MCP get_market_data", result["error"])
        self.assertIn("Internal Server Error", result["error"])

    @patch('src.gemini.requests.get')
    def test_get_market_data_network_error(self, mock_get):
        mock_get.side_effect = requests.exceptions.RequestException("Connection refused")

        result = gemini.get_market_data_wrapper(symbol="TESTSYM", days=10)
        
        self.assertIn("error", result)
        self.assertIn("Request error calling MCP get_market_data", result["error"])
        self.assertIn("Connection refused", result["error"])

    @patch('src.gemini.requests.get')
    def test_get_market_data_json_decode_error(self, mock_get):
        mock_response = Mock(spec=requests.Response)
        mock_response.status_code = 200
        mock_response.json.side_effect = json.JSONDecodeError("Expecting value", "doc", 0)
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        result = gemini.get_market_data_wrapper(symbol="TESTSYM", days=10)

        self.assertIn("error", result)
        self.assertEqual(result["error"], "Invalid JSON response from MCP get_market_data")

    # --- Tests for get_current_price_wrapper ---
    @patch('src.gemini.requests.get')
    def test_get_current_price_success(self, mock_get):
        mock_response = Mock(spec=requests.Response)
        mock_response.status_code = 200
        expected_data = {"last_price": 150.75}
        mock_response.json.return_value = expected_data
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        result = gemini.get_current_price_wrapper(symbol="TESTSYM")
        
        mock_get.assert_called_once_with(
            "http://localhost:5001/mcp/market/get_current_price",
            params={"symbol": "TESTSYM"},
            timeout=15
        )
        self.assertEqual(result, expected_data)

    @patch('src.gemini.requests.get')
    def test_get_current_price_http_error(self, mock_get):
        mock_response = Mock(spec=requests.Response)
        mock_response.status_code = 404
        mock_response.text = "Not Found"
        http_error_instance = requests.exceptions.HTTPError(response=mock_response)
        mock_response.raise_for_status.side_effect = http_error_instance
        mock_get.return_value = mock_response

        result = gemini.get_current_price_wrapper(symbol="TESTSYM")
        
        self.assertIn("error", result)
        self.assertIn("HTTP error calling MCP get_current_price", result["error"])
        self.assertIn("Not Found", result["error"])

    @patch('src.gemini.requests.get')
    def test_get_current_price_network_error(self, mock_get):
        mock_get.side_effect = requests.exceptions.Timeout("Timeout occurred")

        result = gemini.get_current_price_wrapper(symbol="TESTSYM")
        
        self.assertIn("error", result)
        self.assertIn("Request error calling MCP get_current_price", result["error"])
        self.assertIn("Timeout occurred", result["error"])

    @patch('src.gemini.requests.get')
    def test_get_current_price_json_decode_error(self, mock_get):
        mock_response = Mock(spec=requests.Response)
        mock_response.status_code = 200
        mock_response.json.side_effect = json.JSONDecodeError("Bad JSON", "doc", 0)
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        result = gemini.get_current_price_wrapper(symbol="TESTSYM")

        self.assertIn("error", result)
        self.assertEqual(result["error"], "Invalid JSON response from MCP get_current_price")

    # --- Tests for place_buy_order_wrapper ---
    @patch('src.gemini.requests.post')
    def test_place_buy_order_success(self, mock_post):
        mock_response = Mock(spec=requests.Response)
        mock_response.status_code = 200
        expected_data = {"order_id": "12345", "status": "PLACED"}
        mock_response.json.return_value = expected_data
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        payload = {"symbol": "TESTBUY", "quantity": 10, "order_type": "LIMIT", "price": 100.0}
        result = gemini.place_buy_order_wrapper(
            symbol="TESTBUY", quantity=10, order_type="LIMIT", price=100.0
        )
        
        mock_post.assert_called_once_with(
            "http://localhost:5002/mcp/trading/place_buy_order",
            headers={'Content-Type': 'application/json'},
            data=json.dumps(payload),
            timeout=15
        )
        self.assertEqual(result, expected_data)

    @patch('src.gemini.requests.post')
    def test_place_buy_order_http_error(self, mock_post):
        mock_response = Mock(spec=requests.Response)
        mock_response.status_code = 400
        mock_response.text = "Bad Request: Invalid quantity"
        http_error_instance = requests.exceptions.HTTPError(response=mock_response)
        mock_response.raise_for_status.side_effect = http_error_instance
        mock_post.return_value = mock_response
        
        payload = {"symbol": "TESTBUY", "quantity": -5, "order_type": "MARKET", "price": None}
        result = gemini.place_buy_order_wrapper(symbol="TESTBUY", quantity=-5, order_type="MARKET")
        
        self.assertIn("error", result)
        self.assertIn("HTTP error calling MCP place_buy_order", result["error"])
        self.assertIn("Bad Request: Invalid quantity", result["error"])

    @patch('src.gemini.requests.post')
    def test_place_buy_order_network_error(self, mock_post):
        mock_post.side_effect = requests.exceptions.ConnectionError("Failed to connect")

        result = gemini.place_buy_order_wrapper(symbol="TESTBUY", quantity=10)
        
        self.assertIn("error", result)
        self.assertIn("Request error calling MCP place_buy_order", result["error"])
        self.assertIn("Failed to connect", result["error"])

    @patch('src.gemini.requests.post')
    def test_place_buy_order_json_decode_error(self, mock_post):
        mock_response = Mock(spec=requests.Response)
        mock_response.status_code = 200
        mock_response.json.side_effect = json.JSONDecodeError("Malformed JSON", "doc", 0)
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response
        
        result = gemini.place_buy_order_wrapper(symbol="TESTBUY", quantity=10)

        self.assertIn("error", result)
        self.assertEqual(result["error"], "Invalid JSON response from MCP place_buy_order")

    # --- Tests for place_sell_order_wrapper ---
    @patch('src.gemini.requests.post')
    def test_place_sell_order_success(self, mock_post):
        mock_response = Mock(spec=requests.Response)
        mock_response.status_code = 200
        expected_data = {"order_id": "67890", "status": "FILLED"}
        mock_response.json.return_value = expected_data
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        payload = {"symbol": "TESTSELL", "quantity": 5, "order_type": "MARKET", "price": None}
        result = gemini.place_sell_order_wrapper(
            symbol="TESTSELL", quantity=5, order_type="MARKET"
        )
        
        mock_post.assert_called_once_with(
            "http://localhost:5002/mcp/trading/place_sell_order",
            headers={'Content-Type': 'application/json'},
            data=json.dumps(payload),
            timeout=15
        )
        self.assertEqual(result, expected_data)

    @patch('src.gemini.requests.post')
    def test_place_sell_order_http_error(self, mock_post):
        mock_response = Mock(spec=requests.Response)
        mock_response.status_code = 503
        mock_response.text = "Service Unavailable"
        http_error_instance = requests.exceptions.HTTPError(response=mock_response)
        mock_response.raise_for_status.side_effect = http_error_instance
        mock_post.return_value = mock_response
        
        result = gemini.place_sell_order_wrapper(symbol="TESTSELL", quantity=5)
        
        self.assertIn("error", result)
        self.assertIn("HTTP error calling MCP place_sell_order", result["error"])
        self.assertIn("Service Unavailable", result["error"])

    @patch('src.gemini.requests.post')
    def test_place_sell_order_network_error(self, mock_post):
        mock_post.side_effect = requests.exceptions.RequestException("DNS resolution failed")

        result = gemini.place_sell_order_wrapper(symbol="TESTSELL", quantity=5)
        
        self.assertIn("error", result)
        self.assertIn("Request error calling MCP place_sell_order", result["error"])
        self.assertIn("DNS resolution failed", result["error"])

    @patch('src.gemini.requests.post')
    def test_place_sell_order_json_decode_error(self, mock_post):
        mock_response = Mock(spec=requests.Response)
        mock_response.status_code = 200
        mock_response.json.side_effect = json.JSONDecodeError("Garbled JSON", "doc", 0)
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response
        
        result = gemini.place_sell_order_wrapper(symbol="TESTSELL", quantity=5)

        self.assertIn("error", result)
        self.assertEqual(result["error"], "Invalid JSON response from MCP place_sell_order")

    # --- Tests for get_portfolio_wrapper ---
    @patch('src.gemini.requests.get')
    def test_get_portfolio_success(self, mock_get):
        mock_response = Mock(spec=requests.Response)
        mock_response.status_code = 200
        expected_data = [{"symbol": "ABC", "quantity": 100, "avg_price": 50.0}]
        mock_response.json.return_value = expected_data
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        result = gemini.get_portfolio_wrapper()
        
        mock_get.assert_called_once_with(
            "http://localhost:5002/mcp/trading/get_portfolio",
            timeout=15
        )
        self.assertEqual(result, expected_data)

    @patch('src.gemini.requests.get')
    def test_get_portfolio_http_error(self, mock_get):
        mock_response = Mock(spec=requests.Response)
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        http_error_instance = requests.exceptions.HTTPError(response=mock_response)
        mock_response.raise_for_status.side_effect = http_error_instance
        mock_get.return_value = mock_response

        result = gemini.get_portfolio_wrapper()
        
        self.assertIn("error", result)
        self.assertIn("HTTP error calling MCP get_portfolio", result["error"])
        self.assertIn("Unauthorized", result["error"])

    @patch('src.gemini.requests.get')
    def test_get_portfolio_network_error(self, mock_get):
        mock_get.side_effect = requests.exceptions.RequestException("Host unreachable")

        result = gemini.get_portfolio_wrapper()
        
        self.assertIn("error", result)
        self.assertIn("Request error calling MCP get_portfolio", result["error"])
        self.assertIn("Host unreachable", result["error"])

    @patch('src.gemini.requests.get')
    def test_get_portfolio_json_decode_error(self, mock_get):
        mock_response = Mock(spec=requests.Response)
        mock_response.status_code = 200
        mock_response.json.side_effect = json.JSONDecodeError("Invalid format", "doc", 0)
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        result = gemini.get_portfolio_wrapper()

        self.assertIn("error", result)
        self.assertEqual(result["error"], "Invalid JSON response from MCP get_portfolio")


if __name__ == '__main__':
    unittest.main()
