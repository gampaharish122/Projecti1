from mcp.server.fastmcp import FastMCP
from typing import Dict
import requests
from datetime import datetime

# Hardcoded configuration
API_TOKEN = "jSUS2ZMHsdRF7seneARayXzrs2H5pqwdeU4qwSxDq="
OVERALL_API_ENDPOINT = "https://apidata.globaldata.com/GlobalDataSocialMedia/api/Content/GetOverallData"
TIMELINE_API_ENDPOINT = "https://apidata.globaldata.com/GlobalDataSocialMedia/api/Content/GetTimelineData"
TOP_CONCEPTS_API_ENDPOINT = "https://apidata.globaldata.com/GlobalDataSocialMedia/api/Content/GetTopConcepts"
TOP_COMPANIES_API_ENDPOINT = "https://apidata.globaldata.com/GlobalDataSocialMedia/api/Content/GetTopCompanies"
TOP_THEMES_API_ENDPOINT = "https://apidata.globaldata.com/GlobalDataSocialMedia/api/Content/GetTopThemes"
TOP_HASHTAGS_API_ENDPOINT = "https://apidata.globaldata.com/GlobalDataSocialMedia/api/Content/GetTopHashtags"
TOP_CONTRIBUTORS_API_ENDPOINT = "https://apidata.globaldata.com/GlobalDataSocialMedia/api/Content/GetTopContributors"
SOCIAL_MEDIA_POSTS_API_ENDPOINT = "https://apidata.globaldata.com/GlobalDataSocialMedia/api/Content/GetSocialMediaPosts"
INFLUENCER_LISTING_API_ENDPOINT = "https://apidata.globaldata.com/GlobalDataSocialMedia/api/Content/GetInfluencerListing"
PORT = 10000

# Initialize MCP server
mcp = FastMCP("web-search", host="0.0.0.0", port=PORT)

# Validate DD-MM-YYYY format
def validate_date_format(date_str: str) -> str:
    try:
        datetime.strptime(date_str, "%d-%m-%Y")
        return date_str
    except ValueError:
        raise ValueError(f"Invalid date format: '{date_str}'. Use DD-MM-YYYY.")

# Generic API caller
def fetch_data(
    endpoint: str,
    DisplayName: str = "POC",
    Keyword: str = None,
    FromDate: str = None,
    ToDate: str = None,
    add_frequency: bool = False,
    keyword_before_dates: bool = False
) -> Dict:
    # Validate dates if provided
    if FromDate:
        try:
            FromDate = validate_date_format(FromDate)
        except ValueError as e:
            return {"error": str(e)}
    if ToDate:
        try:
            ToDate = validate_date_format(ToDate)
        except ValueError as e:
            return {"error": str(e)}

    url = f"{endpoint}?TokenID={API_TOKEN}&DisplayName={DisplayName}"

    if add_frequency:
        url += "&Frequency=Day"

    if Keyword is not None:
        url += "&SiteName=Disruptor&Source=All&Sentiment=All"
        if keyword_before_dates and FromDate and ToDate:
            url += f"&Keyword={Keyword}&FromDate={FromDate}&ToDate={ToDate}"
        elif FromDate and ToDate:
            url += f"&FromDate={FromDate}&ToDate={ToDate}&Keyword={Keyword}"

    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        return {"error": str(e)}

# Tool: Overall Data
@mcp.tool()
def web_search(Keyword: str, FromDate: str, ToDate: str) -> Dict:
    return fetch_data(OVERALL_API_ENDPOINT, Keyword=Keyword, FromDate=FromDate, ToDate=ToDate)

# Tool: Timeline Data
@mcp.tool()
def GetTimelineData(Keyword: str, FromDate: str, ToDate: str) -> Dict:
    return fetch_data(TIMELINE_API_ENDPOINT, Keyword=Keyword, FromDate=FromDate, ToDate=ToDate, add_frequency=True)

# Tool: Top Concepts Data
@mcp.tool()
def GetTopConcepts(Keyword: str, FromDate: str, ToDate: str) -> Dict:
    return fetch_data(TOP_CONCEPTS_API_ENDPOINT, Keyword=Keyword, FromDate=FromDate, ToDate=ToDate, keyword_before_dates=True)

# Tool: Top Companies Data
@mcp.tool()
def GetTopCompanies(Keyword: str, FromDate: str, ToDate: str) -> Dict:
    return fetch_data(TOP_COMPANIES_API_ENDPOINT, Keyword=Keyword, FromDate=FromDate, ToDate=ToDate)

# Tool: Top Themes Data
@mcp.tool()
def GetTopThemes(Keyword: str, FromDate: str, ToDate: str) -> Dict:
    return fetch_data(TOP_THEMES_API_ENDPOINT, Keyword=Keyword, FromDate=FromDate, ToDate=ToDate)

# Tool: Top Hashtags Data
@mcp.tool()
def GetTopHashtags(Keyword: str, FromDate: str, ToDate: str) -> Dict:
    return fetch_data(TOP_HASHTAGS_API_ENDPOINT, Keyword=Keyword, FromDate=FromDate, ToDate=ToDate)

# Tool: Top Contributors Data
@mcp.tool()
def GetTopContributors(Keyword: str, FromDate: str, ToDate: str) -> Dict:
    return fetch_data(TOP_CONTRIBUTORS_API_ENDPOINT, Keyword=Keyword, FromDate=FromDate, ToDate=ToDate)

# Tool: Social Media Posts Data
@mcp.tool()
def GetSocialMediaPosts(Keyword: str, FromDate: str, ToDate: str) -> Dict:
    return fetch_data(SOCIAL_MEDIA_POSTS_API_ENDPOINT, Keyword=Keyword, FromDate=FromDate, ToDate=ToDate)

# Tool: Influencer Listing (only TokenID and DisplayName in URL)
@mcp.tool()
def GetInfluencerListing() -> Dict:
    """
    Fetch influencers for the hardcoded DisplayName 'POC'.
    """
    url = f"{INFLUENCER_LISTING_API_ENDPOINT}?TokenID={API_TOKEN}&DisplayName=POC"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        # Ensure 'result' is always a dictionary
        if isinstance(data, list):
            return {"result": {"influencers": data}}
        elif isinstance(data, dict):
            return {"result": data}
        else:
            return {"result": {}}
    except requests.RequestException as e:
        return {"result": {"error": str(e)}}

# Start server
if __name__ == "__main__":
    mcp.run(transport="streamable-http")
