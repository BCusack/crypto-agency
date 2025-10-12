import subprocess
import json
import os
from typing import Dict, Any


def get_bybit_market_data(symbol: str = "BTCUSDT") -> Dict[str, Any]:
    """Get market data from Bybit using the Bybit MCP server via uvx."""
    try:
        # Set up environment variables for the MCP server
        env = os.environ.copy()
        env.update({
            'BYBIT_API_KEY': os.getenv('BYBIT_API_KEY', ''),
            'BYBIT_API_SECRET': os.getenv('BYBIT_API_SECRET', ''),
            'BYBIT_TESTNET': os.getenv('BYBIT_TESTNET', 'true'),  # Default to testnet for safety
            'BYBIT_TRADING_ENABLED': os.getenv('BYBIT_TRADING_ENABLED', 'false')  # Disabled by default
        })

        # Check if API credentials are provided
        if not env['BYBIT_API_KEY'] or not env['BYBIT_API_SECRET']:
            return {
                "status": "error",
                "message": "Bybit API credentials not configured. Please set BYBIT_API_KEY and BYBIT_API_SECRET environment variables."
            }

        # Run the Bybit MCP server using uvx
        cmd = ["uvx", "bybit-mcp", "get_tickers", "--symbol", symbol]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30,
            env=env
        )

        if result.returncode != 0:
            return {
                "status": "error",
                "message": f"Bybit MCP command failed: {result.stderr}"
            }

        # Parse the JSON response
        try:
            data = json.loads(result.stdout)
            return {
                "status": "success",
                "symbol": symbol,
                "data": data
            }
        except json.JSONDecodeError:
            return {
                "status": "error",
                "message": f"Failed to parse response: {result.stdout}"
            }

    except subprocess.TimeoutExpired:
        return {
            "status": "error",
            "message": "Bybit MCP request timed out"
        }
    except FileNotFoundError:
        return {
            "status": "error",
            "message": "uvx not found. Please install uv first."
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error calling Bybit MCP: {str(e)}"
        }


def get_bybit_price(symbol: str = "BTCUSDT") -> Dict[str, Any]:
    """Get current price for a trading pair from Bybit."""
    try:
        # Set up environment variables
        env = os.environ.copy()
        env.update({
            'BYBIT_API_KEY': os.getenv('BYBIT_API_KEY', ''),
            'BYBIT_API_SECRET': os.getenv('BYBIT_API_SECRET', ''),
            'BYBIT_TESTNET': os.getenv('BYBIT_TESTNET', 'true'),
            'BYBIT_TRADING_ENABLED': os.getenv('BYBIT_TRADING_ENABLED', 'false')
        })

        if not env['BYBIT_API_KEY'] or not env['BYBIT_API_SECRET']:
            return {
                "status": "error",
                "message": "Bybit API credentials not configured. Please set BYBIT_API_KEY and BYBIT_API_SECRET environment variables."
            }

        cmd = ["uvx", "bybit-mcp", "get_tickers", "--symbol", symbol]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30,
            env=env
        )

        if result.returncode != 0:
            return {
                "status": "error",
                "message": f"Failed to get price for {symbol}: {result.stderr}"
            }

        try:
            data = json.loads(result.stdout)
            # Extract price from ticker data
            if 'result' in data and 'list' in data['result'] and len(data['result']['list']) > 0:
                ticker = data['result']['list'][0]
                price = ticker.get('lastPrice', 'Unknown')
                return {
                    "status": "success",
                    "symbol": symbol,
                    "price": price,
                    "data": ticker
                }
            else:
                return {
                    "status": "error",
                    "message": f"No price data found for {symbol}"
                }
        except json.JSONDecodeError:
            return {
                "status": "error",
                "message": f"Failed to parse price response: {result.stdout}"
            }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Error getting price: {str(e)}"
        }
