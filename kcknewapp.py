import streamlit as st
import pandas as pd
import os
from datetime import datetime
import re
from io import BytesIO

st.set_page_config(
    page_title="School Management System",
    page_icon="🎓",
    layout="wide"
)

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "ADMIN001"

def init_session_state():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'login_attempts' not in st.session_state:
        st.session_state.login_attempts = 0

def check_url_params():
    try:
        query_params = st.query_params
        if 'logout' in query_params or 'reset' in query_params:
            st.session_state.logged_in = False
            st.session_state.login_attempts = 0
            st.query_params.clear()
            st.rerun()
    except:
        pass

init_session_state()
check_url_params()

STUDENT_FILE = "students_data.xlsx"
FEE_STRUCTURE_FILE = "fee_structure.xlsx"
FEE_PAYMENTS_FILE = "fee_payments.xlsx"

STANDARDS = ["Playgroup", "Nursery", "Junior KG", "Senior KG", "1st", "2nd"]
AGE_OPTIONS = [2, 3, 4, 5, 6, 7, 8, 9, 10]
FEE_TYPES = ["Admission Fees", "Tuition Fees", "Activity Fees", "Uniform Fees", "Stationary", "Term Fees", "Lunch Fees"]
PAYMENT_MODES = ["Cash", "Online/UPI", "Cheque", "Card", "Bank Transfer"]

def initialize_student_excel():
    if not os.path.exists(STUDENT_FILE):
        df = pd.DataFrame(columns=['Student_ID', 'Name', 'Address', 'Age', 'Blood_Group', 'Father_Phone', 'Mother_Phone', 'Aadhar_Details', 'Standard'])
        df.to_excel(STUDENT_FILE, index=False)
        return df
    else:
        return pd.read_excel(STUDENT_FILE)

def initialize_fee_structure():
    if not os.path.exists(FEE_STRUCTURE_FILE):
        df = pd.DataFrame(columns=['Fee_ID', 'Standard', 'Fee_Type', 'Amount', 'Payment_Frequency', 'Academic_Year'])
        df.to_excel(FEE_STRUCTURE_FILE, index=False)
        return df
    else:
        return pd.read_excel(FEE_STRUCTURE_FILE)

def initialize_fee_payments():
    if not os.path.exists(FEE_PAYMENTS_FILE):
        df = pd.DataFrame(columns=['Receipt_No', 'Student_ID', 'Student_Name', 'Standard', 'Payment_Date', 'Amount_Paid', 'Payment_Mode', 'Fee_Type', 'Academic_Year', 'Remarks'])
        df.to_excel(FEE_PAYMENTS_FILE, index=False)
        return df
    else:
        return pd.read_excel(FEE_PAYMENTS_FILE)

def load_students():
    try:
        df = pd.read_excel(STUDENT_FILE)
        if df.empty:
            df = pd.DataFrame(columns=['Student_ID', 'Name', 'Address', 'Age', 'Blood_Group', 'Father_Phone', 'Mother_Phone', 'Aadhar_Details', 'Standard'])
        return df
    except Exception as e:
        st.error(f"Error loading students: {e}")
        return pd.DataFrame(columns=['Student_ID', 'Name', 'Address', 'Age', 'Blood_Group', 'Father_Phone', 'Mother_Phone', 'Aadhar_Details', 'Standard'])

def load_fee_structure():
    try:
        return pd.read_excel(FEE_STRUCTURE_FILE)
    except:
        return pd.DataFrame(columns=['Fee_ID', 'Standard', 'Fee_Type', 'Amount', 'Payment_Frequency', 'Academic_Year'])

def load_fee_payments():
    try:
        return pd.read_excel(FEE_PAYMENTS_FILE)
    except:
        return pd.DataFrame(columns=['Receipt_No', 'Student_ID', 'Student_Name', 'Standard', 'Payment_Date', 'Amount_Paid', 'Payment_Mode', 'Fee_Type', 'Academic_Year', 'Remarks'])

def save_students(df):
    try:
        df.to_excel(STUDENT_FILE, index=False)
        return True
    except Exception as e:
        st.error(f"Error saving students: {e}")
        return False

def save_fee_structure(df):
    try:
        df.to_excel(FEE_STRUCTURE_FILE, index=False)
        return True
    except Exception as e:
        st.error(f"Error saving fee structure: {e}")
        return False

def save_fee_payments(df):
    try:
        df.to_excel(FEE_PAYMENTS_FILE, index=False)
        return True
    except Exception as e:
        st.error(f"Error saving payments: {e}")
        return False

def generate_student_id(df):
    if df.empty:
        return "STU001"
    else:
        last_id = df['Student_ID'].max()
        num = int(last_id[3:]) + 1
        return f"STU{num:03d}"

def generate_receipt_no(df):
    if df.empty:
        return f"RCP{datetime.now().strftime('%Y%m')}001"
    else:
        last_receipt = df['Receipt_No'].max()
        try:
            num = int(last_receipt[-3:]) + 1
            return f"RCP{datetime.now().strftime('%Y%m')}{num:03d}"
        except:
            return f"RCP{datetime.now().strftime('%Y%m')}001"

