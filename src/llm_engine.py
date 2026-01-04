from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
import os
import re
from urllib.parse import urlparse
from src.rag_pipeline import get_retriever
from src.serper_tool import search_serper, format_serper_results
from src.config import OPENAI_API_KEY, DATA_DIR


def _enrich_shopping_with_links(shopping_data: dict, search_data: dict) -> str:
    """
    Match shopping results with direct links from organic search.
    Returns formatted markdown with enriched data.
    """
    output = "## Real-time Shopping Data (with Direct Links):\n\n"
    
    # Extract organic links by domain (store ALL links, not just first)
    organic_links = {}  # domain -> list of links
    if "organic" in search_data:
        for item in search_data["organic"]:
            link = item.get("link", "")
            title = item.get("title", "")
            if link and not link.startswith("https://www.google.com"):
                # Extract domain
                try:
                    domain = urlparse(link).netloc.lower()
                    # Remove www. for matching
                    domain = domain.replace("www.", "")
                    
                    # Store ALL links for this domain
                    if domain not in organic_links:
                        organic_links[domain] = []
                    organic_links[domain].append({"link": link, "title": title})
                except:
                    pass
    
    # Process shopping items
    if "shopping" in shopping_data:
        for item in shopping_data["shopping"]:
            title = item.get("title", "No Title")
            source = item.get("source", "Unknown Seller")
            price = item.get("price", "N/A")
            rating = item.get("rating", "N/A")
            rating_count = item.get("ratingCount", "0")
            
            # Try to match seller to a direct link
            # Default to the Google Shopping link (fallback)
            direct_link = item.get("link")
            
            source_lower = source.lower()
            
            # Extract base seller name (before dash/hyphen if present)
            # e.g., "eBay - seller-name" -> "ebay"
            # e.g., "Walmart - Seller" -> "walmart"
            # e.g., "Newegg.com - TrustBasket" -> "newegg.com"
            if ' - ' in source_lower:
                base_seller = source_lower.split(' - ')[0].strip()
            else:
                base_seller = source_lower
            
            # Clean: remove spaces, keep only alphanumeric and dots
            source_clean = re.sub(r'[^a-z0-9.]', '', base_seller)
            
            # Remove common suffixes that might prevent matching
            # e.g. "Gazelle Store" -> "gazellestore" -> "gazelle"
            for suffix in ['store', 'official', 'inc', 'llc', 'shop', 'app', 'online', 'usa']:
                if source_clean.endswith(suffix) and len(source_clean) > len(suffix):
                    source_clean = source_clean[:-len(suffix)]
            
            # Try to match against organic link domains
            best_match = None
            best_match_score = 0
            
            for domain, link_list in organic_links.items():
                # Get main domain part (e.g. "buy.gazelle.com" -> "gazelle")
                # Simple heuristic: take the longest part that isn't a common TLD
                parts = domain.split('.')
                main_domain = max(parts, key=len)
                if main_domain in ['com', 'org', 'net', 'co', 'io', 'fail']:
                    if len(parts) > 1:
                        # Fallback to second to last part if longest is TLD (unlikely but safe)
                        main_domain = parts[-2]
                
                # Calculate domain match score
                domain_score = 0
                
                # Exact match (highest priority)
                if source_clean == domain or domain == source_clean:
                    domain_score = 100
                elif source_clean == main_domain or main_domain == source_clean:
                    domain_score = 95
                # Domain contains seller or seller contains domain
                elif source_clean in domain:
                    domain_score = 80
                elif domain in source_clean:
                    domain_score = 70
                # Partial match (e.g., "ebay" in "ebay.com")
                else:
                    # Extract domain base (e.g., "ebay" from "ebay.com")
                    domain_base = domain.split('.')[0]
                    source_base = source_clean.split('.')[0]
                    
                    if domain_base == source_base:
                        domain_score = 60
                    elif domain_base in source_base or source_base in domain_base:
                        domain_score = 40
                
                # If domain matches reasonably, find best link from this domain
                if domain_score >= 40:
                    for link_info in link_list:
                        link = link_info["link"]
                        link_title = link_info["title"].lower()
                        
                        # Bonus points for title similarity
                        title_score = 0
                        title_lower = title.lower()
                        
                        # Check if key words from shopping title appear in link title
                        title_words = set(re.findall(r'\w+', title_lower))
                        link_words = set(re.findall(r'\w+', link_title))
                        common_words = title_words & link_words
                        
                        similarity = 0
                        if len(title_words) > 0:
                            similarity = (len(common_words) / len(title_words))
                            title_score = similarity * 50 # Max 50 points
                        
                        total_score = domain_score + title_score
                        
                        # Keep best match overall
                        # Store score and link
                        if total_score > best_match_score:
                            best_match_score = total_score
                            best_match = link
            
            # Decide whether to replace the fallback link
            # Logic:
            # 1. If we have a high-confidence match (domain + good title match), use it.
            # 2. If the fallback link is already good (e.g. Google Shopping link for eBay), be conservative about replacing it.
            # 3. For marketplaces like eBay/Amazon, PREFER the fallback link unless title match is VERY strong (>50% words match),
            #    because organic search often gives one generic link for many different specific listings.
            
            should_replace = False
            
            # Base threshold
            if best_match_score >= 90: # High confidence (e.g. Domain 80 + Title 10+)
                 should_replace = True
            
            # Stricter rules for marketplaces where items are unique
            is_marketplace = any(m in source_clean for m in ['ebay', 'amazon', 'walmart', 'etsy', 'poshmark'])
            if is_marketplace:
                # If marketplace, require good title similarity to avoid "one link for all items" problem
                # domain_score is usually 100 or 80.
                # best_match_score = domain_score + (similarity * 50)
                # We want similarity > 0.6 (60%) approximately
                # So if domain is 100, score > 130
                if best_match_score < 130:
                    should_replace = False
            
            if should_replace and best_match:
                direct_link = best_match
            
            # Format output
            output += f"- **{title}**\n"
            output += f"  - Source: {source}\n"
            output += f"  - Price: {price}\n"
            output += f"  - Rating: {rating} ({rating_count} reviews)\n"
            
            if direct_link:
                output += f"  - **Direct Link**: {direct_link}\n"
            else:
                output += f"  - Direct Link: Not found\n"
            
            output += "\n"
    
    return output

