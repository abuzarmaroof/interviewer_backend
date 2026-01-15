from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from interview_bot import InterviewBot
import pdfplumber
import io
import docx

app = FastAPI()

# ✅ CORS (for React)
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
     "https://ai-interviewer-c4nl.onrender.com"
    # add your deployed frontend URL here later
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

bot = InterviewBot()

# ------------------ FILE TEXT EXTRACTION ------------------

def extract_text_from_pdf_bytes(file_bytes: bytes):
    text = ""
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            t = page.extract_text()
            if t:
                text += t + "\n"
    return text.strip()


def extract_text_from_file(file: UploadFile):
    filename = file.filename.lower()
    content = file.file.read()

    # PDF
    if filename.endswith(".pdf"):
        return extract_text_from_pdf_bytes(content)

    # TXT
    elif filename.endswith(".txt"):
        try:
            return content.decode("utf-8", errors="ignore")
        except:
            return ""

    # DOCX
    elif filename.endswith(".docx"):
        try:
            doc = docx.Document(io.BytesIO(content))
            return "\n".join(p.text for p in doc.paragraphs)
        except:
            return ""

    else:
        return ""

# ------------------ API ROUTES ------------------

@app.post("/start_interview")
async def start_interview(
    name: str = Form(...),
    topic: str = Form(""),
    difficulty: str = Form("Intermediate"),
    mode: str = Form("Conceptual"),
    resume: UploadFile = File(None),
    notes: UploadFile = File(None),
):
    resume_text = ""
    notes_text = ""

    if resume:
        resume_text = extract_text_from_file(resume)
        print("✅ Resume text length:", len(resume_text))

    if notes:
        notes_text = extract_text_from_file(notes)
        print("✅ Notes text length:", len(notes_text))

    setup = {
        "name": name,
        "topic": topic,
        "difficulty": difficulty,
        "mode": mode,
        "resume_text": resume_text,
        "notes_text": notes_text,
    }

    return bot.start_interview(setup)


@app.post("/chat")
async def chat(request: Request):
    data = await request.json()

    if "message" not in data:
        return {"ended": False, "message": "Invalid request"}

    result = bot.ask_question(data["message"])

    # If bot returned full report
    if isinstance(result, dict) and result.get("ended") is True:
        return result

    # Normal message
    if isinstance(result, dict) and "message" in result:
        return {
            "ended": False,
            "message": result["message"]
        }

    # Fallback
    return {
        "ended": False,
        "message": str(result)
    }


@app.get("/")
def root():
    return {"status": "AIVA backend running"}
