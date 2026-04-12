import requests
from newspaper import Article
from requests.exceptions import ConnectionError, HTTPError, InvalidSchema, InvalidURL, MissingSchema, RequestException, Timeout


def fetch_article(url: str) -> Article | dict[str, str]:
    """Fetches the article content from the URL."""
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

    try:
        # stream=True pauses the function after getting headers
        response = requests.get(url, headers=headers, stream=True, timeout=5)
        response.raise_for_status() # To throw errors and execute the except block

        # Content must be HTML before being passed to article
        content_type = response.headers.get('Content-Type', '')
        if 'text/html' not in content_type:
            return {"Error": "Content received is not HTML."}
        
        article = Article(url)
        article.set_html(response.text)
        article.parse()

        if not article.text.strip():
            return {"Error": "The page was reachable, but we could not extract readable article text."}

        return article

    except (MissingSchema, InvalidSchema, InvalidURL):
        return {"Error": "Please enter a valid URL starting with http:// or https://."}
    except Timeout:
        return {"Error": "The website took too long to respond. Please try again."}
    except ConnectionError:
        return {"Error": "Could not reach this website. Check the URL and try again."}
    except HTTPError as err:
        if err.response is not None:
            status_code = err.response.status_code
        else:
            status_code = None
        if status_code == 404:
            return {"Error": "This page was not found (404). Please verify the URL."}
        if status_code == 403:
            return {"Error": "This website blocked access to the article (403). Try a different source."}
        return {"Error": f"The website returned an error ({status_code or 'unknown status'})."}
    except RequestException:
        return {"Error": "Unable to fetch this URL right now. Please try again."}