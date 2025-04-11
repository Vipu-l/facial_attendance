
import os
import io
import pandas as pd
from datetime import datetime
import pytz
from deepface import DeepFace
from PIL import Image
import streamlit as st

# Ensure image directory exists
os.makedirs("images", exist_ok=True)

# CSV path
CSV_PATH = "attendance.csv"

# Function to mark attendance
def mark_attendance(name):
    if not os.path.exists(CSV_PATH):
        df = pd.DataFrame(columns=["Name", "Date", "Time"])
        df.to_csv(CSV_PATH, index=False)

    df = pd.read_csv(CSV_PATH)

    # Get IST time
    ist = pytz.timezone("Asia/Kolkata")
    now = datetime.now(ist)
    date = now.strftime("%Y-%m-%d")
    time = now.strftime("%H:%M:%S")

    new_entry = pd.DataFrame([[name, date, time]], columns=["Name", "Date", "Time"])
    df = pd.concat([df, new_entry], ignore_index=True)
    df.to_csv(CSV_PATH, index=False)
    return time, date

# Streamlit App
st.set_page_config(page_title="Face Attendance", layout="centered")
st.title("🧑‍💼 Face Recognition Attendance System")

tab1, tab2, tab3 = st.tabs(["📷 Register Reference Image", "✅ Mark Attendance", "📋 View/Export Log"])

# Register Tab
with tab1:
    st.header("Register a Person")
    name = st.text_input("Enter Name")
    image_file = st.file_uploader("Upload Reference Image", type=["jpg", "jpeg", "png"])

    if st.button("Register") and name and image_file:
        img = Image.open(image_file).convert("RGB")
        img.save(f"images/{name}.jpg")
        st.success(f"{name} registered successfully!")

# Attendance Tab
with tab2:
    st.header("Mark Attendance")

    method = st.radio("Select Input Method:", ["📁 Upload Image", "📸 Capture from Webcam"])
    input_image = None

    if method == "📁 Upload Image":
        uploaded = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"], key="upload")
        if uploaded:
            input_image = Image.open(uploaded).convert("RGB")

    elif method == "📸 Capture from Webcam":
        cam_image = st.camera_input("Take a photo")
        if cam_image:
            input_image = Image.open(cam_image).convert("RGB")

    if st.button("Check Attendance") and input_image:
        input_image.save("test.jpg")
        recognized = False

        for ref_img in os.listdir("images"):
            try:
                result = DeepFace.verify(
                    img1_path="test.jpg",
                    img2_path=os.path.join("images", ref_img),
                    model_name="Facenet",
                    enforce_detection=False
                )
                if result["verified"]:
                    name = os.path.splitext(ref_img)[0]
                    time, date = mark_attendance(name)
                    st.success(f"✅ {name} recognized at {time} on {date}")
                    recognized = True
                    break
            except Exception as e:
                st.warning(f"Error with {ref_img}: {e}")

        if not recognized:
            st.error("❌ Face not recognized. Try again with a clearer image.")

# Attendance Log Tab
with tab3:
    st.header("Attendance Log")

    if os.path.exists(CSV_PATH):
        df = pd.read_csv(CSV_PATH)
        st.dataframe(df)

        towrite = io.BytesIO()
        df.to_excel(towrite, index=False, sheet_name="Attendance")
        towrite.seek(0)

        st.download_button(
            "📥 Download as Excel",
            towrite,
            file_name="attendance.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.info("No attendance records found yet.")
