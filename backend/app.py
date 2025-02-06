from flask import Flask, request, jsonify
import requests
from flask_cors import CORS
from cache import cache  # Import caching system

app = Flask(__name__)
CORS(app)  # Allows frontend to communicate with this backend

# Initialize cache
cache.init_app(app)

COINGECKO_API_URL = "https://api.coingecko.com/api/v3"


def fetch_data(url):
    """Helper function to fetch data from CoinGecko with error handling."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        return {"error": "Request timed out"}, 504
    except requests.exceptions.HTTPError as e:
        return {"error": f"HTTP error: {e}"}, response.status_code
    except requests.exceptions.RequestException as e:
        return {"error": f"API request failed: {str(e)}"}, 500


@app.route("/search", methods=["GET"])
@cache.cached(timeout=600, query_string=True)  # Cache for 10 minutes
def search_crypto():
    """Search for cryptocurrencies by name."""
    query = request.args.get("query", "").strip().lower()
    
    if not query:
        return jsonify({"error": "Query parameter is required"}), 400

    # Fetch full crypto list once and filter locally
    cached_coins = cache.get("coin_list")
    if not cached_coins:
        coins_response = fetch_data(f"{COINGECKO_API_URL}/coins/list")
        if "error" in coins_response:
            return jsonify(coins_response), 500
        cached_coins = coins_response
        cache.set("coin_list", cached_coins, timeout=600)  # Cache for 10 minutes

    matches = [coin for coin in cached_coins if query in coin["id"]]
    return jsonify(matches[:10])  # Return top 10 matches



@app.route("/crypto/<crypto_id>", methods=["GET"])
@cache.cached(timeout=120)  # Cache for 2 minutes
def get_crypto_info(crypto_id):
    """Get cryptocurrency details by ID."""
    crypto_data = fetch_data(f"{COINGECKO_API_URL}/coins/{crypto_id}")

    # Check if fetch_data() returned an error tuple
    if isinstance(crypto_data, tuple):
        return jsonify({"error": crypto_data[0]}), crypto_data[1]  # Return error message with status code

    # Now we know crypto_data is a dictionary, so we can safely use .get()
    market_data = crypto_data.get("market_data", {})

    result = {
        "name": crypto_data.get("name"),
        "symbol": crypto_data.get("symbol").upper(),
        "price": market_data.get("current_price", {}).get("usd"),
        "market_cap": market_data.get("market_cap", {}).get("usd"),
        "high_24h": market_data.get("high_24h", {}).get("usd"),
        "low_24h": market_data.get("low_24h", {}).get("usd"),
        "ath": market_data.get("ath", {}).get("usd"),
        "atl": market_data.get("atl", {}).get("usd"),
        "price_change_24h": market_data.get("price_change_percentage_24h"),
        "volume": market_data.get("total_volume", {}).get("usd"),
        "last_updated": crypto_data.get("last_updated")
    }

    return jsonify(result)



@app.route("/crypto/<crypto_id>/history", methods=["GET"])
@cache.cached(timeout=600, query_string=True)  # Cache for 10 minutes
def get_crypto_history(crypto_id):
    """Get historical price data."""
    days = request.args.get("days", 7)

    history_data = fetch_data(f"{COINGECKO_API_URL}/coins/{crypto_id}/market_chart?vs_currency=usd&days={days}")
    
    # Check if fetch_data() returned an error
    if isinstance(history_data, tuple):
        return jsonify({"error": history_data[0]}), history_data[1]  # Return error message with status code

    # Now we know history_data is a dictionary, so we can safely use .get()
    history = [{"timestamp": point[0], "price": point[1]} for point in history_data.get("prices", [])]

    return jsonify(history)


if __name__ == "__main__":
    app.run(debug=True)
