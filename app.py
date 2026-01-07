
import streamlit as st
from datetime import datetime
import os
from fpdf import FPDF
import google.generativeai as genai
import re
import base64

# --- Styling Improvements ---
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

# --- API Client ---
def get_gemini_response(prompt):
    api_key = os.environ.get("groq")
    if not api_key:
        return "❌ GEMINI_API_KEY not set. Please add it in Hugging Face 'Secrets'."

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.0-flash")
    try:
        response = model.generate_content(prompt + " Use plain text format without markdown, avoid symbols like **, #, or any special formatting.")
        return response.text
    except Exception as e:
        return f"❌ Gemini API Error: {str(e)}"

# --- Utility Function to Clean Text ---
def sanitize_text(text):
    return re.sub(r'[^\x00-\x7F]+', ' ', text)

# --- PDF Generation ---
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
        footer_text = f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Created by Mahar Affandi Noor Ghazi - Pace GK Academy | Contact: +92 311 750 5369"
        self.cell(0, 10, footer_text, 0, 0, 'C')

def create_pdf(interview_text, note_text, name):
    pdf = PDF()
    pdf.add_page()

    pdf.set_font("Times", "B", 18)
    pdf.cell(0, 10, f"Mock Interview: {name}", ln=1, align='C')
    pdf.ln(10)

    pdf.set_font("Times", "", 12)
    interview_lines = sanitize_text(interview_text).split('\n')
    for line in interview_lines:
        if line.strip():
            pdf.multi_cell(0, 8, line.strip())
    pdf.ln(10)

    pdf.set_font("Times", "B", 14)
    pdf.cell(0, 10, "Special Note", ln=1)
    pdf.set_font("Times", "", 12)
    note_lines = sanitize_text(note_text).split('\n')
    for line in note_lines:
        if line.strip():
            pdf.multi_cell(0, 8, line.strip())
    
    output_path = f"{name.replace(' ', '_')}_mock_interview.pdf"
    pdf.output(output_path)
    return output_path

# --- Streamlit App ---
st.set_page_config(
    page_title="Interview Generator",
    page_icon="📘",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Set background
set_background("background.jpg")  # Ensure background.jpg is uploaded

st.title("🎓 Pace GK Academy - Mock Interview Generator")
st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <h3 style="color: #1e3c72; font-family: 'Helvetica', sans-serif;">Professional Exam Preparation Toolkit</h3>
        <p style="color: #2a5298;">Crafting Success Stories for PPSC, FPSC, CSS & PMS Aspirants</p>
    </div>
""", unsafe_allow_html=True)

with st.form("interview_form"):
    cols = st.columns(2)
    with cols[0]:
        name = st.text_input("Full Name ✍️")
        father_name = st.text_input("Father's Name 👨")
        district = st.text_input("District of Domicile 🏙️")
        tehsil = st.text_input("Tehsil 🗺️")
    with cols[1]:
        bachelors = st.text_input("Bachelor's Degree 🎓")
        masters = st.text_input("Master's Degree 🎓")
        department_post = st.text_input("Department & Post 🏛️")
        exam_type = st.selectbox("Exam Type 📝", ["PPSC", "FPSC", "CSS", "PMS", "Other"])
    
    hobby = st.text_input("Hobby 🎨")
    fav_personality = st.text_input("Favorite Personality 🌟")
    
    submitted = st.form_submit_button("🚀 Generate Interview Report")

if submitted:
    if all([name, father_name, district, tehsil, bachelors, masters, department_post, exam_type, hobby, fav_personality]):
        interview_prompt = f"""
        Generate a detailed mock interview based on the following Pakistani candidate's profile:
        - Name: {name}
        - Father's Name: {father_name}
        - District: {district}
        - Tehsil: {tehsil}
        - Bachelor's Degree: {bachelors}
        - Master's Degree: {masters}
        - Exam Type: {exam_type}
        - Department and Post: {department_post}
        - Hobby: {hobby}
        - Favorite Personality: {fav_personality}
        Include questions from:
        - Name-based personalities
        - District/Tehsil-specific geography, history, administration
        - Educational background
        - Post/Department-specific issues
        - Pakistan's geography, national & international affairs, sports
        - Government projects related to education
        - Situational judgment and problem-solving
        - Questions related to religion
        - Questions related to pre and post Pakistan history
        - Questions from geography especially countries in international affairs
        Format all in clear, numbered interview questions.
        """
  
        note_prompt = f"""
        Based on the profile of a candidate applying for the post of {department_post} through {exam_type},
        give a special note with motivational advice and suggest specific areas the candidate should study.
        Also suggest good ideas to answer a few important questions.
        Keep the tone encouraging and professional.
        """  

        with st.spinner("🔍 Analyzing profile and crafting personalized interview..."):
            interview_text = get_gemini_response(interview_prompt)
            note_text = get_gemini_response(note_prompt)

        st.success("✅ Interview Generated Successfully!")
        
        with st.expander("📋 View Interview Questions", expanded=True):
            st.write(interview_text)
        
        with st.expander("📝 View Special Note", expanded=False):
            st.write(note_text)

        file_path = create_pdf(interview_text, note_text, name)
        with open(file_path, "rb") as f:
            st.download_button(
                "📄 Download Comprehensive Report",
                f,
                file_name=file_path,
                mime="application/pdf",
                help="Download your personalized interview guide with professional recommendations"
            )
    else:
        st.warning("⚠️ Please complete all fields to proceed.")

st.markdown("""
    <div style="text-align: center; margin-top: 2rem; color: #1e3c72;">
        <p>📞 Contact: +92 311 750 5369 | 📍 Pace GK Academy</p>
        <p>💡 Expert Guidance for Competitive Exam Success</p>
    </div>
""", unsafe_allow_html=True)
