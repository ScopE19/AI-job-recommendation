import torch
from sentence_transformers import SentenceTransformer, util
from openai import OpenAI
import os
from dotenv import load_dotenv
load_dotenv()

# Load a pre-trained model for sentence embeddings
model = SentenceTransformer('all-MiniLM-L6-v2')

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_explanation_with_openai(user_text, job_title, job_description):
    prompt = (
        f"User profile: {user_text}\n"
        f"Job title: {job_title}\n"
        f"Job description: {job_description}\n\n"
        f"Explain in 1-2 sentences why this job is a good match for the user:"
    )

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that matches job descriptions to user profiles."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=100
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"(AI explanation unavailable: {e})"
    
def recommend_jobs(user_text, vacancies, top_n=2):
    """
    Recommend vacancies based on similarity between user_text and vacancy descriptions.
    """
    print(f"User text length: {len(user_text)}")  # Debug log
    print(f"Vacancies received: {len(vacancies)}")  # Debug log
    # Encode user text
    user_embedding = model.encode(user_text, convert_to_tensor=True)

    # Filter out vacancies with no description
    valid_vacancies = []
    for v in vacancies:
        desc = v.get("description") or v.get("snippet", "")
        if desc:  # Only include vacancies with some text
            valid_vacancies.append({**v, "description": desc})
    
    print(f"{len(valid_vacancies)} vacancies after description check")  # Debug
    if not valid_vacancies:
        return []

    # Encode all vacancy descriptions
    vacancy_descriptions = [v["description"] for v in valid_vacancies]
    vacancy_embeddings = model.encode(vacancy_descriptions, convert_to_tensor=True)

    # Compute cosine similarities
    similarities = util.cos_sim(user_embedding, vacancy_embeddings)[0]

    # Get top N vacancies
    top_indices = torch.topk(similarities, k=min(top_n, len(similarities))).indices

    # Return top matching vacancies
    recommended = []
    for idx in top_indices:
        vacancy = valid_vacancies[idx]
        title = vacancy.get("title", "Unknown Title")
        description = vacancy.get("description", "") or vacancy.get("snippet", "")
        reason = generate_explanation_with_openai(user_text, title, description)
        recommended.append({
            **vacancy,
            "reason": reason
        })

    return recommended