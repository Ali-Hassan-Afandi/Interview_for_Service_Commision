import streamlit as st
from datetime import datetime
import os
from fpdf import FPDF
from groq import Groq
import re
import base64

# ---------------------- Background Styling ----------------------
def set_background(image_path):
    with open(image_path, "rb") as f:
        img_data = f.read()
    b64_img = base64.b64encode(img_data).decode()
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/png;base64,{b64_img}");
            background-size: cover;
            background-position: center;
        }}
        .main {{
            background-color: rgba(255, 255, 255, 0.9);
            border-radius: 10px;
            padding: 2rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}
        .stTextInput>div>div>input, .stSelectbox>div>div>select {{
            background-color: rgba(255, 255, 255, 0.8);
            border: 1px solid #1e3c72;
        }}
        .stButton>button {{
            background: linear-gradient(to right, #1e3c72, #2a5298);
            color: white;
            border: none;
            padding: 0.5rem 2rem;
            border-radius: 25px;
            font-weight: bold;
        }}
        .stDownloadButton>button {{
            background: linear-gradient(to right, #2a5298, #1e3c72);
            color: white;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )


# ---------------------- GROQ API Function ----------------------
def get_groq_response(prompt: str) -> str:
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        return "ERROR: GROQ_API_KEY not set in environment variables."

    try:
        client = Groq(api_key=api_key)

        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8,
            max_tokens=2000,
            top_p=1,
            stream=False
        )

        return completion.choices[0].message["content"]

    except Exception as e:
        return f"GROQ API Error: {str(e)}"


# ---------------------- Clean Text ----------------------
def sanitize_text(text):
    return re.sub(r'[^\x00-\x7F]+', ' ', text)

# ---------------------- PDF Generator ----------------------
class PDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 12)
        self.set_text_color(40, 40, 40)
        self.cell(0, 10, '"Success is where preparation and opportunity meet." - Bobby Unser', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.set_text_color(100, 100, 100)
        footer_text = f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Pace GK Academy"
        self.cell(0, 10, footer_text, 0, 0, 'C')

def create_pdf(interview_text, note_text, name):
    pdf = PDF()
    pdf.add_page()

    pdf.set_font("Times", "B", 18)
    pdf.cell(0, 10, f"Mock Interview: {name}", ln=1, align='C')
    pdf.ln(10)

    pdf.set_font("Times", "", 12)
    for line in sanitize_text(interview_text).split('\n'):
        if line.strip():
            pdf.multi_cell(0, 8, line.strip())
    pdf.ln(8)

    pdf.set_font("Times", "B", 14)
    pdf.cell(0, 10, "Special Note", ln=1)
    pdf.set_font("Times", "", 12)
    for line in sanitize_text(note_text).split('\n'):
        if line.strip():
            pdf.multi_cell(0, 8, line.strip())
    
    output_path = f"{name.replace(' ', '_')}_mock_interview.pdf"
    pdf.output(output_path)
    return output_path

# ---------------------- STREAMLIT APP ----------------------
st.set_page_config(
    page_title="Interview Generator",
    page_icon="📘",
    layout="centered",
    initial_sidebar_state="collapsed"
)

set_background("image.jpg")

st.title("Pace GK Academy - Mock Interview Generator")
st.markdown("<h4 style='text-align:center;color:#1e3c72;'>Professional Exam Preparation Toolkit</h4>", unsafe_allow_html=True)

with st.form("interview_form"):
    cols = st.columns(2)
    with cols[0]:
        name = st.text_input("Full Name")
        father_name = st.text_input("Father's Name")
        district = st.text_input("District")
        tehsil = st.text_input("Tehsil")
    with cols[1]:
        bachelors = st.text_input("Bachelor's Degree")
        masters = st.text_input("Master's Degree")
        department_post = st.text_input("Department & Post")
        exam_type = st.selectbox("Exam Type", ["PPSC", "FPSC", "CSS", "PMS", "Other"])
    
    hobby = st.text_input("Hobby")
    fav_personality = st.text_input("Favorite Personality")
    
    submitted = st.form_submit_button("Generate Interview Report")

if submitted:
    if all([name, father_name, district, tehsil, bachelors, masters, department_post, exam_type, hobby, fav_personality]):
        
        interview_prompt = f"""
        Generate a detailed mock interview for the following Pakistani competitive exam candidate:
        Name: {name}
        Father's Name: {father_name}
        District: {district}
        Tehsil: {tehsil}
        Bachelor's Degree: {bachelors}
        Master's Degree: {masters}
        Exam Type: {exam_type}
        Department and Post: {department_post}
        Hobby: {hobby}
        Favorite Personality: {fav_personality}

        Required sections:
        1. Personal introduction questions
        2. District and tehsil geography, culture and administration
        3. Subject-based questions linked to degrees
        4. Department and post-specific technical questions
        5. Pakistan studies, history, Islamic studies
        6. International affairs and geography
        7. Situational judgment & ethical questions
        8. General knowledge and current affairs

        Provide clear, well-structured, numbered interview questions.
        """

        note_prompt = f"""
        Write a motivational note for a candidate applying for the post of {department_post} through {exam_type}.
        Include preparation guidance, important areas to study, and advice on how to answer key questions confidently.
        Tone must be encouraging, respectful, and professional.
        """

        with st.spinner("Generating personalized interview..."):
            interview_text = get_groq_response(interview_prompt)
            note_text = get_groq_response(note_prompt)

        st.success("Interview Generated Successfully")

        with st.expander("Interview Questions"):
            st.write(interview_text)

        with st.expander("Special Note"):
            st.write(note_text)

        file_path = create_pdf(interview_text, note_text, name)

        with open(file_path, "rb") as f:
            st.download_button(
                "Download Full Interview Report",
                f,
                file_name=file_path,
                mime="application/pdf"
            )
    else:
        st.warning("Please complete all fields before proceeding.")

st.markdown("<p style='text-align:center;color:#1e3c72;'>Pace GK Academy | +92 311 750 5369</p>", unsafe_allow_html=True)
