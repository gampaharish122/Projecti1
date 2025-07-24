from mcp.server.fastmcp import FastMCP
from typing import Dict
import requests

# Constants
PORT = 1111
API_ENDPOINT_MAIN = "https://apidata.globaldata.com/GlobalDataAIHub/api/Content/GetAIHubAPI"
API_ENDPOINT_SOURCE_DATA = "https://apidata.globaldata.com/GlobalDataAIHub/api/Content/GetAIHubAPISourceData"

AUTH_HEADER = {
    "Authorization": "bearer 8eW2w2fE80Rd2a2Z499Sqs8zN8XmbJFJlNiaOBWoXFan9XrTajkQCYcy-5BzOAcquHHbYpiU-X34lcn3sf1T9VMqbx8hMj6QvLFni_-WhOYsSbQAtNyYiOjtdJtGmdtZPiI6Dgf_anJskc7uBh3vXKQSrfJzSdCmdWn6xLMSNc7qTLI_rLwp3UqjgiJYYYSZ_EyjABQqdW-pbPXPN04etgJOue2JP6EAzGFlK2noUVUL64uufY8me7sjnO3yxHoKZdkzBVZ_5pXUDIcbSBnuhAw9TH0n67solaowHZBxptMA9eEosk2S-7Z2q9RjybuIV9CPksX6aZCcxrJq_xoDSl39utzNMsnDCcb0ZRz9zVE",
    "Accept": "application/json"
}

# Initialize MCP server
mcp = FastMCP("GetAIHubApi", stateless_http=True, host="0.0.0.0", port=PORT)

# Helper function to clean source types
def normalize_source_type(source_type: str) -> str:
    """
    Normalizes and formats the source type input.
    """
    allowed_types = {"news", "deals", "filings", "jobs", "socialmedia", "companies","Events", "Reports", "Patents", "Research",  "Financials"}
    source_types = [s.strip().lower() for s in source_type.split(",")]
    filtered = [s.capitalize() for s in source_types if s in allowed_types]
    return ",".join(filtered)

# Tool 1: Dynamic Source Type
@mcp.tool()
def GetAIHubApi(question: str, source_type: str) -> Dict:
    """
    Calls the GlobalData AI Hub SourceData API with dynamic SourceType, question, chunk size, and date range.
Format for date_start and date_end should be DD-MM-YYYY. Use this for getting background information on any factual questions e.g. "What is walmart doing in sustainability"
Choose most relevant source types for given question
Source types explained
SocialMedia - Queries Social Media Data for given Question
News-  Queries News Database
Deals - Queries deals database which has transactions like M&A, investments, partnerships, mergers etc
Filings - Queries company disclosures like Annual Reports, Earnings releases etc.
Companies - Queries business description of companies
In case of multiple types use , separator e.g. Deals,News,Filings
 
Args:
  Question : Query
 SourceType: possible values are SocialMedia, News, Deals, Filings, Companies
    """
    cleaned_source_type = normalize_source_type(source_type)
    url = f"{API_ENDPOINT_MAIN}?SourceType={requests.utils.quote(cleaned_source_type)}&Question={requests.utils.quote(question)}"

    try:
        response = requests.get(url, headers=AUTH_HEADER, timeout=1000)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        return {"error": str(e)}

# Tool 2: Dynamic Source Data with extra parameters
@mcp.tool()
def GetAIHubAPISourceData(question: str, source_type: str, chunk_size: int, date_start: str, date_end: str) -> Dict:
    """
    Calls the GlobalData AI Hub SourceData API with dynamic SourceType, question, chunk size, and date range.

Format for date_start and date_end should be DD-MM-YYYY. Use this for getting background information on any factual questions e.g. "What is walmart doing in sustainability"
 
Calls the GlobalData AI Hub SourceData API with dynamic SourceType, question, chunk size, and date range.

Format for date_start and date_end should be DD-MM-YYYY. Use this for getting background information on any factual questions e.g. "What is walmart doing in sustainability"

Choose most relevant source types for given question

Source types explained

SocialMedia - Queries Social Media Data for given Question

News-  Queries News Database

Deals - Queries deals database which has transactions like M&A, investments, partnerships, mergers etc

Filings - Queries company disclosures like Annual Reports, Earnings releases etc.

Companies - Queries business description of companies

In case of multiple types use , separator e.g. Deals,News,Filings
 
Args:

  Question : Query

  ChunkSize: Number of chunks of background information to load (typically use 30)

  FromDate : Date in format DD-MM-YYYY

  ToDate : Date in the format DD-MM-YYY

  SourceType: possible values are SocialMedia, News, Deals, Filings, Companies
 
    """
    cleaned_source_type = normalize_source_type(source_type)
    params = {
        "SourceType": cleaned_source_type,
        "Question": question,
        "ChunkSize": chunk_size,
        "DateStart": date_start,
        "DateEnd": date_end
    }
    encoded_params = requests.compat.urlencode(params, quote_via=requests.utils.quote)
    url = f"{API_ENDPOINT_SOURCE_DATA}?{encoded_params}"

    try:
        response = requests.get(url, headers=AUTH_HEADER, timeout=1000)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        return {"error": str(e)}

# Start MCP server
if __name__ == "__main__":
    mcp.run(transport="streamable-http")
