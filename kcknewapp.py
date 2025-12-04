import streamlit as st
import pandas as pd
import os
from datetime import datetime
import re
from io import BytesIO

st.set_page_config(page_title="School Management System", page_icon="🎓", layout="wide")

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
    return pd.read_excel(STUDENT_FILE)

def initialize_fee_structure():
    if not os.path.exists(FEE_STRUCTURE_FILE):
        df = pd.DataFrame(columns=['Fee_ID', 'Standard', 'Fee_Type', 'Amount', 'Payment_Frequency', 'Academic_Year'])
        df.to_excel(FEE_STRUCTURE_FILE, index=False)
        return df
    return pd.read_excel(FEE_STRUCTURE_FILE)

def initialize_fee_payments():
    if not os.path.exists(FEE_PAYMENTS_FILE):
        df = pd.DataFrame(columns=['Receipt_No', 'Student_ID', 'Student_Name', 'Standard', 'Payment_Date', 'Amount_Paid', 'Payment_Mode', 'Fee_Type', 'Academic_Year', 'Remarks'])
        df.to_excel(FEE_PAYMENTS_FILE, index=False)
        return df
    return pd.read_excel(FEE_PAYMENTS_FILE)

def load_students():
    try:
        df = pd.read_excel(STUDENT_FILE)
        if df.empty:
            df = pd.DataFrame(columns=['Student_ID', 'Name', 'Address', 'Age', 'Blood_Group', 'Father_Phone', 'Mother_Phone', 'Aadhar_Details', 'Standard'])
        return df
    except:
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
    except:
        return False

def save_fee_structure(df):
    try:
        df.to_excel(FEE_STRUCTURE_FILE, index=False)
        return True
    except:
        return False

def save_fee_payments(df):
    try:
        df.to_excel(FEE_PAYMENTS_FILE, index=False)
        return True
    except:
        return False

def generate_student_id(df):
    if df.empty:
        return "STU001"
    last_id = df['Student_ID'].max()
    num = int(last_id[3:]) + 1
    return f"STU{num:03d}"

def generate_receipt_no(df):
    if df.empty:
        return f"RCP{datetime.now().strftime('%Y%m')}001"
    last_receipt = df['Receipt_No'].max()
    try:
        num = int(last_receipt[-3:]) + 1
        return f"RCP{datetime.now().strftime('%Y%m')}{num:03d}"
    except:
        return f"RCP{datetime.now().strftime('%Y%m')}001"

def generate_fee_id(df):
    if df.empty:
        return "FEE001"
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
    return total_fees, total_paid, total_fees - total_paid