def generate_fee_id(df):
    if df.empty:
        return "FEE001"
    else:
        last_id = df['Fee_ID'].max()
        num = int(last_id[3:]) + 1
        return f"FEE{num:03d}"

def validate_aadhar(aadhar):
    pattern = r'^\d{12}$'
    return bool(re.match(pattern, str(aadhar).replace(" ", "")))

def validate_phone(phone):
    pattern = r'^[6-9]\d{9}$'
    return bool(re.match(pattern, str(phone).replace(" ", "").replace("-", "")))

def calculate_pending_fees(student_id, students_df, fee_structure_df, payments_df):
    student = students_df[students_df['Student_ID'] == student_id]
    if student.empty:
        return 0, 0, 0
    standard = student.iloc[0]['Standard']
    total_fees = fee_structure_df[fee_structure_df['Standard'] == standard]['Amount'].sum()
    total_paid = payments_df[payments_df['Student_ID'] == student_id]['Amount_Paid'].sum()
    pending = total_fees - total_paid
    return total_fees, total_paid, pending

def login_page():
    st.markdown("""<style>.login-container{max-width:400px;margin:50px auto;padding:40px;background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);border-radius:15px;box-shadow:0 10px 30px rgba(0,0,0,0.3)}.login-title{color:white;text-align:center;font-size:32px;font-weight:bold;margin-bottom:30px}.login-subtitle{color:#e0e0e0;text-align:center;margin-bottom:30px}.logo-container{text-align:center;margin-bottom:30px;background:white;padding:20px;border-radius:10px}.logo-placeholder{width:150px;height:150px;margin:0 auto;background:#f0f0f0;border:3px dashed #999;border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:14px;color:#666;text-align:center}</style>""", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="logo-container">', unsafe_allow_html=True)
        logo_path = "school_logo.png"
        if os.path.exists(logo_path):
            st.image(logo_path, width=150)
        else:
            st.markdown("""<div class="logo-placeholder"><div><p style="margin:0;">🏫</p><p style="margin:5px 0 0 0;font-size:12px;">School Logo</p><p style="margin:5px 0 0 0;font-size:10px;">Place 'school_logo.png' here</p></div></div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        st.markdown('<p class="login-title">🎓 School Management</p>', unsafe_allow_html=True)
        st.markdown('<p class="login-subtitle">Admin Login</p>', unsafe_allow_html=True)
        with st.form("login_form"):
            username = st.text_input("👤 Username", placeholder="Enter username")
            password = st.text_input("🔐 Password", type="password", placeholder="Enter password")
            submit = st.form_submit_button("🔓 Login", use_container_width=True)
            if submit:
                if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
                    st.session_state.logged_in = True
                    st.session_state.login_attempts = 0
                    st.success("✅ Login successful!")
                    st.rerun()
                else:
                    st.session_state.login_attempts += 1
                    remaining = 5 - st.session_state.login_attempts
                    if st.session_state.login_attempts >= 5:
                        st.error("🚫 Too many failed attempts. Please contact administrator.")
                    else:
                        st.error(f"❌ Invalid credentials! {remaining} attempts remaining.")
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown("---")
        st.info("**Default Credentials:**\n\n👤 Username: admin\n\n🔐 Password: ADMIN001")

def logout():
    st.session_state.logged_in = False
    st.session_state.login_attempts = 0
    st.rerun()

def main():
    check_url_params()
    if not st.session_state.logged_in:
        login_page()
        return
    st.markdown("""<style>.dashboard-logo{position:fixed;top:70px;right:20px;z-index:999;background:white;padding:10px;border-radius:10px;box-shadow:0 2px 10px rgba(0,0,0,0.1)}.logo-img{width:80px;height:80px;object-fit:contain}.logo-placeholder-dash{width:80px;height:80px;background:#f0f0f0;border:2px dashed #999;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:10px;color:#666;text-align:center}</style>""", unsafe_allow_html=True)
    logo_path = "school_logo.png"
    if os.path.exists(logo_path):
        import base64
        with open(logo_path, "rb") as f:
            img_data = base64.b64encode(f.read()).decode()
        logo_html = f'<div class="dashboard-logo"><img src="data:image/png;base64,{img_data}" class="logo-img"></div>'
        st.markdown(logo_html, unsafe_allow_html=True)
    else:
        st.markdown("""<div class="dashboard-logo"><div class="logo-placeholder-dash"><div><p style="margin:0;">🏫</p><p style="margin:2px 0 0 0;">Logo</p></div></div></div>""", unsafe_allow_html=True)
    col1, col2 = st.columns([8, 1])
    with col1:
        st.title("🎓 School Management System")
    with col2:
        if st.button("🚪 Logout", key="logout_btn"):
            logout()
    st.markdown("---")
    initialize_student_excel()
    initialize_fee_structure()
    initialize_fee_payments()
    st.sidebar.markdown("""
    <style>
    [data-testid="stSidebar"] {
        font-size: 24px;
    }
    [data-testid="stSidebar"] label {
        font-size: 24px !important;
    }
    [data-testid="stSidebar"] .stRadio label {
        font-size: 24px !important;
    }
    [data-testid="stSidebar"] h1 {
        font-size: 32px !important;
    }
    [data-testid="stSidebar"] div[role="radiogroup"] label {
        font-size: 24px !important;
        line-height: 1.8 !important;
    }
    </style>
""", unsafe_allow_html=True)

st.sidebar.title("📚 Navigation")
main_menu = st.sidebar.radio("Main Menu:", ["👨‍🎓 Student Management", "💰 Fees Management"])
if main_menu == "👨‍🎓 Student Management":
    student_menu = st.sidebar.radio("Student Operations:", ["📊 View Students", "➕ Add Student", "✏️ Update Student", "🗑️ Delete Student", "📥 Import Students", "📈 Student Analytics"])
    handle_student_menu(student_menu)
else:
    fees_menu = st.sidebar.radio("Fees Operations:", ["💵 Collect Payment", "📋 View Payments", "🔍 Student Fee History", "⚙️ Fee Structure", "📊 Fees Dashboard", "📄 Reports", "⚠️ Defaulters"])
    handle_fees_menu(fees_menu)

def handle_student_menu(menu):
    students_df = load_students()
    if menu == "📊 View Students":
        st.header("📊 All Students")
        if students_df.empty:
            st.info("No students in the database. Add students to get started!")
        else:
            col1, col2 = st.columns([2, 1])
            with col1:
                search_term = st.text_input("🔍 Search by Name or Student ID:", "")
            with col2:
                filter_standard = st.selectbox("Filter by Class:", ["All"] + sorted(students_df['Standard'].unique().tolist()))
            filtered_df = students_df.copy()
            if search_term:
                filtered_df = filtered_df[filtered_df['Name'].str.contains(search_term, case=False, na=False) | filtered_df['Student_ID'].str.contains(search_term, case=False, na=False)]
            if filter_standard != "All":
                filtered_df = filtered_df[filtered_df['Standard'] == filter_standard]
            st.dataframe(filtered_df, use_container_width=True, height=400)
            st.info(f"📊 Total Students: {len(filtered_df)}")
            buffer = BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                filtered_df.to_excel(writer, index=False, sheet_name='Students')
            buffer.seek(0)
            st.download_button(label="💾 Export to Excel", data=buffer, file_name=f"students_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    elif menu == "➕ Add Student":
        st.header("➕ Add New Student")
        st.markdown("### 📝 Student Registration Form")
        with st.form("add_student_form"):
            st.subheader("👤 Personal Information")
            col1, col2, col3 = st.columns(3)
            with col1:
                name = st.text_input("Full Name *", placeholder="Enter student's full name")
                age = st.selectbox("Age *", ["Select"] + AGE_OPTIONS)
            with col2:
                blood_group = st.selectbox("Blood Group *", ["Select", "A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"])
                standard = st.selectbox("Class/Standard *", ["Select"] + STANDARDS)
            with col3:
                aadhar = st.text_input("Aadhar Card Number *", placeholder="12-digit Aadhar number")
            st.markdown("---")
            st.subheader("📞 Parent Contact Details")
            col1, col2 = st.columns(2)
            with col1:
                father_phone = st.text_input("Father's Phone Number *", placeholder="10-digit mobile number")
            with col2:
                mother_phone = st.text_input("Mother's Phone Number *", placeholder="10-digit mobile number")
            st.markdown("---")
            st.subheader("🏠 Address Information")
            address = st.text_area("Complete Address *", placeholder="Enter complete residential address", height=100)
            st.markdown("---")
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                submit = st.form_submit_button("✅ Add Student", use_container_width=True, type="primary")
            if submit:
                errors = []
                if not name:
                    errors.append("Name is required")
                if standard == "Select":
                    errors.append("Please select a standard")
                if blood_group == "Select":
                    errors.append("Please select blood group")
                if age == "Select":
                    errors.append("Please select age")
                if not address:
                    errors.append("Address is required")
                if not aadhar:
                    errors.append("Aadhar number is required")
                elif not validate_aadhar(aadhar):
                    errors.append("Invalid Aadhar number (must be 12 digits)")
                if not father_phone:
                    errors.append("Father's phone number is required")
                elif not validate_phone(father_phone):
                    errors.append("Invalid father's phone number")
                if not mother_phone:
                    errors.append("Mother's phone number is required")
                elif not validate_phone(mother_phone):
                    errors.append("Invalid mother's phone number")
                if errors:
                    for error in errors:
                        st.error(f"❌ {error}")
                else:
                    new_id = generate_student_id(students_df)
                    new_student = pd.DataFrame({'Student_ID': [new_id], 'Name': [name], 'Address': [address], 'Age': [age], 'Blood_Group': [blood_group], 'Father_Phone': [father_phone], 'Mother_Phone': [mother_phone], 'Aadhar_Details': [aadhar], 'Standard': [standard]})
                    students_df = pd.concat([students_df, new_student], ignore_index=True)
                    if save_students(students_df):
                        st.success(f"✅ Student added successfully! Student ID: {new_id}")
                        st.balloons()
                        st.markdown("---")
                        st.info(f"**Student Details Saved:**\n- **Student ID:** {new_id}\n- **Name:** {name}\n- **Class:** {standard}\n- **Age:** {age}\n- **Blood Group:** {blood_group}")
                    else:
                        st.error("❌ Failed to save student data!")
    elif menu == "✏️ Update Student":
        st.header("✏️ Update Student Information")
        if students_df.empty:
            st.warning("No students available to update!")
        else:
            student_id = st.selectbox("Select Student ID:", students_df['Student_ID'].tolist())
            if student_id:
                student_data = students_df[students_df['Student_ID'] == student_id].iloc[0]
                st.markdown("### Current Student Details")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.info(f"**Name:** {student_data['Name']}")
                    st.info(f"**Class:** {student_data['Standard']}")
                with col2:
                    st.info(f"**Age:** {student_data['Age']}")
                    st.info(f"**Blood Group:** {student_data['Blood_Group']}")
                with col3:
                    st.info(f"**Father's Phone:** {student_data.get('Father_Phone', 'N/A')}")
                    st.info(f"**Mother's Phone:** {student_data.get('Mother_Phone', 'N/A')}")
                st.markdown("---")
                with st.form("update_student_form"):
                    st.subheader("👤 Personal Information")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        name = st.text_input("Full Name *", value=student_data['Name'])
                        try:
                            age_index = AGE_OPTIONS.index(int(student_data['Age']))
                        except (ValueError, TypeError):
                            age_index = 0
                        age = st.selectbox("Age *", AGE_OPTIONS, index=age_index)
                    with col2:
                        blood_group_list = ["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"]
                        try:
                            bg_index = blood_group_list.index(student_data['Blood_Group'])
                        except ValueError:
                            bg_index = 0
                        blood_group = st.selectbox("Blood Group *", blood_group_list, index=bg_index)
                        try:
                            standard_index = STANDARDS.index(student_data['Standard'])
                        except ValueError:
                            standard_index = 0
                        standard = st.selectbox("Class/Standard *", STANDARDS, index=standard_index)
                    with col3:
                        aadhar = st.text_input("Aadhar Card Number *", value=student_data['Aadhar_Details'])
                    st.markdown("---")
                    st.subheader("📞 Parent Contact Details")
                    col1, col2 = st.columns(2)
                    with col1:
                        father_phone = st.text_input("Father's Phone Number *", value=student_data.get('Father_Phone', ''))
                    with col2:
                        mother_phone = st.text_input("Mother's Phone Number *", value=student_data.get('Mother_Phone', ''))
                    st.markdown("---")
                    st.subheader("🏠 Address Information")
                    address = st.text_area("Complete Address *", value=student_data['Address'], height=100)
                    st.markdown("---")
                    col1, col2, col3 = st.columns([1, 1, 1])
                    with col2:
                        update = st.form_submit_button("💾 Update Student", use_container_width=True, type="primary")
                    if update:
                        errors = []
                        if not name:
                            errors.append("Name is required")
                        if not address:
                            errors.append("Address is required")
                        if not aadhar or not validate_aadhar(aadhar):
                            errors.append("Invalid Aadhar number")
                        if not father_phone or not validate_phone(father_phone):
                            errors.append("Invalid father's phone number")
                        if not mother_phone or not validate_phone(mother_phone):
                            errors.append("Invalid mother's phone number")
                        if errors:
                            for error in errors:
                                st.error(f"❌ {error}")
                        else:
                            students_df.loc[students_df['Student_ID'] == student_id, 'Name'] = name
                            students_df.loc[students_df['Student_ID'] == student_id, 'Address'] = address
                            students_df.loc[students_df['Student_ID'] == student_id, 'Age'] = age
                            students_df.loc[students_df['Student_ID'] == student_id, 'Blood_Group'] = blood_group
                            students_df.loc[students_df['Student_ID'] == student_id, 'Father_Phone'] = father_phone
                            students_df.loc[students_df['Student_ID'] == student_id, 'Mother_Phone'] = mother_phone
                            students_df.loc[students_df['Student_ID'] == student_id, 'Aadhar_Details'] = aadhar
                            students_df.loc[students_df['Student_ID'] == student_id, 'Standard'] = standard
                            if save_students(students_df):
                                st.success("✅ Student updated successfully!")
                                st.balloons()
                            else:
                                st.error("❌ Failed to update student data!")
    elif menu == "🗑️ Delete Student":
        st.header("🗑️ Delete Student")
        if students_df.empty:
            st.warning("No students available to delete!")
        else:
            student_id = st.selectbox("Select Student ID to Delete:", students_df['Student_ID'].tolist())
            if student_id:
                student_data = students_df[students_df['Student_ID'] == student_id].iloc[0]
                st.markdown("### 📋 Student Details to be Deleted:")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.write(f"**Name:** {student_data['Name']}")
                    st.write(f"**Class:** {student_data['Standard']}")
                    st.write(f"**Age:** {student_data['Age']}")
                with col2:
                    st.write(f"**Blood Group:** {student_data['Blood_Group']}")
                    st.write(f"**Aadhar:** {student_data['Aadhar_Details']}")
                with col3:
                    st.write(f"**Father's Phone:** {student_data.get('Father_Phone', 'N/A')}")
                    st.write(f"**Mother's Phone:** {student_data.get('Mother_Phone', 'N/A')}")
                st.write(f"**Address:** {student_data['Address']}")
                st.markdown("---")
                st.error("⚠️ **Warning:** This action cannot be undone! All student data and associated fee records will be permanently deleted.")
                col1, col2, col3 = st.columns([1, 1, 1])
                with col2:
                    if st.button("🗑️ Confirm Delete", type="primary", use_container_width=True):
                        students_df = students_df[students_df['Student_ID'] != student_id]
                        if save_students(students_df):
                            st.success("✅ Student deleted successfully!")
                            st.rerun()
                        else:
                            st.error("❌ Failed to delete student!")
    elif menu == "📥 Import Students":
        st.header("📥 Import Students from Excel")
        st.info("📋 **Excel File Requirements:**\n- Must have columns: Name, Address, Age, Blood_Group, Father_Phone, Mother_Phone, Aadhar_Details, Standard\n- Standard must be: Playgroup, Nursery, Junior KG, Senior KG, 1st, or 2nd\n- Blood Group: A+, A-, B+, B-, O+, O-, AB+, AB-\n- Age: 2-10\n- Aadhar: 12 digits\n- Phone: 10 digits (Indian mobile)")
        st.subheader("📥 Step 1: Download Template")
        template_df = pd.DataFrame({'Name': ['Sample Student'], 'Address': ['Sample Address, City'], 'Age': [5], 'Blood_Group': ['A+'], 'Father_Phone': ['9876543210'], 'Mother_Phone': ['9876543211'], 'Aadhar_Details': ['123456789012'], 'Standard': ['Playgroup']})
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            template_df.to_excel(writer, index=False, sheet_name='Students')
        buffer.seek(0)
        st.download_button(label="📥 Download Excel Template", data=buffer, file_name="student_import_template.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        st.markdown("---")
        st.subheader("📤 Step 2: Upload Your Excel File")
        uploaded_file = st.file_uploader("Choose an Excel file", type=['xlsx', 'xls'])
        if uploaded_file is not None:
            try:
                import_df = pd.read_excel(uploaded_file)
                st.subheader("📊 Preview of Uploaded Data")
                st.dataframe(import_df.head(10), use_container_width=True)
                st.info(f"Total rows in file: {len(import_df)}")
                required_columns = ['Name', 'Address', 'Age', 'Blood_Group', 'Father_Phone', 'Mother_Phone', 'Aadhar_Details', 'Standard']
                missing_columns = [col for col in required_columns if col not in import_df.columns]
                if missing_columns:
                    st.error(f"❌ Missing required columns: {', '.join(missing_columns)}")
                else:
                    valid_rows = []
                    invalid_rows = []
                    for idx, row in import_df.iterrows():
                        errors = []
                        if pd.isna(row['Name']) or str(row['Name']).strip() == '':
                            errors.append("Name is empty")
                        if row['Standard'] not in STANDARDS:
                            errors.append(f"Invalid Standard: {row['Standard']}")
                        valid_blood_groups = ["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"]
                        if row['Blood_Group'] not in valid_blood_groups:
                            errors.append(f"Invalid Blood Group: {row['Blood_Group']}")
                        try:
                            age = int(row['Age'])
                            if age not in AGE_OPTIONS:
                                errors.append(f"Age must be between 2-10, got: {age}")
                        except:
                            errors.append(f"Invalid Age: {row['Age']}")
                        if not validate_aadhar(str(row['Aadhar_Details'])):
                            errors.append("Invalid Aadhar (must be 12 digits)")
                        if not validate_phone(str(row['Father_Phone'])):
                            errors.append("Invalid father's phone number")
                        if not validate_phone(str(row['Mother_Phone'])):
                            errors.append("Invalid mother's phone number")
                        if errors:
                            invalid_rows.append({'Row': idx + 2, 'Errors': ', '.join(errors)})
                        else:
                            valid_rows.append(row)
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("✅ Valid Rows", len(valid_rows))
                    with col2:
                        st.metric("❌ Invalid Rows", len(invalid_rows))
                    if invalid_rows:
                        st.warning("⚠️ Some rows have errors:")
                        error_df = pd.DataFrame(invalid_rows)
                        st.dataframe(error_df, use_container_width=True)
                    if valid_rows:
                        st.markdown("---")
                        st.subheader("Import Options")
                        import_mode = st.radio("Choose import mode:", ["Append to existing data", "Replace all existing data"])
                        skip_duplicates = st.checkbox("Skip duplicate Aadhar numbers", value=True)
                        if st.button("📥 Import Students", type="primary"):
                            valid_df = pd.DataFrame(valid_rows)
                            if skip_duplicates and not students_df.empty:
                                existing_aadhars = set(students_df['Aadhar_Details'].astype(str))
                                valid_df = valid_df[~valid_df['Aadhar_Details'].astype(str).isin(existing_aadhars)]
                                st.info(f"📊 After removing duplicates: {len(valid_df)} students to import")
                            if len(valid_df) > 0:
                                new_students = []
                                for _, row in valid_df.iterrows():
                                    if import_mode == "Append to existing data":
                                        new_id = generate_student_id(students_df)
                                        students_df = pd.concat([students_df, pd.DataFrame([{'Student_ID': new_id}])], ignore_index=True)
                                    else:
                                        new_id = generate_student_id(pd.DataFrame(new_students) if new_students else pd.DataFrame())
                                    new_students.append({'Student_ID': new_id, 'Name': row['Name'], 'Address': row['Address'], 'Age': int(row['Age']), 'Blood_Group': row['Blood_Group'], 'Father_Phone': row['Father_Phone'], 'Mother_Phone': row['Mother_Phone'], 'Aadhar_Details': row['Aadhar_Details'], 'Standard': row['Standard']})
                                new_df = pd.DataFrame(new_students)
                                if import_mode == "Replace all existing data":
                                    final_df = new_df
                                else:
                                    final_df = pd.concat([students_df, new_df], ignore_index=True)
                                    final_df = final_df[final_df['Name'].notna()]
                                if save_students(final_df):
                                    st.success(f"✅ Successfully imported {len(new_students)} students!")
                                    st.balloons()
                                else:
                                    st.error("❌ Failed to save imported data!")
                            else:
                                st.warning("⚠️ No valid students to import after filtering!")
            except Exception as e:
                st.error(f"❌ Error reading file: {str(e)}")
    elif menu == "📈 Student Analytics":
        st.header("📈 Student Analytics")
        if students_df.empty:
            st.info("No data available for analytics!")
        else:
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Students", len(students_df))
            with col2:
                st.metric("Total Classes", students_df['Standard'].nunique())
            with col3:
                avg_age = students_df['Age'].astype(float).mean()
                st.metric("Average Age", f"{avg_age:.1f}")
            with col4:
                most_common_bg = students_df['Blood_Group'].mode()[0]
                st.metric("Most Common Blood Group", most_common_bg)
            st.markdown("---")
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Students by Class")
                standard_counts = students_df['Standard'].value_counts().sort_index()
                st.bar_chart(standard_counts)
            with col2:
                st.subheader("Students by Blood Group")
                blood_group_counts = students_df['Blood_Group'].value_counts()
                st.bar_chart(blood_group_counts)
            st.markdown("---")
            st.subheader("Age Distribution")
            age_counts = students_df['Age'].astype(int).value_counts().sort_index()
            st.line_chart(age_counts)

def handle_fees_menu(menu):
    students_df = load_students()
    fee_structure_df = load_fee_structure()
    payments_df = load_fee_payments()
    if menu == "💵 Collect Payment":
        st.header("💵 Collect Fee Payment")
        if students_df.empty:
            st.warning("⚠️ No students found! Please add students first.")
            return
        with st.form("payment_form"):
            col1, col2 = st.columns(2)
            with col1:
                student_id = st.selectbox("Select Student *", students_df['Student_ID'].tolist())
                if student_id:
                    student = students_df[students_df['Student_ID'] == student_id].iloc[0]
                    st.info(f"**Name:** {student['Name']}\n\n**Class:** {student['Standard']}")
                    total_fee, paid, pending = calculate_pending_fees(student_id, students_df, fee_structure_df, payments_df)
                    st.metric("Pending Fees", f"₹{pending:.2f}")
                fee_type = st.selectbox("Fee Type *", FEE_TYPES)
                amount = st.number_input("Amount (₹) *", min_value=0.0, step=100.0)
            with col2:
                payment_date = st.date_input("Payment Date *", datetime.now())
                payment_mode = st.selectbox("Payment Mode *", PAYMENT_MODES)
                academic_year = st.text_input("Academic Year *", value=f"{datetime.now().year}-{datetime.now().year+1}")
                remarks = st.text_area("Remarks", placeholder="Optional notes")
            submit = st.form_submit_button("💰 Process Payment", type="primary")
            if submit:
                if not student_id or amount <= 0:
                    st.error("❌ Please fill all required fields!")
                else:
                    receipt_no = generate_receipt_no(payments_df)
                    new_payment = pd.DataFrame({'Receipt_No': [receipt_no], 'Student_ID': [student_id], 'Student_Name': [student['Name']], 'Standard': [student['Standard']], 'Payment_Date': [payment_date], 'Amount_Paid': [amount], 'Payment_Mode': [payment_mode], 'Fee_Type': [fee_type], 'Academic_Year': [academic_year], 'Remarks': [remarks]})
                    payments_df = pd.concat([payments_df, new_payment], ignore_index=True)
                    if save_fee_payments(payments_df):
                        st.success(f"✅ Payment processed successfully! Receipt No: {receipt_no}")
                        st.balloons()
                        st.markdown("---")
                        st.subheader("📄 Payment Receipt")
                        receipt_col1, receipt_col2 = st.columns(2)
                        with receipt_col1:
                            st.write(f"**Receipt No:** {receipt_no}")
                            st.write(f"**Date:** {payment_date}")
                            st.write(f"**Student ID:** {student_id}")
                            st.write(f"**Name:** {student['Name']}")
                        with receipt_col2:
                            st.write(f"**Class:** {student['Standard']}")
                            st.write(f"**Amount:** ₹{amount:.2f}")
                            st.write(f"**Mode:** {payment_mode}")
                            st.write(f"**Fee Type:** {fee_type}")
                    else:
                        st.error("❌ Failed to save payment!")
    elif menu == "📋 View Payments":
        st.header("📋 All Fee Payments")
        if payments_df.empty:
            st.info("No payment records found!")
        else:
            col1, col2, col3 = st.columns(3)
            with col1:
                search_term = st.text_input("🔍 Search by Student ID/Name:")
            with col2:
                fee_type_filter = st.selectbox("Filter by Fee Type:", ["All"] + FEE_TYPES)
            with col3:
                payment_mode_filter = st.selectbox("Filter by Payment Mode:", ["All"] + PAYMENT_MODES)
            filtered_df = payments_df.copy()
            if search_term:
                filtered_df = filtered_df[filtered_df['Student_ID'].str.contains(search_term, case=False, na=False) | filtered_df['Student_Name'].str.contains(search_term, case=False, na=False)]
            if fee_type_filter != "All":
                filtered_df = filtered_df[filtered_df['Fee_Type'] == fee_type_filter]
            if payment_mode_filter != "All":
                filtered_df = filtered_df[filtered_df['Payment_Mode'] == payment_mode_filter]
            st.dataframe(filtered_df, use_container_width=True, height=400)
            st.info(f"📊 Total Payments: {len(filtered_df)} | Total Amount: ₹{filtered_df['Amount_Paid'].sum():.2f}")
            buffer = BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                filtered_df.to_excel(writer, index=False, sheet_name='Payments')
            buffer.seek(0)
            st.download_button(label="💾 Export Payments to Excel", data=buffer, file_name=f"fee_payments_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    elif menu == "🔍 Student Fee History":
        st.header("🔍 Student Fee History")
        if students_df.empty:
            st.warning("No students found!")
        else:
            student_id = st.selectbox("Select Student:", students_df['Student_ID'].tolist())
            if student_id:
                student = students_df[students_df['Student_ID'] == student_id].iloc[0]
                col1, col2 = st.columns(2)
                with col1:
                    st.write("### Student Details")
                    st.write(f"**Name:** {student['Name']}")
                    st.write(f"**Class:** {student['Standard']}")
                    st.write(f"**Age:** {student['Age']}")
                with col2:
                    st.write("### Fee Summary")
                    total_fee, paid, pending = calculate_pending_fees(student_id, students_df, fee_structure_df, payments_df)
                    st.metric("Total Fee Structure", f"₹{total_fee:.2f}")
                    st.metric("Total Paid", f"₹{paid:.2f}")
                    st.metric("Pending", f"₹{pending:.2f}")
                st.markdown("---")
                st.subheader("Payment History")
                student_payments = payments_df[payments_df['Student_ID'] == student_id]
                if student_payments.empty:
                    st.info("No payment history found for this student.")
                else:
                    st.dataframe(student_payments, use_container_width=True)
                    buffer = BytesIO()
                    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                        student_payments.to_excel(writer, index=False, sheet_name='Payment_History')
                    buffer.seek(0)
                    st.download_button(label="💾 Export Student History", data=buffer, file_name=f"student_{student_id}_history_{datetime.now().strftime('%Y%m%d')}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    elif menu == "⚙️ Fee Structure":
        st.header("⚙️ Fee Structure Management")
        tab1, tab2 = st.tabs(["📋 View Structure", "➕ Add/Update Fee"])
        with tab1:
            if fee_structure_df.empty:
                st.info("No fee structure defined. Add fee structure to get started!")
            else:
                st.dataframe(fee_structure_df, use_container_width=True)
                buffer = BytesIO()
                with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                    fee_structure_df.to_excel(writer, index=False, sheet_name='Fee_Structure')
                buffer.seek(0)
                st.download_button(label="💾 Export Fee Structure", data=buffer, file_name=f"fee_structure_{datetime.now().strftime('%Y%m%d')}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        with tab2:
            with st.form("fee_structure_form"):
                col1, col2 = st.columns(2)
                with col1:
                    standard = st.selectbox("Class *", STANDARDS)
                    fee_type = st.selectbox("Fee Type *", FEE_TYPES)
                    amount = st.number_input("Amount (₹) *", min_value=0.0, step=100.0)
                with col2:
                    payment_frequency = st.selectbox("Payment Frequency *", ["One-time", "Monthly", "Quarterly", "Half-Yearly", "Yearly"])
                    academic_year = st.text_input("Academic Year *", value=f"{datetime.now().year}-{datetime.now().year+1}")
                submit = st.form_submit_button("💾 Save Fee Structure", type="primary")
                if submit:
                    if not standard or not fee_type or amount <= 0:
                        st.error("❌ Please fill all required fields!")
                    else:
                        existing = fee_structure_df[(fee_structure_df['Standard'] == standard) & (fee_structure_df['Fee_Type'] == fee_type) & (fee_structure_df['Academic_Year'] == academic_year)]
                        if not existing.empty:
                            fee_structure_df.loc[(fee_structure_df['Standard'] == standard) & (fee_structure_df['Fee_Type'] == fee_type) & (fee_structure_df['Academic_Year'] == academic_year), 'Amount'] = amount
                            fee_structure_df.loc[(fee_structure_df['Standard'] == standard) & (fee_structure_df['Fee_Type'] == fee_type) & (fee_structure_df['Academic_Year'] == academic_year), 'Payment_Frequency'] = payment_frequency
                            message = "updated"
                        else:
                            fee_id = generate_fee_id(fee_structure_df)
                            new_fee = pd.DataFrame({'Fee_ID': [fee_id], 'Standard': [standard], 'Fee_Type': [fee_type], 'Amount': [amount], 'Payment_Frequency': [payment_frequency], 'Academic_Year': [academic_year]})
                            fee_structure_df = pd.concat([fee_structure_df, new_fee], ignore_index=True)
                            message = "added"
                        if save_fee_structure(fee_structure_df):
                            st.success(f"✅ Fee structure {message} successfully!")
                        else:
                            st.error("❌ Failed to save fee structure!")
    elif menu == "📊 Fees Dashboard":
        st.header("📊 Fees Dashboard")
        if payments_df.empty and fee_structure_df.empty:
            st.info("No fee data available!")
            return
        st.subheader("📈 Summary Metrics")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            total_collected = payments_df['Amount_Paid'].sum() if not payments_df.empty else 0
            st.metric("Total Collected", f"₹{total_collected:,.2f}")
        with col2:
            total_expected = fee_structure_df['Amount'].sum() * len(students_df) if not fee_structure_df.empty and not students_df.empty else 0
            st.metric("Total Expected", f"₹{total_expected:,.2f}")
        with col3:
            pending_total = total_expected - total_collected
            st.metric("Total Pending", f"₹{pending_total:,.2f}")
        with col4:
            collection_rate = (total_collected/total_expected*100) if total_expected > 0 else 0
            st.metric("Collection Rate", f"{collection_rate:.1f}%")
        st.markdown("---")
        if not payments_df.empty:
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("💰 Payment Mode Distribution")
                mode_dist = payments_df['Payment_Mode'].value_counts()
                st.bar_chart(mode_dist)
            with col2:
                st.subheader("📚 Fee Type Collection")
                fee_type_dist = payments_df.groupby('Fee_Type')['Amount_Paid'].sum()
                st.bar_chart(fee_type_dist)
            st.markdown("---")
            st.subheader("🎓 Class-wise Collection")
            standard_collection = payments_df.groupby('Standard')['Amount_Paid'].sum().sort_values(ascending=False)
            st.bar_chart(standard_collection)
    elif menu == "📄 Reports":
        st.header("📄 Generate Reports")
        report_type = st.selectbox("Select Report Type", ["Daily Collection Report", "Monthly Collection Report", "Custom Date Range Report"])
        if report_type == "Daily Collection Report":
            report_date = st.date_input("Select Date", datetime.now())
            if st.button("Generate Report", type="primary"):
                daily_payments = payments_df[pd.to_datetime(payments_df['Payment_Date']).dt.date == report_date]
                if daily_payments.empty:
                    st.warning(f"No payments found for {report_date}")
                else:
                    st.subheader(f"Daily Report - {report_date}")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total Transactions", len(daily_payments))
                    with col2:
                        st.metric("Total Amount", f"₹{daily_payments['Amount_Paid'].sum():,.2f}")
                    with col3:
                        st.metric("Avg Transaction", f"₹{daily_payments['Amount_Paid'].mean():,.2f}")
                    st.dataframe(daily_payments, use_container_width=True)
                    buffer = BytesIO()
                    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                        daily_payments.to_excel(writer, index=False, sheet_name='Daily_Report')
                    buffer.seek(0)
                    st.download_button(label="💾 Download Report", data=buffer, file_name=f"daily_report_{report_date}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    elif menu == "⚠️ Defaulters":
        st.header("⚠️ Defaulters List")
        if students_df.empty or fee_structure_df.empty:
            st.warning("Add students and fee structure to view defaulters!")
            return
        st.info("Students with pending fees")
        defaulters = []
        for _, student in students_df.iterrows():
            student_id = student['Student_ID']
            total_fee, paid, pending = calculate_pending_fees(student_id, students_df, fee_structure_df, payments_df)
            if pending > 0:
                defaulters.append({'Student_ID': student_id, 'Name': student['Name'], 'Class': student['Standard'], 'Total_Fee': total_fee, 'Paid': paid, 'Pending': pending, 'Father_Phone': student.get('Father_Phone', 'N/A'), 'Mother_Phone': student.get('Mother_Phone', 'N/A')})
        if not defaulters:
            st.success("🎉 No defaulters! All students have paid their fees.")
        else:
            defaulters_df = pd.DataFrame(defaulters)
            defaulters_df = defaulters_df.sort_values('Pending', ascending=False)
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Defaulters", len(defaulters_df))
            with col2:
                st.metric("Total Pending Amount", f"₹{defaulters_df['Pending'].sum():,.2f}")
            st.dataframe(defaulters_df, use_container_width=True)
            buffer = BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                defaulters_df.to_excel(writer, index=False, sheet_name='Defaulters')
            buffer.seek(0)
            st.download_button(label="💾 Export Defaulters List", data=buffer, file_name=f"defaulters_list_{datetime.now().strftime('%Y%m%d')}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

if __name__ == "__main__":
    main()
