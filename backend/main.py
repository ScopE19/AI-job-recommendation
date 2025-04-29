from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from database.fetch_vacancies import fetch_vacancies_from_hh
from ml.matcher import recommend_jobs
import pandas as pd
from typing import Optional
import os
import aiofiles
from docx import Document
import csv
import PyPDF2

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

@app.get("/")
async def root():
    return {"message": "Backend is running"}

def extract_text_from_file(path: str) -> str:
    text = ""
    extension = os.path.splitext(path)[1].lower()

    if extension == ".pdf":
        with open(path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                text += page.extract_text()
    elif extension in [".doc", ".docx"]:
        doc = Document(path)
        for para in doc.paragraphs:
            text += para.text + " "
    elif extension == ".csv":
        with open(path, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                text += " ".join(row) + " "
    else:
        text = ""
    
    return text

@app.post("/recommend")
async def recommend(user_text: str = Form(...), file: Optional[UploadFile] = File(None)):
    # Start with user's skills text
    
    resume_text = user_text.lower()

    extracted_keywords = []

    print(f"Received user_text: {user_text}")  # Debug log
    print(f"File received: {file.filename if file else None}")
    
    # If file is uploaded, process it
    if file:
        file_location = f"temp_{file.filename}"
        async with aiofiles.open(file_location, "wb") as out_file:
            content = await file.read()
            await out_file.write(content)

        # Extract text from resume
        extracted_text = extract_text_from_file(file_location)
        resume_text += " " + extracted_text

        # Special case: if CSV, extract column names as additional skills
        if file.filename.endswith(".csv"):
            df = pd.read_csv(file_location)
            extracted_keywords = df.columns.tolist()
            resume_text += " " + " ".join(extracted_keywords)

        # Clean up temp file
        os.remove(file_location)

    # Now, fetch vacancies
    vacancies = fetch_vacancies_from_hh(user_text)
    print(f"Fetched {len(vacancies)} vacancies")  # Debug log
    # Recommend jobs
    recommended_jobs = recommend_jobs(resume_text, vacancies)

    return {
        "skills_provided": user_text,
        "csv_columns_found": extracted_keywords,
        "recommended_jobs": recommended_jobs,
        "message": "Processed input successfully"
    }