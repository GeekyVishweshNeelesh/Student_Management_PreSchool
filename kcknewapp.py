import streamlit as st
import pandas as pd
import os
from datetime import datetime
import re
from io import BytesIO

# Page configuration
st.set_page_config(
    page_title="School Management System",
    page_icon="🎓",
    layout="wide"
)

# Admin credentials
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "ADMIN001"

# Initialize session state for login
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

# ============================================================================
# INITIALIZE EXCEL FILES
# ============================================================================

def initialize_student_excel():
    if not os.path.exists(STUDENT_FILE):
        df = pd.DataFrame(columns=['Student_ID', 'Name', 'Address', 'Age', 'Blood_Group', 'Father_Phone', 'Mother_Phone', 'Aadhar_Details', 'Standard'])
        df.to_excel(STUDENT_FILE, index=False)
        return df
    else:
        return pd.read_excel(STUDENT_FILE)

def initialize_fee_structure():
    if not os.path.exists(FEE_STRUCTURE_FILE):
        df = pd.DataFrame(columns=['Fee_ID', 'Standard', 'Fee_Type', 'Amount', 'Academic_Year'])
        df.to_excel(FEE_STRUCTURE_FILE, index=False)
        return df
    else:
        return pd.read_excel(FEE_STRUCTURE_FILE)

def initialize_fee_payments():
    if not os.path.exists(FEE_PAYMENTS_FILE):
        df = pd.DataFrame(columns=['Payment_ID', 'Student_ID', 'Fee_Type', 'Amount', 'Payment_Date', 'Payment_Mode', 'Notes'])
        df.to_excel(FEE_PAYMENTS_FILE, index=False)
        return df
    else:
        return pd.read_excel(FEE_PAYMENTS_FILE)

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_next_student_id():
    students_df = initialize_student_excel()
    if len(students_df) == 0:
        return 1001
    return int(students_df['Student_ID'].max()) + 1

def validate_phone(phone):
    pattern = r'^[0-9]{10}$'
    return bool(re.match(pattern, str(phone)))

def validate_aadhar(aadhar):
    pattern = r'^\d{12}$'
    return bool(re.match(pattern, str(aadhar).replace(" ", "")))

# ============================================================================
# LOGIN PAGE
# ============================================================================

