import streamlit as st
import os
import tempfile
from groq import Groq
from xhtml2pdf import pisa


client = Groq(api_key=os.environ.get("GROQ_API_KEY"))


def html_to_pdf(html_content):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
        pisa.CreatePDF(html_content, dest=tmp_pdf)
        tmp_pdf_path = tmp_pdf.name

    with open(tmp_pdf_path, "rb") as f:
        pdf_bytes = f.read()

    return pdf_bytes


st.title("PassATS AI — CV Optimizer for ATS Systems")

st.write("أدخل السيرة الذاتية والوصف الوظيفي ليتم إعادة صياغتهما بشكل متوافق 100% مع أنظمة ATS.")

cv_input = st.text_area("CV — السيرة الذاتية", height=250)
job_desc_input = st.text_area("Job Description — الوصف الوظيفي", height=250)

process_btn = st.button("Generate Optimized ATS CV")


if process_btn:
    if not cv_input or not job_desc_input:
        st.error("الرجاء إدخال السيرة الذاتية والوصف الوظيفي.")
    else:
        st.info("جاري المعالجة عبر Groq…")

        system_prompt = """
        أنت خبير في كتابة السير الذاتية المتوافقة مع ATS.
        أعد صياغة السيرة الذاتية بالكامل لتتوافق 100% مع الوصف الوظيفي.
        أعد الإخراج على شكل كود HTML فقط.
        استخدم Inline CSS فقط.
        لا تستخدم Markdown.
        لا تكتب أي نص خارج HTML.
        اجعل التصميم احترافي، أكاديمي، منظم، وخفيف.
        """

        user_prompt = f"""
        السيرة الذاتية:
        {cv_input}

        الوصف الوظيفي:
        {job_desc_input}

        أعد كتابة السيرة الذاتية بصيغة HTML فقط.
        """

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.2,
        )

        html_output = response.choices[0].message.content

        st.success("تم إنشاء السيرة الذاتية بنجاح!")

        st.subheader("HTML Output Preview")
        st.code(html_output, language="html")

        pdf_bytes = html_to_pdf(html_output)

        st.download_button(
            label="Download PDF",
            data=pdf_bytes,
            file_name="optimized_cv.pdf",
            mime="application/pdf"
        )
