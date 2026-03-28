import requests
from loguru import logger

HEADERS = {'User-Agent': 'LimitlessAI/1.0', 'Accept': 'application/json'}
GAMMA_URL = 'https://gamma-api.polymarket.com/markets'

CRYPTO_KEYWORDS = [
    'bitcoin', 'btc', 'ethereum', 'eth', 'crypto', 'cryptocurrency',
    'federal reserve', 'fed rate', 'interest rate', 'inflation', 'cpi',
    'recession', 'oil price', 'gold', 'stock market', 'nasdaq', 's&p',
    'trump', 'tariff', 'trade war', 'geopolit', 'war', 'sanction'
]


def get_polymarket_signals(limit: int = 5) -> str:
    """
    Fetch crowd-probability signals from Polymarket using the Gamma API.
    Returns active crypto/macro prediction markets with YES probabilities.
    Probabilities above 70% indicate strong crowd consensus.
    """
    try:
        results = []
        for keyword in ['crypto', 'bitcoin', 'fed', 'inflation', 'recession', 'oil']:
            params = {
                'limit': 20,
                'active': 'true',
                'closed': 'false',
                'archived': 'false',
            }
            r = requests.get(GAMMA_URL, params=params, headers=HEADERS, timeout=10)
            if r.status_code != 200:
                continue
            markets = r.json() if isinstance(r.json(), list) else []
            for m in markets:
                q = m.get('question', '').lower()
                if keyword in q and m.get('active') and not m.get('closed'):
                    if m not in results:
                        results.append(m)
            if len(results) >= limit:
                break

        if not results:
            return 'No active crypto/macro Polymarket signals found.'

        output = f'Polymarket Crowd-Probability Signals ({len(results[:limit])} markets):\n'
        output += 'Probabilities > 70% = strong crowd consensus. Use as geopolitical signal weight.\n\n'

        for i, market in enumerate(results[:limit], 1):
            question = market.get('question', 'N/A')
            outcomes = market.get('outcomePrices', '[]')
            end_date = market.get('endDate', 'N/A')[:10] if market.get('endDate') else 'N/A'
            volume = market.get('volume', 0)

            # Parse outcome prices - stored as JSON string '["0.65", "0.35"]'
            try:
                import json
                prices = json.loads(outcomes) if isinstance(outcomes, str) else outcomes
                yes_prob = float(prices[0]) * 100 if prices else None
                signal = 'BULLISH' if yes_prob and yes_prob > 60 else ('BEARISH' if yes_prob and yes_prob < 40 else 'NEUTRAL')
                prob_str = f'{yes_prob:.1f}% YES [{signal}]' if yes_prob else 'N/A'
            except:
                prob_str = 'N/A'
                signal = 'NEUTRAL'

            output += f'{i}. {question[:80]}\n'
            output += f'   Probability: {prob_str} | Ends: {end_date} | Vol: ${float(volume or 0):,.0f}\n\n'

        logger.info(f'Polymarket signals fetched: {len(results[:limit])} active crypto/macro markets')
        return output

    except Exception as e:
        logger.warning(f'Polymarket signals failed: {e}')
        return f'Polymarket signals unavailable: {str(e)}'


# Alias for backwards compatibility
get_crypto_polymarket_signals = get_polymarket_signals
