
import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image
from deepface import DeepFace
from datetime import datetime
import pytz
import os

st.set_page_config(page_title="Face Attendance App", layout="centered")

st.title("🧑‍💼 Face Recognition Attendance System")

# Directory for reference images
os.makedirs("images", exist_ok=True)

# Upload reference images
st.subheader("1. Upload Reference Images (Named as 'name.jpg')")
ref_images = st.file_uploader("Upload one or more reference images", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
if ref_images:
    for img in ref_images:
        with open(os.path.join("images", img.name), "wb") as f:
            f.write(img.getbuffer())
    st.success("✅ Reference images uploaded successfully!")

# Attendance marking function
def mark_attendance(name):
    file_path = "attendance.csv"
    ist = pytz.timezone('Asia/Kolkata')
    now = datetime.now(ist)
    date = now.strftime("%Y-%m-%d")
    time = now.strftime("%H:%M:%S")
    new_entry = pd.DataFrame([[name, date, time]], columns=["Name", "Date", "Time"])
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        df = pd.concat([df, new_entry], ignore_index=True)
    else:
        df = new_entry
    df.to_csv(file_path, index=False)

# Upload live image
st.subheader("2. Upload Live Image to Recognize")
test_image = st.file_uploader("Upload image for attendance", type=["jpg", "jpeg", "png"])
if test_image:
    test_img_path = "test.jpg"
    with open(test_img_path, "wb") as f:
        f.write(test_image.getbuffer())

    st.image(test_img_path, caption="Uploaded Image", use_column_width=True)

    reference_images = os.listdir("images")
    recognized = False

    for ref_img in reference_images:
        ref_path = os.path.join("images", ref_img)
        try:
            result = DeepFace.verify(img1_path=test_img_path, img2_path=ref_path, model_name="Facenet", enforce_detection=False)
            if result["verified"]:
                name = ref_img.split(".")[0]
                mark_attendance(name)
                st.success(f"✅ Attendance marked for {name}")
                recognized = True
                break
        except Exception as e:
            st.warning(f"⚠️ Error verifying {ref_img}: {e}")

    if not recognized:
        st.error("❌ Face not recognized. Try again with a clearer image.")

# Show attendance log
st.subheader("📋 Attendance Log")
if os.path.exists("attendance.csv"):
    df = pd.read_csv("attendance.csv")
    st.dataframe(df)
    st.download_button("📥 Download Attendance CSV", data=df.to_csv(index=False), file_name="attendance.csv", mime="text/csv")
else:
    st.info("No attendance records found yet.")