def process_query(user_query: str):
    """
    Main logic to process user query using Dynamic RAG.
    """
    
    # 1. Fetch relevant documents from RAG
    print("Retrieving from RAG...")
    try:
        retriever = get_retriever()
        rag_docs = retriever.invoke(user_query)
        rag_context = "\n\n".join([doc.page_content for doc in rag_docs])
    except Exception as e:
        print(f"RAG Retrieval failed (DB might be empty): {e}")
        rag_context = "No internal knowledge base data available."

    # 2. Fetch real-time data using Serper API
    print("Fetching from Serper...")
    
    # If query implies "buy" or "price", use shopping search, else general
    is_shopping = any(keyword in user_query.lower() for keyword in ["buy", "price", "cost", "cheap", "deal", "seller"])
    
    serper_context = ""
    if is_shopping:
        # Fetch both Shopping (for prices) and Search (for direct links)
        print("Fetching Shopping Data...")
        shopping_data = search_serper(user_query, type="shopping", num=10)
        
        print("Fetching Organic Search Data (for links)...")
        search_data = search_serper(user_query, type="search", num=20)
        
        # Match sellers to direct links in Python (more reliable than LLM matching)
        enriched_shopping = _enrich_shopping_with_links(shopping_data, search_data)
        
        serper_context = enriched_shopping
    else:
        search_type = "search"
        serper_data = search_serper(user_query, type=search_type)
        serper_context = format_serper_results(serper_data)

    # 5. Store Serper results back into RAG (Continuous Learning)
    # We save the new data as a markdown file so it gets indexed on the next app restart.
    if serper_context and "Error" not in serper_context:
        import time
        from langchain_core.documents import Document
        # Create a simple safe filename from query
        filename = "".join([c if c.isalnum() else "_" for c in user_query])[:50]
        filepath = os.path.join(DATA_DIR, "updates", f"{filename}_{int(time.time())}.md")
        
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(f"# Query: {user_query}\n\n{serper_context}")
            print(f"saved new knowledge to {filepath}")
        except Exception as e:
            print(f"Failed to save update: {e}")

    # 3. Merge contexts
    final_context = f"""
    === INTERNAL KNOWLEDGE BASE (Product Specs & Seller Info) ===
    {rag_context}
    
    === REAL-TIME WEB DATA (Current Prices & Listings) ===
    {serper_context}
    """
    
    # 4. Generate Answer with LLM
    if not OPENAI_API_KEY:
         return "Error: OPENAI_API_KEY not set. Please set it in your .env file."

    llm = ChatOpenAI(model="gpt-4o", temperature=0, api_key=OPENAI_API_KEY)
    
    template = """You are PriceFinder AI, an expert shopping assistant.
    
    Use the provided context to answer the user's request.
    
    Context:
    {context}
    
    User Request: {question}
    
    Instructions:
    1. If the user asks for product info, combine specs from the internal base with real-time details.
    2. If the user wants to buy or find the best price, compare the Internal Knowledge (if any sellers listed) with Real-Time Web Data.
    3. Highlight the "Cheapest Seller" clearly.
    4. Suggest the "Best Rated" product/seller clearly, considering both price and rating (if available).
    5. Provide a neat "Price Comparison Table" if at 5 to 6 multiple prices and sellers are available and include links to the sellers in that table.
    6. **CRITICAL LINK RULES**:
       - **NEVER GUESS OR CONSTRUCT A LINK**.
       - **ONLY** use a link if it is explicitly provided in the "REAL-TIME WEB DATA" context.
       - **VERIFY** the link matches the seller.
       - **DO NOT** use generic homepage links (e.g. `www.keychron.com` or `www.ebay.com` is BANNED). The link must lead to a specific product page or offer.
       - Use the Direct Link provided in the "REAL-TIME WEB DATA" context. **If the context says "Direct Link: Not found", write "Link not found".**
       - Google Shopping links (starting with `google.com/search` or `google.com/shopping`) ARE ACCEPTABLE if provided in the context as the Direct Link.
    7. Be concise, professional, and helpful.
    
    Answer:"""
    
    prompt = ChatPromptTemplate.from_template(template)
    
    chain = (
        {"context": lambda x: final_context, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    
    response = chain.invoke(user_query)
    return response
