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

def generate_pdf_from_text(text_content):
    html_template = f"""
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{
                font-family: Arial, sans-serif;
                direction: rtl;
                text-align: right;
                line-height: 1.7;
                font-size: 15px;
                padding: 25px;
            }}
            h2 {{
                margin-top: 25px;
                margin-bottom: 10px;
                font-size: 20px;
            }}
            p {{
                margin-bottom: 12px;
            }}
            ul {{
                margin-bottom: 15px;
            }}
        </style>
    </head>
    <body>
        <pre style="white-space: pre-wrap;">{text_content}</pre>
    </body>
    </html>
    """

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        HTML(string=html_template).write_pdf(tmp.name)
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
        أعد صياغة السيرة الذاتية كنص منسق فقط.
        لا تستخدم HTML.
        لا تستخدم Markdown.
        لا تستخدم رموز برمجية.
        فقط نص CV احترافي جاهز للقراءة.
        """

        user_prompt = f"""
        السيرة الذاتية المستخرجة من PDF:
        {cv_text}

        الأوصاف الوظيفية:
        {job_descriptions}

        أعد كتابة السيرة الذاتية كنص منسق فقط.
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

        final_cv_text = response.choices[0].message.content

        st.success("تم إنشاء السيرة الذاتية المحسّنة!")

        st.subheader("السيرة الذاتية بعد التحسين")
        st.text_area("CV النهائي", final_cv_text, height=500)

        pdf_bytes = generate_pdf_from_text(final_cv_text)

        st.download_button(
            label="تحميل ملف PDF النهائي",
            data=pdf_bytes,
            file_name="optimized_cv.pdf",
            mime="application/pdf"
        )