def login_page():
    st.markdown("""<style>
        .stApp > header {visibility: hidden;}
        .login-container{max-width:400px;margin:50px auto;padding:40px;background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);border-radius:15px;box-shadow:0 10px 30px rgba(0,0,0,0.3)}
        .login-title{color:white;text-align:center;font-size:32px;font-weight:bold;margin-bottom:30px}
        .login-subtitle{color:#e0e0e0;text-align:center;margin-bottom:30px}
    </style>""", unsafe_allow_html=True)
    st.markdown('<div style="height:20px"></div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if os.path.exists("school_logo.png"):
            st.image("school_logo.png", width=150)
        else:
            st.markdown('<div style="text-align:center;margin-bottom:30px"><p style="font-size:80px;margin:0">🏫</p><p style="color:#666;font-size:14px">School Logo</p></div>', unsafe_allow_html=True)
        st.markdown('<div class="login-container"><p class="login-title">🎓 School Management</p><p class="login-subtitle">Admin Login</p>', unsafe_allow_html=True)
        with st.form("login_form"):
            username = st.text_input("👤 Username", placeholder="Enter username")
            password = st.text_input("🔐 Password", type="password", placeholder="Enter password")
            if st.form_submit_button("🔓 Login", use_container_width=True):
                if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
                    st.session_state.logged_in = True
                    st.session_state.login_attempts = 0
                    st.success("✅ Login successful!")
                    st.rerun()
                else:
                    st.session_state.login_attempts += 1
                    remaining = 5 - st.session_state.login_attempts
                    if st.session_state.login_attempts >= 5:
                        st.error("🚫 Too many failed attempts.")
                    else:
                        st.error(f"❌ Invalid credentials! {remaining} attempts remaining.")
        st.markdown('</div>', unsafe_allow_html=True)
        st.info("**Credentials:**\n\n👤 Username: admin\n\n🔐 Password: ADMIN001")

def handle_student_menu(menu):
    students_df = load_students()
    if menu == "📊 View Students":
        st.header("📊 All Students")
        if students_df.empty:
            st.info("No students in database. Add students to get started!")
        else:
            col1, col2 = st.columns([2, 1])
            with col1:
                search = st.text_input("🔍 Search by Name or ID:", "")
            with col2:
                filter_std = st.selectbox("Filter by Class:", ["All"] + sorted(students_df['Standard'].unique().tolist()))
            filtered = students_df.copy()
            if search:
                filtered = filtered[filtered['Name'].str.contains(search, case=False, na=False) | filtered['Student_ID'].str.contains(search, case=False, na=False)]
            if filter_std != "All":
                filtered = filtered[filtered['Standard'] == filter_std]
            st.dataframe(filtered, use_container_width=True, height=400)
            st.info(f"📊 Total: {len(filtered)}")
            buf = BytesIO()
            with pd.ExcelWriter(buf, engine='openpyxl') as w:
                filtered.to_excel(w, index=False)
            buf.seek(0)
            st.download_button("💾 Export", buf, f"students_{datetime.now().strftime('%Y%m%d')}.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    elif menu == "➕ Add Student":
        st.header("➕ Add New Student")
        with st.form("add_form"):
            st.subheader("👤 Personal Info")
            c1, c2, c3 = st.columns(3)
            with c1:
                name = st.text_input("Full Name *")
                age = st.selectbox("Age *", ["Select"] + AGE_OPTIONS)
            with c2:
                bg = st.selectbox("Blood Group *", ["Select", "A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"])
                std = st.selectbox("Class *", ["Select"] + STANDARDS)
            with c3:
                aadhar = st.text_input("Aadhar *")
            st.markdown("---")
            st.subheader("📞 Parent Contact")
            c1, c2 = st.columns(2)
            with c1:
                fphone = st.text_input("Father's Phone *")
            with c2:
                mphone = st.text_input("Mother's Phone *")
            st.markdown("---")
            st.subheader("🏠 Address")
            addr = st.text_area("Complete Address *", height=100)
            if st.form_submit_button("✅ Add Student", type="primary"):
                errs = []
                if not name: errs.append("Name required")
                if std == "Select": errs.append("Select standard")
                if bg == "Select": errs.append("Select blood group")
                if age == "Select": errs.append("Select age")
                if not addr: errs.append("Address required")
                if not aadhar or not validate_aadhar(aadhar): errs.append("Invalid Aadhar")
                if not fphone or not validate_phone(fphone): errs.append("Invalid father's phone")
                if not mphone or not validate_phone(mphone): errs.append("Invalid mother's phone")
                if errs:
                    for e in errs: st.error(f"❌ {e}")
                else:
                    new_id = generate_student_id(students_df)
                    new = pd.DataFrame({'Student_ID': [new_id], 'Name': [name], 'Address': [addr], 'Age': [age], 'Blood_Group': [bg], 'Father_Phone': [fphone], 'Mother_Phone': [mphone], 'Aadhar_Details': [aadhar], 'Standard': [std]})
                    students_df = pd.concat([students_df, new], ignore_index=True)
                    if save_students(students_df):
                        st.success(f"✅ Added! ID: {new_id}")
                        st.balloons()
    elif menu == "✏️ Update Student":
        st.header("✏️ Update Student")
        if students_df.empty:
            st.warning("No students!")
        else:
            sid = st.selectbox("Select ID:", students_df['Student_ID'].tolist())
            if sid:
                std_data = students_df[students_df['Student_ID'] == sid].iloc[0]
                st.markdown("### Current Details")
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.info(f"**Name:** {std_data['Name']}")
                with c2:
                    st.info(f"**Class:** {std_data['Standard']}")
                with c3:
                    st.info(f"**Age:** {std_data['Age']}")
                with st.form("upd_form"):
                    c1, c2, c3 = st.columns(3)
                    with c1:
                        name = st.text_input("Name *", value=std_data['Name'])
                        age = st.selectbox("Age *", AGE_OPTIONS, index=AGE_OPTIONS.index(int(std_data['Age'])) if int(std_data['Age']) in AGE_OPTIONS else 0)
                    with c2:
                        bgl = ["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"]
                        bg = st.selectbox("Blood Group *", bgl, index=bgl.index(std_data['Blood_Group']) if std_data['Blood_Group'] in bgl else 0)
                        std = st.selectbox("Class *", STANDARDS, index=STANDARDS.index(std_data['Standard']) if std_data['Standard'] in STANDARDS else 0)
                    with c3:
                        aadhar = st.text_input("Aadhar *", value=std_data['Aadhar_Details'])
                    c1, c2 = st.columns(2)
                    with c1:
                        fphone = st.text_input("Father Phone *", value=std_data.get('Father_Phone', ''))
                    with c2:
                        mphone = st.text_input("Mother Phone *", value=std_data.get('Mother_Phone', ''))
                    addr = st.text_area("Address *", value=std_data['Address'])
                    if st.form_submit_button("💾 Update", type="primary"):
                        if validate_aadhar(aadhar) and validate_phone(fphone) and validate_phone(mphone):
                            students_df.loc[students_df['Student_ID'] == sid, 'Name'] = name
                            students_df.loc[students_df['Student_ID'] == sid, 'Address'] = addr
                            students_df.loc[students_df['Student_ID'] == sid, 'Age'] = age
                            students_df.loc[students_df['Student_ID'] == sid, 'Blood_Group'] = bg
                            students_df.loc[students_df['Student_ID'] == sid, 'Father_Phone'] = fphone
                            students_df.loc[students_df['Student_ID'] == sid, 'Mother_Phone'] = mphone
                            students_df.loc[students_df['Student_ID'] == sid, 'Aadhar_Details'] = aadhar
                            students_df.loc[students_df['Student_ID'] == sid, 'Standard'] = std
                            if save_students(students_df):
                                st.success("✅ Updated!")
                        else:
                            st.error("❌ Invalid data")
    elif menu == "🗑️ Delete Student":
        st.header("🗑️ Delete Student")
        if students_df.empty:
            st.warning("No students!")
        else:
            sid = st.selectbox("Select ID:", students_df['Student_ID'].tolist())
            if sid:
                std_data = students_df[students_df['Student_ID'] == sid].iloc[0]
                st.markdown("### Details:")
                st.write(f"**Name:** {std_data['Name']} | **Class:** {std_data['Standard']}")
                st.error("⚠️ Cannot be undone!")
                if st.button("🗑️ Confirm Delete", type="primary"):
                    students_df = students_df[students_df['Student_ID'] != sid]
                    if save_students(students_df):
                        st.success("✅ Deleted!")
                        st.rerun()
    elif menu == "📥 Import Students":
        st.header("📥 Import Students")
        st.info("Columns: Name, Address, Age, Blood_Group, Father_Phone, Mother_Phone, Aadhar_Details, Standard")
        template = pd.DataFrame({'Name': ['Sample'], 'Address': ['Address'], 'Age': [5], 'Blood_Group': ['A+'], 'Father_Phone': ['9876543210'], 'Mother_Phone': ['9876543211'], 'Aadhar_Details': ['123456789012'], 'Standard': ['Playgroup']})
        buf = BytesIO()
        with pd.ExcelWriter(buf, engine='openpyxl') as w:
            template.to_excel(w, index=False)
        buf.seek(0)
        st.download_button("📥 Download Template", buf, "template.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        uploaded = st.file_uploader("Upload Excel", type=['xlsx'])
        if uploaded:
            try:
                imp_df = pd.read_excel(uploaded)
                st.dataframe(imp_df.head(10))
                if st.button("📥 Import", type="primary"):
                    new_students = []
                    for _, row in imp_df.iterrows():
                        if validate_aadhar(str(row['Aadhar_Details'])) and validate_phone(str(row['Father_Phone'])) and validate_phone(str(row['Mother_Phone'])):
                            new_id = generate_student_id(pd.concat([students_df, pd.DataFrame(new_students)]) if new_students else students_df)
                            new_students.append({'Student_ID': new_id, 'Name': row['Name'], 'Address': row['Address'], 'Age': int(row['Age']), 'Blood_Group': row['Blood_Group'], 'Father_Phone': row['Father_Phone'], 'Mother_Phone': row['Mother_Phone'], 'Aadhar_Details': row['Aadhar_Details'], 'Standard': row['Standard']})
                    if new_students:
                        final = pd.concat([students_df, pd.DataFrame(new_students)], ignore_index=True)
                        if save_students(final):
                            st.success(f"✅ Imported {len(new_students)} students!")
            except Exception as e:
                st.error(f"Error: {e}")
    elif menu == "📈 Student Analytics":
        st.header("📈 Analytics")
        if students_df.empty:
            st.info("No data!")
        else:
            c1, c2, c3, c4 = st.columns(4)
            with c1: st.metric("Total", len(students_df))
            with c2: st.metric("Classes", students_df['Standard'].nunique())
            with c3: st.metric("Avg Age", f"{students_df['Age'].mean():.1f}")
            with c4: st.metric("Common BG", students_df['Blood_Group'].mode()[0])
            st.bar_chart(students_df['Standard'].value_counts())

def handle_fees_menu(menu):
    students_df = load_students()
    fee_df = load_fee_structure()
    pay_df = load_fee_payments()
    if menu == "💵 Collect Payment":
        st.header("💵 Collect Payment")
        if students_df.empty:
            st.warning("Add students first!")
            return
        with st.form("pay_form"):
            sid = st.selectbox("Student *", students_df['Student_ID'].tolist())
            if sid:
                st_d = students_df[students_df['Student_ID'] == sid].iloc[0]
                st.info(f"**{st_d['Name']}** - {st_d['Standard']}")
            ftype = st.selectbox("Fee Type *", FEE_TYPES)
            amt = st.number_input("Amount (₹) *", min_value=0.0, step=100.0)
            pdate = st.date_input("Date *", datetime.now())
            pmode = st.selectbox("Mode *", PAYMENT_MODES)
            if st.form_submit_button("💰 Process", type="primary"):
                if amt > 0:
                    rno = generate_receipt_no(pay_df)
                    new_pay = pd.DataFrame({'Receipt_No': [rno], 'Student_ID': [sid], 'Student_Name': [st_d['Name']], 'Standard': [st_d['Standard']], 'Payment_Date': [pdate], 'Amount_Paid': [amt], 'Payment_Mode': [pmode], 'Fee_Type': [ftype], 'Academic_Year': [f"{datetime.now().year}"], 'Remarks': ['']})
                    pay_df = pd.concat([pay_df, new_pay], ignore_index=True)
                    if save_fee_payments(pay_df):
                        st.success(f"✅ Receipt: {rno}")
                        st.balloons()
    elif menu == "📋 View Payments":
        st.header("📋 Payments")
        if pay_df.empty:
            st.info("No payments!")
        else:
            st.dataframe(pay_df, use_container_width=True)
            buf = BytesIO()
            with pd.ExcelWriter(buf, engine='openpyxl') as w:
                pay_df.to_excel(w, index=False)
            buf.seek(0)
            st.download_button("💾 Export", buf, f"payments_{datetime.now().strftime('%Y%m%d')}.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    elif menu == "🔍 Student Fee History":
        st.header("🔍 Fee History")
        if students_df.empty:
            st.warning("No students!")
        else:
            sid = st.selectbox("Student:", students_df['Student_ID'].tolist())
            if sid:
                st_d = students_df[students_df['Student_ID'] == sid].iloc[0]
                st.write(f"**{st_d['Name']}** - {st_d['Standard']}")
                hist = pay_df[pay_df['Student_ID'] == sid]
                if hist.empty:
                    st.info("No history")
                else:
                    st.dataframe(hist)
    elif menu == "⚙️ Fee Structure":
        st.header("⚙️ Fee Structure")
        if fee_df.empty:
            st.info("No structure defined")
        else:
            st.dataframe(fee_df)
        with st.form("fee_form"):
            std = st.selectbox("Class *", STANDARDS)
            ftype = st.selectbox("Type *", FEE_TYPES)
            amt = st.number_input("Amount *", min_value=0.0, step=100.0)
            if st.form_submit_button("💾 Save", type="primary"):
                fid = generate_fee_id(fee_df)
                new_fee = pd.DataFrame({'Fee_ID': [fid], 'Standard': [std], 'Fee_Type': [ftype], 'Amount': [amt], 'Payment_Frequency': ['Yearly'], 'Academic_Year': [f"{datetime.now().year}"]})
                fee_df = pd.concat([fee_df, new_fee], ignore_index=True)
                if save_fee_structure(fee_df):
                    st.success("✅ Saved!")
    elif menu == "📊 Fees Dashboard":
        st.header("📊 Dashboard")
        if pay_df.empty:
            st.info("No data")
        else:
            total = pay_df['Amount_Paid'].sum()
            st.metric("Total Collected", f"₹{total:,.2f}")
            st.bar_chart(pay_df.groupby('Fee_Type')['Amount_Paid'].sum())
    elif menu == "📄 Reports":
        st.header("📄 Reports")
        rtype = st.selectbox("Type", ["Daily", "Monthly", "Custom Date Range"])
        if rtype == "Custom Date Range":
            c1, c2 = st.columns(2)
            with c1:
                sdate = st.date_input("Start Date")
            with c2:
                edate = st.date_input("End Date", datetime.now())
            if st.button("Generate", type="primary"):
                pay_df['Payment_Date'] = pd.to_datetime(pay_df['Payment_Date'])
                filtered = pay_df[(pay_df['Payment_Date'].dt.date >= sdate) & (pay_df['Payment_Date'].dt.date <= edate)]
                if filtered.empty:
                    st.warning("No data")
                else:
                    st.subheader(f"Report: {sdate} to {edate}")
                    st.metric("Total", f"₹{filtered['Amount_Paid'].sum():,.2f}")
                    st.dataframe(filtered)
                    buf = BytesIO()
                    with pd.ExcelWriter(buf, engine='openpyxl') as w:
                        filtered.to_excel(w, index=False)
                    buf.seek(0)
                    st.download_button("💾 Download", buf, f"report_{sdate}_to_{edate}.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    elif menu == "⚠️ Defaulters":
        st.header("⚠️ Defaulters")
        if students_df.empty:
            st.warning("No students!")
        else:
            defaulters = []
            for _, st_d in students_df.iterrows():
                total, paid, pend = calculate_pending_fees(st_d['Student_ID'], students_df, fee_df, pay_df)
                if pend > 0:
                    defaulters.append({'ID': st_d['Student_ID'], 'Name': st_d['Name'], 'Class': st_d['Standard'], 'Pending': pend})
            if defaulters:
                st.dataframe(pd.DataFrame(defaulters))
            else:
                st.success("🎉 No defaulters!")

def main():
    check_url_params()
    if not st.session_state.logged_in:
        login_page()
        return
    st.markdown('<style>.dashboard-logo{position:fixed;top:70px;right:20px;z-index:999;background:white;padding:10px;border-radius:10px;box-shadow:0 2px 10px rgba(0,0,0,0.1);width:80px;height:80px}</style>', unsafe_allow_html=True)
    if os.path.exists("school_logo.png"):
        import base64
        with open("school_logo.png", "rb") as f:
            st.markdown(f'<div class="dashboard-logo"><img src="data:image/png;base64,{base64.b64encode(f.read()).decode()}" style="width:100%;height:100%;object-fit:contain"></div>', unsafe_allow_html=True)
    c1, c2 = st.columns([8, 1])
    with c1:
        st.title("🎓 School Management System")
    with c2:
        if st.button("🚪 Logout"):
            st.session_state.logged_in = False
            st.rerun()
    st.markdown("---")
    initialize_student_excel()
    initialize_fee_structure()
    initialize_fee_payments()
    st.sidebar.markdown('''<style>
        [data-testid="stSidebar"]{font-size:36px}
        [data-testid="stSidebar"] label{font-size:36px !important; font-weight:700}
        [data-testid="stSidebar"] .stRadio > label{font-size:60px !important; font-weight:900; color:#1f77b4; text-shadow:2px 2px 4px rgba(0,0,0,0.2); letter-spacing:0.5px}
        [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label{font-size:48px !important; padding:14px 0; font-weight:900; text-shadow:1px 1px 2px rgba(0,0,0,0.1)}
        [data-testid="stSidebar"] h1{font-size:38px !important; font-weight:700}
    </style>''', unsafe_allow_html=True)
    st.sidebar.title("📚 Navigation")
    main_menu = st.sidebar.radio("Main Menu:", ["👨‍🎓 Student Management", "💰 Fees Management"])
    if main_menu == "👨‍🎓 Student Management":
        student_menu = st.sidebar.radio("Operations:", ["📊 View Students", "➕ Add Student", "✏️ Update Student", "🗑️ Delete Student", "📥 Import Students", "📈 Student Analytics"])
        handle_student_menu(student_menu)
    else:
        fees_menu = st.sidebar.radio("Operations:", ["💵 Collect Payment", "📋 View Payments", "🔍 Student Fee History", "⚙️ Fee Structure", "📊 Fees Dashboard", "📄 Reports", "⚠️ Defaulters"])
        handle_fees_menu(fees_menu)

if __name__ == "__main__":
    main()
