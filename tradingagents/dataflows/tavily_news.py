import os
from dotenv import load_dotenv
from loguru import logger
from .congressional_signals import get_congressional_trades
from .polymarket_signals import get_polymarket_signals

load_dotenv('/root/limitless-ai/TradingAgents/.env')


def get_news_tavily(ticker: str, start_date: str, end_date: str) -> str:
    """Fetch ticker news via Tavily. Agent-optimized RAG results."""
    try:
        from tavily import TavilyClient
        client = TavilyClient(api_key=os.getenv('TAVILY_API_KEY'))
        query = f'{ticker} stock crypto price news analysis {end_date}'
        results = client.search(query=query, search_depth='basic', max_results=5, include_answer=True)
        if not results:
            return f'No news found for {ticker} via Tavily.'
        output = f'Tavily News for {ticker} ({start_date} to {end_date}):\n\n'
        if results.get('answer'):
            output += f'Summary: {results["answer"]}\n\n'
        for i, r in enumerate(results.get('results', [])[:5], 1):
            output += f'{i}. {r.get("title", "No title")}\n'
            output += f'   Source: {r.get("url", "")}\n'
            output += f'   {r.get("content", "")[:300]}\n\n'
        logger.info(f'Tavily news fetched for {ticker}: {len(results.get("results", []))} articles')
        return output
    except Exception as e:
        logger.warning(f'Tavily news failed for {ticker}: {e}')
        return f'Tavily news unavailable for {ticker}: {str(e)}'


def get_global_news_tavily(curr_date: str, look_back_days: int = 7, limit: int = 10) -> str:
    """
    Fetch global macro/crypto news via Tavily plus congressional signals and
    Polymarket crowd-probability data for the geopolitical reasoning layer.
    """
    output = ''

    # --- Layer 1: Tavily global news ---
    try:
        from tavily import TavilyClient
        client = TavilyClient(api_key=os.getenv('TAVILY_API_KEY'))
        query = f'global crypto market news geopolitical events economic signals {curr_date}'
        results = client.search(query=query, search_depth='basic',
                                max_results=min(limit, 10), include_answer=True, topic='news')
        if results:
            output += f'Global Macro News via Tavily ({curr_date}, last {look_back_days} days):\n\n'
            if results.get('answer'):
                output += f'Summary: {results["answer"]}\n\n'
            for i, r in enumerate(results.get('results', [])[:limit], 1):
                output += f'{i}. {r.get("title", "No title")}\n'
                output += f'   Source: {r.get("url", "")}\n'
                output += f'   {r.get("content", "")[:300]}\n\n'
            logger.info(f'Tavily global news fetched: {len(results.get("results", []))} articles')
    except Exception as e:
        output += f'Tavily global news unavailable: {str(e)}\n'
        logger.warning(f'Tavily global news failed: {e}')

    # --- Layer 2: SEC EDGAR Congressional & Insider Trade Signals ---
    try:
        congressional = get_congressional_trades(lookback_days=14, limit=10)
        output += '\n\n--- SEC EDGAR CONGRESSIONAL & INSIDER TRADE SIGNALS ---\n'
        output += congressional
        logger.info('Congressional signals appended to global news')
    except Exception as ce:
        output += f'\n[Congressional signals unavailable: {ce}]'
        logger.warning(f'Congressional signals failed: {ce}')

    # --- Layer 3: Polymarket Crowd-Probability Signals ---
    try:
        poly = get_polymarket_signals(limit=8)
        output += '\n\n--- POLYMARKET CROWD-PROBABILITY SIGNALS ---\n'
        output += poly
        logger.info('Polymarket signals appended to global news')
    except Exception as pe:
        output += f'\n[Polymarket signals unavailable: {pe}]'
        logger.warning(f'Polymarket signals failed: {pe}')

    return output if output else 'No global intelligence signals available.'
