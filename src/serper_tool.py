import requests
import json
from src.config import SERPER_API_KEY

def search_serper(query: str, type: str = "search", num: int = 10):
    """
    Searches using the Serper API.
    
    Args:
        query: The search query.
        type: 'search' for general results, 'shopping' for shopping results.
        num: Number of results to fetch (default 10).
    """
    if not SERPER_API_KEY:
        return {"error": "SERPER_API_KEY not found in environment variables."}

    url = "https://google.serper.dev/search"
    if type == "shopping":
        url = "https://google.serper.dev/shopping"
        #API endpoint for shopping results
    payload = json.dumps({
        "q": query,
        "num": num
    })
    headers = {
        'X-API-KEY': SERPER_API_KEY,
        'Content-Type': 'application/json'
    }

    try:
        response = requests.request("POST", url, headers=headers, data=payload)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def format_serper_results(results: dict) -> str:
    """Formats Serper JSON results into a readable string string."""
    output = ""
    
    if "shopping" in results:
        output += "## Real-time Shopping Data:\n"
        for item in results["shopping"]:
            title = item.get("title", "No Title")
            source = item.get("source", "Unknown Seller")
            price = item.get("price", "N/A")
            link = item.get("link", "#")
            rating = item.get("rating", "N/A")
            rating_count = item.get("ratingCount", "0")
            
            output += f"- **{title}**\n  - Source: {source}\n  - Price: {price}\n  - Rating: {rating} ({rating_count} reviews)\n  - [Link]({link})\n\n"
            
    elif "organic" in results:
        output += "## Web Search Results:\n"
        for item in results["organic"]:
            title = item.get("title", "No Title")
            snippet = item.get("snippet", "")
            link = item.get("link", "#")
            output += f"- **{title}**\n  - {snippet}\n  - [Read more]({link})\n\n"
            
    elif "error" in results:
        output += f"Error fetching online data: {results['error']}\n"
        
    return output