def login_page():
    st.markdown("""
        <style>
        .login-container {
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }
        .login-box {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 40px;
            border-radius: 15px;
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
            width: 100%;
            max-width: 400px;
            color: white;
        }
        .login-title {
            text-align: center;
            font-size: 2em;
            font-weight: bold;
            margin-bottom: 30px;
        }
        .logo-container {
            text-align: center;
            margin-bottom: 30px;
        }
        .logo-placeholder {
            width: 120px;
            height: 120px;
            background: linear-gradient(135deg, rgba(255,255,255,0.2), rgba(255,255,255,0.1));
            border: 3px dashed white;
            border-radius: 15px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 60px;
            margin: 0 auto;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        }
        .logo-img-login {
            width: 120px;
            height: 120px;
            object-fit: contain;
            border-radius: 15px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        }
        </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Display school logo
        logo_path = "school_logo.png"
        st.markdown("<div class='logo-container'>", unsafe_allow_html=True)
        
        if os.path.exists(logo_path):
            import base64
            with open(logo_path, "rb") as f:
                img_data = base64.b64encode(f.read()).decode()
            st.markdown(f'<img src="data:image/png;base64,{img_data}" class="logo-img-login">', unsafe_allow_html=True)
        else:
            st.markdown("<div class='logo-placeholder'>🏫</div>", unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("<div class='login-title'>🎓 School Management</div>", unsafe_allow_html=True)
        
        username = st.text_input("👤 Username", key="username_input")
        password = st.text_input("🔐 Password", type="password", key="password_input")
        
        if st.button("🔓 Login", use_container_width=True):
            if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
                st.session_state.logged_in = True
                st.session_state.login_attempts = 0
                st.rerun()
            else:
                st.session_state.login_attempts += 1
                remaining = 5 - st.session_state.login_attempts
                
                if st.session_state.login_attempts >= 5:
                    st.error("🚫 Too many failed attempts. Please contact administrator.")
                else:
                    st.error(f"❌ Invalid credentials! {remaining} attempts remaining.")
        st.markdown("---")
        st.info("**Default Credentials:**\n\n👤 Username: admin\n\n🔐 Password: ADMIN001")

# ============================================================================
# STUDENT MANAGEMENT FUNCTIONS
# ============================================================================

def view_students():
    st.header("📊 View All Students")
    students_df = initialize_student_excel()
    
    if len(students_df) > 0:
        # Responsive column display based on device mode
        if st.session_state.device_mode == 'desktop':
            st.dataframe(students_df, use_container_width=True, height=600)
        elif st.session_state.device_mode == 'tablet':
            st.dataframe(students_df, use_container_width=True, height=400)
        else:  # mobile
            st.dataframe(students_df, use_container_width=True, height=300)
        
        # Download button
        csv = students_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Students (CSV)",
            data=csv,
            file_name=f"students_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    else:
        st.info("📭 No students in the database yet.")

def add_student():
    st.header("➕ Add New Student")
    
    with st.form("add_student_form"):
        # Responsive column layout based on device mode
        if st.session_state.device_mode == 'desktop':
            col1, col2 = st.columns(2)
        elif st.session_state.device_mode == 'tablet':
            col1, col2 = st.columns(2)
        else:  # mobile
            col1, col2 = st.columns([1])  # Single column
        
        with col1:
            name = st.text_input("Student Name *")
            age = st.selectbox("Age *", AGE_OPTIONS)
            blood_group = st.selectbox("Blood Group *", ["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"])
        
        if st.session_state.device_mode != 'mobile':
            with col2:
                standard = st.selectbox("Standard *", STANDARDS)
                father_phone = st.text_input("Father's Phone Number *")
                mother_phone = st.text_input("Mother's Phone Number *")
        else:
            standard = st.selectbox("Standard *", STANDARDS)
            father_phone = st.text_input("Father's Phone Number *")
            mother_phone = st.text_input("Mother's Phone Number *")
        
        address = st.text_area("Address *")
        aadhar = st.text_input("Aadhar Details (12 digits) *")
        
        submitted = st.form_submit_button("➕ Add Student", use_container_width=True)
        
        if submitted:
            if not all([name, address, aadhar, father_phone, mother_phone]):
                st.error("❌ Please fill all required fields!")
            elif not validate_aadhar(aadhar):
                st.error("❌ Aadhar must be 12 digits!")
            elif not validate_phone(father_phone):
                st.error("❌ Father's phone must be 10 digits!")
            elif not validate_phone(mother_phone):
                st.error("❌ Mother's phone must be 10 digits!")
            else:
                students_df = initialize_student_excel()
                new_student = {
                    'Student_ID': get_next_student_id(),
                    'Name': name,
                    'Standard': standard,
                    'Age': age,
                    'Blood_Group': blood_group,
                    'Address': address,
                    'Father_Phone': father_phone,
                    'Mother_Phone': mother_phone,
                    'Aadhar_Details': aadhar
                }
                students_df = pd.concat([students_df, pd.DataFrame([new_student])], ignore_index=True)
                students_df.to_excel(STUDENT_FILE, index=False)
                st.success(f"✅ Student {name} added successfully! ID: {new_student['Student_ID']}")

def update_student():
    st.header("✏️ Update Student")
    students_df = initialize_student_excel()
    
    if len(students_df) == 0:
        st.info("No students to update.")
        return
    
    student_names = students_df['Name'].tolist()
    selected_student = st.selectbox("Select Student", student_names)
    student_data = students_df[students_df['Name'] == selected_student].iloc[0]
    
    with st.form("update_student_form"):
        # Responsive layout
        if st.session_state.device_mode != 'mobile':
            col1, col2 = st.columns(2)
        else:
            col1 = st.container()
            col2 = None
        
        with col1:
            new_name = st.text_input("Student Name", value=student_data['Name'])
            new_age = st.selectbox("Age", AGE_OPTIONS, index=AGE_OPTIONS.index(student_data['Age']))
            new_blood = st.selectbox("Blood Group", ["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"], index=["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"].index(student_data['Blood_Group']))
        
        if col2:
            with col2:
                new_standard = st.selectbox("Standard", STANDARDS, index=STANDARDS.index(student_data['Standard']))
                new_father_phone = st.text_input("Father's Phone", value=str(student_data['Father_Phone']))
                new_mother_phone = st.text_input("Mother's Phone", value=str(student_data['Mother_Phone']))
        else:
            new_standard = st.selectbox("Standard", STANDARDS, index=STANDARDS.index(student_data['Standard']))
            new_father_phone = st.text_input("Father's Phone", value=str(student_data['Father_Phone']))
            new_mother_phone = st.text_input("Mother's Phone", value=str(student_data['Mother_Phone']))
        
        new_address = st.text_area("Address", value=student_data['Address'])
        new_aadhar = st.text_input("Aadhar Details", value=student_data['Aadhar_Details'])
        
        submitted = st.form_submit_button("✅ Update Student", use_container_width=True)
        
        if submitted:
            if not validate_aadhar(new_aadhar):
                st.error("❌ Aadhar must be 12 digits!")
            elif not validate_phone(new_father_phone):
                st.error("❌ Father's phone must be 10 digits!")
            elif not validate_phone(new_mother_phone):
                st.error("❌ Mother's phone must be 10 digits!")
            else:
                students_df.loc[students_df['Name'] == selected_student, 'Name'] = new_name
                students_df.loc[students_df['Name'] == new_name, 'Age'] = new_age
                students_df.loc[students_df['Name'] == new_name, 'Blood_Group'] = new_blood
                students_df.loc[students_df['Name'] == new_name, 'Standard'] = new_standard
                students_df.loc[students_df['Name'] == new_name, 'Address'] = new_address
                students_df.loc[students_df['Name'] == new_name, 'Father_Phone'] = new_father_phone
                students_df.loc[students_df['Name'] == new_name, 'Mother_Phone'] = new_mother_phone
                students_df.loc[students_df['Name'] == new_name, 'Aadhar_Details'] = new_aadhar
                students_df.to_excel(STUDENT_FILE, index=False)
                st.success("✅ Student updated successfully!")

def delete_student():
    st.header("🗑️ Delete Student")
    students_df = initialize_student_excel()
    
    if len(students_df) == 0:
        st.info("No students to delete.")
        return
    
    student_names = students_df['Name'].tolist()
    selected_student = st.selectbox("Select Student to Delete", student_names)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ Delete Student", type="secondary"):
            students_df = students_df[students_df['Name'] != selected_student]
            students_df.to_excel(STUDENT_FILE, index=False)
            st.success(f"✅ Student {selected_student} deleted successfully!")

def import_students():
    st.header("📥 Import Students from Excel")
    
    uploaded_file = st.file_uploader("Upload Excel file", type=['xlsx'])
    
    if uploaded_file:
        try:
            imported_df = pd.read_excel(uploaded_file)
            st.write("Preview of data:")
            st.dataframe(imported_df)
            
            if st.button("📥 Import Students"):
                students_df = initialize_student_excel()
                imported_df['Student_ID'] = range(get_next_student_id(), get_next_student_id() + len(imported_df))
                students_df = pd.concat([students_df, imported_df], ignore_index=True)
                students_df.to_excel(STUDENT_FILE, index=False)
                st.success(f"✅ {len(imported_df)} students imported successfully!")
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

# ============================================================================
# FEES MANAGEMENT FUNCTIONS
# ============================================================================

def manage_fee_structure():
    st.header("⚙️ Manage Fee Structure")
    
    fee_df = initialize_fee_structure()
    
    st.subheader("Add/Update Fee Structure")
    
    with st.form("fee_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            standard = st.selectbox("Select Standard", STANDARDS)
            fee_type = st.selectbox("Fee Type", FEE_TYPES)
        
        with col2:
            amount = st.number_input("Fee Amount (₹)", min_value=0.0)
            academic_year = st.text_input("Academic Year", value="2024-2025")
        
        submitted = st.form_submit_button("➕ Add/Update Fee")
        
        if submitted:
            # Check if fee already exists
            existing = fee_df[(fee_df['Standard'] == standard) & (fee_df['Fee_Type'] == fee_type) & (fee_df['Academic_Year'] == academic_year)]
            
            if len(existing) > 0:
                fee_df.loc[(fee_df['Standard'] == standard) & (fee_df['Fee_Type'] == fee_type), 'Amount'] = amount
                st.success("✅ Fee structure updated!")
            else:
                new_fee = {
                    'Fee_ID': len(fee_df) + 1,
                    'Standard': standard,
                    'Fee_Type': fee_type,
                    'Amount': amount,
                    'Academic_Year': academic_year
                }
                fee_df = pd.concat([fee_df, pd.DataFrame([new_fee])], ignore_index=True)
                st.success("✅ Fee added!")
            
            fee_df.to_excel(FEE_STRUCTURE_FILE, index=False)
    
    st.subheader("Current Fee Structure")
    if len(fee_df) > 0:
        st.dataframe(fee_df, use_container_width=True)
    else:
        st.info("No fee structure defined yet.")

def collect_payment():
    st.header("💵 Collect Payment")
    
    students_df = initialize_student_excel()
    fee_df = initialize_fee_structure()
    
    if len(students_df) == 0:
        st.error("No students in the system.")
        return
    
    student_names = students_df['Name'].tolist()
    selected_student = st.selectbox("Select Student", student_names)
    student_id = students_df[students_df['Name'] == selected_student]['Student_ID'].values[0]
    student_standard = students_df[students_df['Name'] == selected_student]['Standard'].values[0]
    
    # Get fees for this standard
    available_fees = fee_df[fee_df['Standard'] == student_standard]['Fee_Type'].unique().tolist()
    
    with st.form("payment_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            fee_type = st.selectbox("Fee Type", available_fees if available_fees else FEE_TYPES)
            amount = st.number_input("Amount (₹)", min_value=0.0)
        
        with col2:
            payment_date = st.date_input("Payment Date")
            payment_mode = st.selectbox("Payment Mode", PAYMENT_MODES)
        
        notes = st.text_area("Notes")
        submitted = st.form_submit_button("💳 Record Payment")
        
        if submitted:
            pay_df = initialize_fee_payments()
            new_payment = {
                'Payment_ID': len(pay_df) + 1,
                'Student_ID': student_id,
                'Fee_Type': fee_type,
                'Amount': amount,
                'Payment_Date': payment_date,
                'Payment_Mode': payment_mode,
                'Notes': notes
            }
            pay_df = pd.concat([pay_df, pd.DataFrame([new_payment])], ignore_index=True)
            pay_df.to_excel(FEE_PAYMENTS_FILE, index=False)
            st.success("✅ Payment recorded successfully!")

def view_payments():
    st.header("📋 View All Payments")
    
    pay_df = initialize_fee_payments()
    
    if len(pay_df) > 0:
        st.dataframe(pay_df, use_container_width=True)
        
        csv = pay_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Payments (CSV)",
            data=csv,
            file_name=f"payments_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    else:
        st.info("No payments recorded yet.")

def student_fee_history():
    st.header("🔍 Student Fee History")
    
    students_df = initialize_student_excel()
    pay_df = initialize_fee_payments()
    
    if len(students_df) == 0:
        st.error("No students in the system.")
        return
    
    student_names = students_df['Name'].tolist()
    selected_student = st.selectbox("Select Student", student_names)
    student_id = students_df[students_df['Name'] == selected_student]['Student_ID'].values[0]
    
    student_payments = pay_df[pay_df['Student_ID'] == student_id]
    
    if len(student_payments) > 0:
        st.dataframe(student_payments, use_container_width=True)
        
        total_paid = student_payments['Amount'].sum()
        st.metric("Total Amount Paid", f"₹{total_paid:,.2f}")
    else:
        st.info(f"No payment history for {selected_student}")

def generate_reports():
    st.header("📄 Generate Reports")
    
    report_type = st.selectbox("Select Report Type", ["Fee Collection Summary", "Class-wise Fees", "Payment Mode Report", "Custom Date Range"])
    
    if report_type == "Fee Collection Summary":
        pay_df = initialize_fee_payments()
        if len(pay_df) > 0:
            summary = pay_df.groupby('Fee_Type')['Amount'].sum()
            st.bar_chart(summary)
            st.dataframe(summary)
        else:
            st.info("No data available.")
    
    elif report_type == "Class-wise Fees":
        students_df = initialize_student_excel()
        pay_df = initialize_fee_payments()
        
        if len(pay_df) > 0:
            pay_df_merged = pay_df.merge(students_df[['Student_ID', 'Standard']], on='Student_ID', how='left')
            class_summary = pay_df_merged.groupby('Standard')['Amount'].sum()
            st.bar_chart(class_summary)
            st.dataframe(class_summary)
        else:
            st.info("No data available.")
    
    elif report_type == "Payment Mode Report":
        pay_df = initialize_fee_payments()
        if len(pay_df) > 0:
            mode_summary = pay_df.groupby('Payment_Mode')['Amount'].sum()
            st.pie_chart(mode_summary)
            st.dataframe(mode_summary)
        else:
            st.info("No data available.")
    
    elif report_type == "Custom Date Range":
        pay_df = initialize_fee_payments()
        
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date")
        with col2:
            end_date = st.date_input("End Date")
        
        if st.button("Generate Report"):
            pay_df['Payment_Date'] = pd.to_datetime(pay_df['Payment_Date'])
            filtered_df = pay_df[(pay_df['Payment_Date'] >= pd.to_datetime(start_date)) & 
                               (pay_df['Payment_Date'] <= pd.to_datetime(end_date))]
            
            if len(filtered_df) > 0:
                st.dataframe(filtered_df, use_container_width=True)
                st.metric("Total Collection", f"₹{filtered_df['Amount'].sum():,.2f}")
                
                # Download report
                csv = filtered_df.to_csv(index=False)
                st.download_button(
                    label="📥 Download Report",
                    data=csv,
                    file_name=f"report_{start_date}_{end_date}.csv",
                    mime="text/csv"
                )
            else:
                st.info("No data for the selected date range.")

# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main():
    check_url_params()
    
    if not st.session_state.logged_in:
        login_page()
        return
    
    # Dark Theme Styling - BLACK BACKGROUND
    st.markdown("""
        <style>
        /* Main background - BLACK */
        .main {
            background-color: #1a1a1a !important;
        }
        
        /* App container - BLACK */
        [data-testid="stAppViewContainer"] {
            background-color: #1a1a1a !important;
            color: #ffffff !important;
        }
        
        /* Headers - WHITE TEXT */
        h1, h2, h3, h4, h5, h6 {
            color: #ffffff !important;
        }
        
        /* Text - WHITE */
        p, span, label {
            color: #ffffff !important;
        }
        
        /* Input fields - DARK BACKGROUND */
        input, textarea, select {
            background-color: #2a2a2a !important;
            color: #ffffff !important;
            border-color: #444444 !important;
        }
        
        /* Dataframe - DARK */
        [data-testid="stDataFrame"] {
            background-color: #2a2a2a !important;
        }
        
        /* Info/Success/Error boxes */
        [data-testid="stAlert"] {
            background-color: #2a2a2a !important;
            color: #ffffff !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # RESPONSIVE LAYOUT BASED ON DEVICE MODE
    if st.session_state.device_mode == 'desktop':
        # DESKTOP VIEW - Full Width
        st.markdown("""
            <style>
            /* Desktop - Full width, large fonts */
            body { font-size: 16px !important; }
            h1 { font-size: 48px !important; }
            h2 { font-size: 36px !important; }
            h3 { font-size: 28px !important; }
            .stButton button { font-size: 16px !important; padding: 12px 24px !important; }
            .stSelectbox { font-size: 16px !important; }
            .stTextInput input { font-size: 16px !important; }
            [data-testid="stMetric"] { font-size: 18px !important; }
            </style>
        """, unsafe_allow_html=True)
        max_width = 1400
        col_ratio_main = [3, 1]
        col_ratio_2 = [1, 1]
        form_cols = 2
        font_size = "large"
        padding = "20px"
        
    elif st.session_state.device_mode == 'tablet':
        # TABLET VIEW - Medium Width
        st.markdown("""
            <style>
            /* Tablet - Medium width, medium fonts */
            body { font-size: 14px !important; }
            h1 { font-size: 36px !important; }
            h2 { font-size: 28px !important; }
            h3 { font-size: 22px !important; }
            .stButton button { font-size: 14px !important; padding: 10px 20px !important; }
            .stSelectbox { font-size: 14px !important; }
            .stTextInput input { font-size: 14px !important; }
            [data-testid="stMetric"] { font-size: 14px !important; }
            </style>
        """, unsafe_allow_html=True)
        max_width = 900
        col_ratio_main = [2, 1]
        col_ratio_2 = [1, 1]
        form_cols = 2
        font_size = "medium"
        padding = "15px"
        
    else:  # mobile
        # MOBILE VIEW - Narrow Width
        st.markdown("""
            <style>
            /* Mobile - Narrow width, small fonts */
            body { font-size: 12px !important; }
            h1 { font-size: 28px !important; }
            h2 { font-size: 20px !important; }
            h3 { font-size: 16px !important; }
            .stButton button { font-size: 12px !important; padding: 8px 16px !important; }
            .stSelectbox { font-size: 12px !important; }
            .stTextInput input { font-size: 12px !important; }
            [data-testid="stMetric"] { font-size: 12px !important; }
            </style>
        """, unsafe_allow_html=True)
        max_width = 600
        col_ratio_main = [1, 0]  # Full width, no sidebar in mobile
        col_ratio_2 = [1]  # Single column
        form_cols = 1  # Single column forms
        font_size = "small"
        padding = "10px"
    
    # Display current device mode
    mode_indicator = f"📊 **Current Layout:** {st.session_state.device_mode.upper()}"
    st.markdown(f"<div style='padding: {padding}; background: #2a2a2a; border-radius: 8px; margin-bottom: 20px;'>{mode_indicator}</div>", unsafe_allow_html=True)
    
    # Dashboard header
    col1, col2 = st.columns([10, 1])
    with col1:
        st.title("🎓 School Management System")
    with col2:
        if st.button("🚪 Logout"):
            st.session_state.logged_in = False
            st.rerun()
    
    st.markdown("---")
    
    # Initialize data
    initialize_student_excel()
    initialize_fee_structure()
    initialize_fee_payments()
    
    # Sidebar Navigation - DARK THEME (BLACK BACKGROUND)
    st.sidebar.markdown('''
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@700;800;900&family=Poppins:wght@700;800;900&display=swap');
        
        /* General sidebar styling - BLACK BACKGROUND, NO GLASSMORPHISM */
        [data-testid="stSidebar"] {
            background: #1a1a1a !important;
            backdrop-filter: none !important;
        }
        
        [data-testid="stSidebar"]{
            font-size: 24px !important;
        }
        
        [data-testid="stSidebar"] label {
            font-size: 24px !important; 
            font-weight: 800 !important;
            color: #ffffff !important;
            letter-spacing: 0.5px !important;
        }
        
        /* MAIN MENU AND OPERATIONS HEADERS - BALANCED SIZE */
        [data-testid="stSidebar"] .stRadio > label {
            font-size: 48px !important;
            font-weight: 900 !important;
            color: #ffffff !important;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.1) !important;
            letter-spacing: 1px !important;
            -webkit-text-stroke: 1px rgba(0,0,0,0.3) !important;
            line-height: 1.2 !important;
            font-family: 'Poppins', 'Arial Black', 'Roboto Black', sans-serif !important;
            margin: 15px 0 !important;
            padding: 10px 5px !important;
            text-transform: uppercase !important;
            word-wrap: break-word !important;
        }
        
        /* MENU ITEMS - LARGE BUT READABLE */
        [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label {
            font-size: 56px !important;
            padding: 12px 8px !important;
            font-weight: 900 !important;
            color: #ffffff !important;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.1) !important;
            -webkit-text-stroke: 1px rgba(0,0,0,0.3) !important;
            line-height: 1.3 !important;
            font-family: 'Poppins', 'Arial Black', 'Roboto Black', sans-serif !important;
            margin: 8px 0 !important;
            border-radius: 6px !important;
            transition: all 0.3s ease !important;
            text-transform: capitalize !important;
        }
        
        /* Menu item hover effect - ENHANCED */
        [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:hover {
            background-color: rgba(45, 90, 160, 0.15) !important;
            transform: scale(1.05) !important;
            letter-spacing: 1px !important;
            color: #ffffff !important;
            box-shadow: 0 2px 8px rgba(45, 90, 160, 0.3) !important;
        }
        
        /* Selected menu item styling - GOLD ACCENT */
        [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label[aria-checked="true"] {
            background-color: rgba(255, 215, 0, 0.2) !important;
            border-left: 4px solid #ffd700 !important;
            padding-left: 10px !important;
            color: #ffffff !important;
            box-shadow: 0 2px 8px rgba(255, 215, 0, 0.3) !important;
        }
        
        /* Sidebar title styling */
        [data-testid="stSidebar"] h1 {
            font-size: 36px !important;
            font-weight: 900 !important;
            color: #ffffff !important;
            text-shadow: 1px 1px 3px rgba(0,0,0,0.1) !important;
            -webkit-text-stroke: 0.8px rgba(0,0,0,0.2) !important;
            font-family: 'Poppins', 'Arial Black', 'Roboto Black', sans-serif !important;
            margin-bottom: 15px !important;
            letter-spacing: 1px !important;
            text-transform: uppercase !important;
        }
        
        /* Paragraph text in sidebar */
        [data-testid="stSidebar"] p {
            font-size: 18px !important;
            font-weight: 700 !important;
            color: #ffffff !important;
            margin: 8px 0 !important;
        }
        
        /* Streamlit radio button styling */
        [data-testid="stSidebar"] .stRadio {
            background-color: transparent !important;
        }
        
        /* Device Switcher Styling */
        .device-switcher {
            display: flex;
            gap: 10px;
            justify-content: center;
            align-items: center;
            margin: 20px 0;
            padding: 15px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 10px;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        }
        
        .device-btn {
            background: rgba(255, 255, 255, 0.2);
            border: 2px solid #ffffff;
            color: #ffffff;
            padding: 10px 15px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 20px;
            font-weight: bold;
            transition: all 0.3s ease;
            text-align: center;
            width: 60px;
        }
        
        .device-btn:hover {
            background: rgba(255, 255, 255, 0.4);
            transform: scale(1.1);
            box-shadow: 0 4px 12px rgba(255, 255, 255, 0.3);
        }
        
        .device-btn.active {
            background: #ffd700;
            color: #667eea;
            border-color: #ffd700;
            box-shadow: 0 4px 15px rgba(255, 215, 0, 0.5);
        }
        </style>
    ''', unsafe_allow_html=True)
    
    # Device Switcher Section - HORIZONTAL (Full Width)
    st.sidebar.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)
    st.sidebar.markdown("### 📱 View Mode")
    
    if 'device_mode' not in st.session_state:
        st.session_state.device_mode = 'desktop'
    
    # Full width buttons - stacked vertically
    if st.sidebar.button("🖥️ Desktop", key="btn_desktop", use_container_width=True):
        st.session_state.device_mode = 'desktop'
    
    if st.sidebar.button("📱 Tablet", key="btn_tablet", use_container_width=True):
        st.session_state.device_mode = 'tablet'
    
    if st.sidebar.button("📲 Mobile", key="btn_mobile", use_container_width=True):
        st.session_state.device_mode = 'mobile'
    
    st.sidebar.markdown(f"**Current Mode:** {st.session_state.device_mode.upper()}", unsafe_allow_html=True)
    st.sidebar.markdown("---")
    
    st.sidebar.title("📚 Navigation")
    
    main_menu = st.sidebar.radio("Main Menu:", ["👨‍🎓 Student Management", "💰 Fees Management"])
    
    if main_menu == "👨‍🎓 Student Management":
        student_menu = st.sidebar.radio("Operations:", ["📊 View Students", "➕ Add Student", "✏️ Update Student", "🗑️ Delete Student", "📥 Import Students"])
        
        if student_menu == "📊 View Students":
            view_students()
        elif student_menu == "➕ Add Student":
            add_student()
        elif student_menu == "✏️ Update Student":
            update_student()
        elif student_menu == "🗑️ Delete Student":
            delete_student()
        elif student_menu == "📥 Import Students":
            import_students()
    
    else:
        fees_menu = st.sidebar.radio("Operations:", ["⚙️ Fee Structure", "💵 Collect Payment", "📋 View Payments", "🔍 Student Fee History", "📄 Reports"])
        
        if fees_menu == "⚙️ Fee Structure":
            manage_fee_structure()
        elif fees_menu == "💵 Collect Payment":
            collect_payment()
        elif fees_menu == "📋 View Payments":
            view_payments()
        elif fees_menu == "🔍 Student Fee History":
            student_fee_history()
        elif fees_menu == "📄 Reports":
            generate_reports()

if __name__ == "__main__":
    main()
