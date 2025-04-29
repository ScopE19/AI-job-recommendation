import requests

def fetch_vacancies_from_hh(query, area="40", per_page=50):
    url = "https://api.hh.ru/vacancies"
    params = {
        "text": query,  # The full user query as the search term
        "area": area,   # Default area code (can be updated for other regions)
        "per_page": per_page,  # Number of results per page
    }
    
    response = requests.get(url, params=params)

    if response.status_code == 200:
        vacancies = response.json().get("items", [])
        
        # Extract relevant job details, including URL, title, and snippet
        job_results = []
        for vacancy in vacancies:
            requirement = vacancy.get("snippet", {}).get("requirement", "")
            responsibility = vacancy.get("snippet", {}).get("responsibility", "")
            full_snippet = f"{requirement} {responsibility}".strip()
            job_details = {
                "title": vacancy.get("name", "No title available"),
                "url": vacancy.get("alternate_url", ""),  # URL to the full job post
                "snippet": full_snippet,
                "description": full_snippet  # Full job description
            }
            job_results.append(job_details)
        
        return job_results
    else:
        # In case of an error or no data found, return an empty list
        return []
