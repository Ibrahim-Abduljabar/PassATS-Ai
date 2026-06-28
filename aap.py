import streamlit as st
import os
import tempfile
import pdfplumber
from groq import Groq
from weasyprint import HTML

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def extract_pdf_text(file):
    with pdfplumber.open(file) as pdf:
        return "\n".join([page.extract_text() or "" for page in pdf.pages])

def html_to_pdf_bytes(html_content):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        HTML(string=html_content).write_pdf(tmp.name)
        path = tmp.name
    with open(path, "rb") as f:
        return f.read()

st.set_page_config(page_title="PassATS AI", layout="wide")
st.title("PassATS AI — ATS CV Optimizer")

uploaded_pdf = st.file_uploader("ارفع ملف السيرة الذاتية (PDF فقط)", type=["pdf"])

if "job_desc_list" not in st.session_state:
    st.session_state.job_desc_list = [""]

def add_job_desc():
    st.session_state.job_desc_list.append("")

st.subheader("الأوصاف الوظيفية")
for i in range(len(st.session_state.job_desc_list)):
    st.session_state.job_desc_list[i] = st.text_area(
        f"الوصف الوظيفي رقم {i+1}",
        st.session_state.job_desc_list[i],
        height=180
    )

st.button("➕ أضف وصف وظيفي آخر", on_click=add_job_desc)

start = st.button("ابدأ تحسين السيرة الذاتية الآن")

if start:
    if not uploaded_pdf:
        st.error("الرجاء رفع ملف PDF.")
    else:
        cv_text = extract_pdf_text(uploaded_pdf)
        job_descriptions = "\n\n---\n\n".join(st.session_state.job_desc_list)

        system_prompt = """
        أنت خبير عالمي في كتابة السير الذاتية المتوافقة مع ATS.
        أعد صياغة السيرة الذاتية لتتوافق مع جميع الأوصاف الوظيفية.
        أعد الإخراج بصيغة HTML فقط.
        استخدم Inline CSS فقط.
        لا تستخدم Markdown.
        لا تكتب أي نص خارج HTML.
        اجعل التصميم احترافي، أكاديمي، منظم، وخفيف.
        """

        user_prompt = f"""
        السيرة الذاتية المستخرجة من PDF:
        {cv_text}

        الأوصاف الوظيفية:
        {job_descriptions}

        أعد كتابة السيرة الذاتية بصيغة HTML فقط.
        """

        st.info("جاري المعالجة عبر Groq…")

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.1,
        )

        html_output = response.choices[0].message.content

        st.success("تم إنشاء السيرة الذاتية المحسّنة!")

        st.subheader("HTML Preview")
        st.code(html_output, language="html")

        pdf_bytes = html_to_pdf_bytes(html_output)

        st.download_button(
            label="تحميل ملف PDF النهائي",
            data=pdf_bytes,
            file_name="optimized_cv.pdf",
            mime="application/pdf"
        )
