import streamlit as st
import pandas as pd
import os
from datetime import datetime
import re
from io import BytesIO
import hashlib

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
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'login_attempts' not in st.session_state:
    st.session_state.login_attempts = 0

# Excel file paths
STUDENT_FILE = "students_data.xlsx"
FEE_STRUCTURE_FILE = "fee_structure.xlsx"
FEE_PAYMENTS_FILE = "fee_payments.xlsx"

# Standard options with sections
STANDARDS = [
    "Playground - Section A", "Playground - Section B",
    "Nursery - Section A", "Nursery - Section B",
    "Jr.KG - Section A", "Jr.KG - Section B",
    "Sr.KG - Section A", "Sr.KG - Section B"
]

# Age options (2 to 10)
AGE_OPTIONS = [2, 3, 4, 5, 6, 7, 8, 9, 10]

# Fee types
FEE_TYPES = [
    "Tuition Fees",
    "Admission Fees",
    "Transportation Fees",
    "Activity/Sports Fees",
    "Books/Uniform Fees",
    "Examination Fees",
    "Other Fees"
]

# Payment modes
PAYMENT_MODES = ["Cash", "Online/UPI", "Cheque", "Card", "Bank Transfer"]

# Initialize Excel files
def initialize_student_excel():
    if not os.path.exists(STUDENT_FILE):
        df = pd.DataFrame(columns=[
            'Student_ID', 'Name', 'Standard', 'Blood_Group',
            'Address', 'Aadhar_Details', 'Age'
        ])
        df.to_excel(STUDENT_FILE, index=False)
        return df
    else:
        return pd.read_excel(STUDENT_FILE)

def initialize_fee_structure():
    if not os.path.exists(FEE_STRUCTURE_FILE):
        df = pd.DataFrame(columns=[
            'Fee_ID', 'Standard', 'Fee_Type', 'Amount',
            'Payment_Frequency', 'Academic_Year'
        ])
        df.to_excel(FEE_STRUCTURE_FILE, index=False)
        return df
    else:
        return pd.read_excel(FEE_STRUCTURE_FILE)

def initialize_fee_payments():
    if not os.path.exists(FEE_PAYMENTS_FILE):
        df = pd.DataFrame(columns=[
            'Receipt_No', 'Student_ID', 'Student_Name', 'Standard',
            'Payment_Date', 'Amount_Paid', 'Payment_Mode',
            'Fee_Type', 'Academic_Year', 'Remarks'
        ])
        df.to_excel(FEE_PAYMENTS_FILE, index=False)
        return df
    else:
        return pd.read_excel(FEE_PAYMENTS_FILE)

# Load data functions
def load_students():
    try:
        df = pd.read_excel(STUDENT_FILE)
        if df.empty:
            df = pd.DataFrame(columns=[
                'Student_ID', 'Name', 'Standard', 'Blood_Group',
                'Address', 'Aadhar_Details', 'Age'
            ])
        return df
    except Exception as e:
        st.error(f"Error loading students: {e}")
        return pd.DataFrame(columns=[
            'Student_ID', 'Name', 'Standard', 'Blood_Group',
            'Address', 'Aadhar_Details', 'Age'
        ])

def load_fee_structure():
    try:
        return pd.read_excel(FEE_STRUCTURE_FILE)
    except:
        return pd.DataFrame(columns=[
            'Fee_ID', 'Standard', 'Fee_Type', 'Amount',
            'Payment_Frequency', 'Academic_Year'
        ])

def load_fee_payments():
    try:
        return pd.read_excel(FEE_PAYMENTS_FILE)
    except:
        return pd.DataFrame(columns=[
            'Receipt_No', 'Student_ID', 'Student_Name', 'Standard',
            'Payment_Date', 'Amount_Paid', 'Payment_Mode',
            'Fee_Type', 'Academic_Year', 'Remarks'
        ])

# Save data functions
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

# Generate unique IDs
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

# Validation functions
def validate_aadhar(aadhar):
    pattern = r'^\d{12}$'
    return bool(re.match(pattern, aadhar.replace(" ", "")))

# Calculate pending fees
def calculate_pending_fees(student_id, students_df, fee_structure_df, payments_df):
    student = students_df[students_df['Student_ID'] == student_id]
    if student.empty:
        return 0, 0, 0

    standard = student.iloc[0]['Standard']

    # Get total fee structure for this standard
    total_fees = fee_structure_df[fee_structure_df['Standard'] == standard]['Amount'].sum()

    # Get total paid by student
    total_paid = payments_df[payments_df['Student_ID'] == student_id]['Amount_Paid'].sum()

    pending = total_fees - total_paid

    return total_fees, total_paid, pending

# Main app
def main():
    st.title("🎓 School Management System")
    st.markdown("---")

    # Initialize Excel files
    initialize_student_excel()
    initialize_fee_structure()
    initialize_fee_payments()

    # Sidebar with custom styling
    st.sidebar.markdown("""
        <style>
        .sidebar .sidebar-content {
            font-size: 18px;
        }
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
            font-size: 20px;
        }
        [data-testid="stSidebar"] .row-widget.stRadio > div {
            font-size: 18px;
        }
        [data-testid="stSidebar"] .row-widget.stRadio label {
            font-size: 18px;
        }
        </style>
    """, unsafe_allow_html=True)

    st.sidebar.title("📚 Navigation")

    main_menu = st.sidebar.radio(
        "Main Menu:",
        ["👨‍🎓 Student Management", "💰 Fees Management"]
    )

    if main_menu == "👨‍🎓 Student Management":
        student_menu = st.sidebar.radio(
            "Student Operations:",
            ["📊 View Students", "➕ Add Student", "✏️ Update Student",
             "🗑️ Delete Student", "📥 Import Students", "📈 Student Analytics"]
        )
        handle_student_menu(student_menu)

    else:  # Fees Management
        fees_menu = st.sidebar.radio(
            "Fees Operations:",
            ["💵 Collect Payment", "📋 View Payments", "🔍 Student Fee History",
             "⚙️ Fee Structure", "📊 Fees Dashboard", "📄 Reports", "⚠️ Defaulters"]
        )
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
                filter_standard = st.selectbox("Filter by Standard:", ["All"] + sorted(students_df['Standard'].unique().tolist()))

            filtered_df = students_df.copy()
            if search_term:
                filtered_df = filtered_df[
                    filtered_df['Name'].str.contains(search_term, case=False, na=False) |
                    filtered_df['Student_ID'].str.contains(search_term, case=False, na=False)
                ]
            if filter_standard != "All":
                filtered_df = filtered_df[filtered_df['Standard'] == filter_standard]

            st.dataframe(filtered_df, use_container_width=True, height=400)
            st.info(f"📊 Total Students: {len(filtered_df)}")

            # Export
            buffer = BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                filtered_df.to_excel(writer, index=False, sheet_name='Students')
            buffer.seek(0)

            st.download_button(
                label="💾 Export to Excel",
                data=buffer,
                file_name=f"students_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    elif menu == "➕ Add Student":
        st.header("➕ Add New Student")

        with st.form("add_student_form"):
            col1, col2 = st.columns(2)

            with col1:
                name = st.text_input("Name *", placeholder="Enter student name")
                standard = st.selectbox("Standard *", ["Select"] + STANDARDS)
                blood_group = st.selectbox("Blood Group *",
                    ["Select", "A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"])

            with col2:
                age = st.selectbox("Age *", ["Select"] + AGE_OPTIONS)
                aadhar = st.text_input("Aadhar Details *", placeholder="Enter 12-digit Aadhar number")
                address = st.text_area("Address *", placeholder="Enter complete address")

            submit = st.form_submit_button("➕ Add Student")

            if submit:
                if not name or standard == "Select" or blood_group == "Select" or age == "Select" or not address or not aadhar:
                    st.error("❌ Please fill all required fields!")
                elif not validate_aadhar(aadhar):
                    st.error("❌ Invalid Aadhar number! Must be 12 digits.")
                else:
                    new_id = generate_student_id(students_df)
                    new_student = pd.DataFrame({
                        'Student_ID': [new_id],
                        'Name': [name],
                        'Standard': [standard],
                        'Blood_Group': [blood_group],
                        'Address': [address],
                        'Aadhar_Details': [aadhar],
                        'Age': [age]
                    })

                    students_df = pd.concat([students_df, new_student], ignore_index=True)

                    if save_students(students_df):
                        st.success(f"✅ Student added successfully! Student ID: {new_id}")
                        st.balloons()
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

                with st.form("update_student_form"):
                    col1, col2 = st.columns(2)

                    with col1:
                        name = st.text_input("Name *", value=student_data['Name'])
                        try:
                            standard_index = STANDARDS.index(student_data['Standard'])
                        except ValueError:
                            standard_index = 0
                        standard = st.selectbox("Standard *", STANDARDS, index=standard_index)

                        blood_group_list = ["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"]
                        try:
                            bg_index = blood_group_list.index(student_data['Blood_Group'])
                        except ValueError:
                            bg_index = 0
                        blood_group = st.selectbox("Blood Group *", blood_group_list, index=bg_index)

                    with col2:
                        try:
                            age_index = AGE_OPTIONS.index(int(student_data['Age']))
                        except (ValueError, TypeError):
                            age_index = 0
                        age = st.selectbox("Age *", AGE_OPTIONS, index=age_index)

                        aadhar = st.text_input("Aadhar Details *", value=student_data['Aadhar_Details'])
                        address = st.text_area("Address *", value=student_data['Address'])

                    update = st.form_submit_button("💾 Update Student")

                    if update:
                        if not name or not address or not aadhar:
                            st.error("❌ Please fill all required fields!")
                        elif not validate_aadhar(aadhar):
                            st.error("❌ Invalid Aadhar number! Must be 12 digits.")
                        else:
                            students_df.loc[students_df['Student_ID'] == student_id, 'Name'] = name
                            students_df.loc[students_df['Student_ID'] == student_id, 'Standard'] = standard
                            students_df.loc[students_df['Student_ID'] == student_id, 'Blood_Group'] = blood_group
                            students_df.loc[students_df['Student_ID'] == student_id, 'Address'] = address
                            students_df.loc[students_df['Student_ID'] == student_id, 'Aadhar_Details'] = aadhar
                            students_df.loc[students_df['Student_ID'] == student_id, 'Age'] = age

                            if save_students(students_df):
                                st.success("✅ Student updated successfully!")
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

                st.write("### Student Details:")
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Name:** {student_data['Name']}")
                    st.write(f"**Standard:** {student_data['Standard']}")
                    st.write(f"**Blood Group:** {student_data['Blood_Group']}")
                with col2:
                    st.write(f"**Age:** {student_data['Age']}")
                    st.write(f"**Aadhar:** {student_data['Aadhar_Details']}")
                    st.write(f"**Address:** {student_data['Address']}")

                st.warning("⚠️ This action cannot be undone!")

                if st.button("🗑️ Confirm Delete", type="primary"):
                    students_df = students_df[students_df['Student_ID'] != student_id]
                    if save_students(students_df):
                        st.success("✅ Student deleted successfully!")
                        st.rerun()
                    else:
                        st.error("❌ Failed to delete student!")

    elif menu == "📥 Import Students":
        st.header("📥 Import Students from Excel")

        st.info("📋 **Excel File Requirements:**\n"
                "- Must have columns: Name, Standard, Blood_Group, Address, Aadhar_Details, Age\n"
                "- Standard must be one of: Playground/Nursery/Jr.KG/Sr.KG - Section A/B\n"
                "- Blood Group: A+, A-, B+, B-, O+, O-, AB+, AB-\n"
                "- Age: 2-10\n"
                "- Aadhar: 12 digits")

        st.subheader("📥 Step 1: Download Template")

        template_df = pd.DataFrame({
            'Name': ['Sample Student'],
            'Standard': ['Playground - Section A'],
            'Blood_Group': ['A+'],
            'Address': ['Sample Address'],
            'Aadhar_Details': ['123456789012'],
            'Age': [5]
        })

        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            template_df.to_excel(writer, index=False, sheet_name='Students')
        buffer.seek(0)

        st.download_button(
            label="📥 Download Excel Template",
            data=buffer,
            file_name="student_import_template.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        st.markdown("---")
        st.subheader("📤 Step 2: Upload Your Excel File")

        uploaded_file = st.file_uploader("Choose an Excel file", type=['xlsx', 'xls'])

        if uploaded_file is not None:
            try:
                import_df = pd.read_excel(uploaded_file)

                st.subheader("📊 Preview of Uploaded Data")
                st.dataframe(import_df.head(10), use_container_width=True)
                st.info(f"Total rows in file: {len(import_df)}")

                required_columns = ['Name', 'Standard', 'Blood_Group', 'Address', 'Aadhar_Details', 'Age']
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

                        import_mode = st.radio(
                            "Choose import mode:",
                            ["Append to existing data", "Replace all existing data"]
                        )

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

                                    new_students.append({
                                        'Student_ID': new_id,
                                        'Name': row['Name'],
                                        'Standard': row['Standard'],
                                        'Blood_Group': row['Blood_Group'],
                                        'Address': row['Address'],
                                        'Aadhar_Details': row['Aadhar_Details'],
                                        'Age': int(row['Age'])
                                    })

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
                st.metric("Total Standards", students_df['Standard'].nunique())
            with col3:
                avg_age = students_df['Age'].astype(float).mean()
                st.metric("Average Age", f"{avg_age:.1f}")
            with col4:
                most_common_bg = students_df['Blood_Group'].mode()[0]
                st.metric("Most Common Blood Group", most_common_bg)

            st.markdown("---")

            col1, col2 = st.columns(2)

            with col1:
                st.subheader("Students by Standard")
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
                    st.info(f"**Name:** {student['Name']}\n\n**Standard:** {student['Standard']}")

                    total_fee, paid, pending = calculate_pending_fees(student_id, students_df, fee_structure_df, payments_df)
                    st.metric("Pending Fees", f"₹{pending:.2f}")

                fee_type = st.selectbox("Fee Type *", FEE_TYPES)
                amount = st.number_input("Amount (₹) *", min_value=0.0, step=100.0)

            with col2:
                payment_date = st.date_input("Payment Date *", datetime.now())
                payment_mode = st.selectbox("Payment Mode *", PAYMENT_MODES)
                academic_year = st.text_input("Academic Year *", value=f"{datetime.now().year}-{datetime.now().year+1}")
                remarks = st.text_area("Remarks", placeholder="Optional notes")

            submit = st.form_submit_button("💰 Process Payment")

            if submit:
                if not student_id or amount <= 0:
                    st.error("❌ Please fill all required fields!")
                else:
                    receipt_no = generate_receipt_no(payments_df)

                    new_payment = pd.DataFrame({
                        'Receipt_No': [receipt_no],
                        'Student_ID': [student_id],
                        'Student_Name': [student['Name']],
                        'Standard': [student['Standard']],
                        'Payment_Date': [payment_date],
                        'Amount_Paid': [amount],
                        'Payment_Mode': [payment_mode],
                        'Fee_Type': [fee_type],
                        'Academic_Year': [academic_year],
                        'Remarks': [remarks]
                    })

                    payments_df = pd.concat([payments_df, new_payment], ignore_index=True)

                    if save_fee_payments(payments_df):
                        st.success(f"✅ Payment processed successfully! Receipt No: {receipt_no}")
                        st.balloons()

                        # Show receipt
                        st.markdown("---")
                        st.subheader("📄 Payment Receipt")
                        receipt_col1, receipt_col2 = st.columns(2)
                        with receipt_col1:
                            st.write(f"**Receipt No:** {receipt_no}")
                            st.write(f"**Date:** {payment_date}")
                            st.write(f"**Student ID:** {student_id}")
                            st.write(f"**Name:** {student['Name']}")
                        with receipt_col2:
                            st.write(f"**Standard:** {student['Standard']}")
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
                filtered_df = filtered_df[
                    filtered_df['Student_ID'].str.contains(search_term, case=False, na=False) |
                    filtered_df['Student_Name'].str.contains(search_term, case=False, na=False)
                ]
            if fee_type_filter != "All":
                filtered_df = filtered_df[filtered_df['Fee_Type'] == fee_type_filter]
            if payment_mode_filter != "All":
                filtered_df = filtered_df[filtered_df['Payment_Mode'] == payment_mode_filter]

            st.dataframe(filtered_df, use_container_width=True, height=400)
            st.info(f"📊 Total Payments: {len(filtered_df)} | Total Amount: ₹{filtered_df['Amount_Paid'].sum():.2f}")

            # Export
            buffer = BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                filtered_df.to_excel(writer, index=False, sheet_name='Payments')
            buffer.seek(0)

            st.download_button(
                label="💾 Export Payments to Excel",
                data=buffer,
                file_name=f"fee_payments_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

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
                    st.write(f"**Standard:** {student['Standard']}")
                    st.write(f"**Age:** {student['Age']}")

                with col2:
                    st.write("### Fee Summary")
                    total_fee, paid, pending = calculate_pending_fees(student_id, students_df, fee_structure_df, payments_df)
                    st.metric("Total Fee Structure", f"₹{total_fee:.2f}")
                    st.metric("Total Paid", f"₹{paid:.2f}", delta=f"{(paid/total_fee*100) if total_fee > 0 else 0:.1f}%")
                    st.metric("Pending", f"₹{pending:.2f}", delta=f"-{(pending/total_fee*100) if total_fee > 0 else 0:.1f}%", delta_color="inverse")

                st.markdown("---")
                st.subheader("Payment History")

                student_payments = payments_df[payments_df['Student_ID'] == student_id]

                if student_payments.empty:
                    st.info("No payment history found for this student.")
                else:
                    st.dataframe(student_payments, use_container_width=True)

                    # Export student history
                    buffer = BytesIO()
                    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                        student_payments.to_excel(writer, index=False, sheet_name='Payment_History')
                    buffer.seek(0)

                    st.download_button(
                        label="💾 Export Student History",
                        data=buffer,
                        file_name=f"student_{student_id}_history_{datetime.now().strftime('%Y%m%d')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )

    elif menu == "⚙️ Fee Structure":
        st.header("⚙️ Fee Structure Management")

        tab1, tab2 = st.tabs(["📋 View Structure", "➕ Add/Update Fee"])

        with tab1:
            if fee_structure_df.empty:
                st.info("No fee structure defined. Add fee structure to get started!")
            else:
                st.dataframe(fee_structure_df, use_container_width=True)

                # Export
                buffer = BytesIO()
                with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                    fee_structure_df.to_excel(writer, index=False, sheet_name='Fee_Structure')
                buffer.seek(0)

                st.download_button(
                    label="💾 Export Fee Structure",
                    data=buffer,
                    file_name=f"fee_structure_{datetime.now().strftime('%Y%m%d')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

        with tab2:
            with st.form("fee_structure_form"):
                col1, col2 = st.columns(2)

                with col1:
                    standard = st.selectbox("Standard *", STANDARDS)
                    fee_type = st.selectbox("Fee Type *", FEE_TYPES)
                    amount = st.number_input("Amount (₹) *", min_value=0.0, step=100.0)

                with col2:
                    payment_frequency = st.selectbox("Payment Frequency *",
                        ["One-time", "Monthly", "Quarterly", "Half-Yearly", "Yearly"])
                    academic_year = st.text_input("Academic Year *",
                        value=f"{datetime.now().year}-{datetime.now().year+1}")

                submit = st.form_submit_button("💾 Save Fee Structure")

                if submit:
                    if not standard or not fee_type or amount <= 0:
                        st.error("❌ Please fill all required fields!")
                    else:
                        # Check if fee already exists
                        existing = fee_structure_df[
                            (fee_structure_df['Standard'] == standard) &
                            (fee_structure_df['Fee_Type'] == fee_type) &
                            (fee_structure_df['Academic_Year'] == academic_year)
                        ]

                        if not existing.empty:
                            # Update existing
                            fee_structure_df.loc[
                                (fee_structure_df['Standard'] == standard) &
                                (fee_structure_df['Fee_Type'] == fee_type) &
                                (fee_structure_df['Academic_Year'] == academic_year),
                                'Amount'
                            ] = amount
                            fee_structure_df.loc[
                                (fee_structure_df['Standard'] == standard) &
                                (fee_structure_df['Fee_Type'] == fee_type) &
                                (fee_structure_df['Academic_Year'] == academic_year),
                                'Payment_Frequency'
                            ] = payment_frequency
                            message = "updated"
                        else:
                            # Add new
                            fee_id = generate_fee_id(fee_structure_df)
                            new_fee = pd.DataFrame({
                                'Fee_ID': [fee_id],
                                'Standard': [standard],
                                'Fee_Type': [fee_type],
                                'Amount': [amount],
                                'Payment_Frequency': [payment_frequency],
                                'Academic_Year': [academic_year]
                            })
                            fee_structure_df = pd.concat([fee_structure_df, new_fee], ignore_index=True)
                            message = "added"

                        if save_fee_structure(fee_structure_df):
                            st.success(f"✅ Fee structure {message} successfully!")
                        else:
                            st.error("❌ Failed to save fee structure!")

    elif menu == "📊 Fees Dashboard":
        st.header("📊 Fees Dashboard")

        if payments_df.empty and fee_structure_df.empty:
            st.info("No fee data available. Add fee structure and collect payments to see analytics!")
            return

        # Summary Metrics
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
            st.metric("Total Pending", f"₹{pending_total:,.2f}", delta=f"-{(pending_total/total_expected*100) if total_expected > 0 else 0:.1f}%", delta_color="inverse")

        with col4:
            collection_rate = (total_collected/total_expected*100) if total_expected > 0 else 0
            st.metric("Collection Rate", f"{collection_rate:.1f}%")

        st.markdown("---")

        # Charts
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

            # Monthly trend
            st.subheader("📅 Monthly Collection Trend")
            payments_df['Payment_Date'] = pd.to_datetime(payments_df['Payment_Date'])
            payments_df['Month'] = payments_df['Payment_Date'].dt.to_period('M').astype(str)
            monthly_collection = payments_df.groupby('Month')['Amount_Paid'].sum()
            st.line_chart(monthly_collection)

            st.markdown("---")

            # Standard-wise collection
            st.subheader("🎓 Standard-wise Collection")
            standard_collection = payments_df.groupby('Standard')['Amount_Paid'].sum().sort_values(ascending=False)
            st.bar_chart(standard_collection)

            # Recent transactions
            st.markdown("---")
            st.subheader("🕐 Recent Transactions (Last 10)")
            recent = payments_df.sort_values('Payment_Date', ascending=False).head(10)
            st.dataframe(recent[['Receipt_No', 'Student_ID', 'Student_Name', 'Amount_Paid', 'Payment_Date', 'Fee_Type']],
                        use_container_width=True)

    elif menu == "📄 Reports":
        st.header("📄 Generate Reports")

        report_type = st.selectbox("Select Report Type", [
            "Daily Collection Report",
            "Monthly Collection Report",
            "Standard-wise Collection",
            "Fee Type-wise Collection",
            "Payment Mode Report",
            "Custom Date Range Report"
        ])

        if report_type == "Daily Collection Report":
            report_date = st.date_input("Select Date", datetime.now())

            if st.button("Generate Report"):
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

                    # Export
                    buffer = BytesIO()
                    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                        daily_payments.to_excel(writer, index=False, sheet_name='Daily_Report')
                    buffer.seek(0)

                    st.download_button(
                        label="💾 Download Report",
                        data=buffer,
                        file_name=f"daily_report_{report_date}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )

        elif report_type == "Monthly Collection Report":
            col1, col2 = st.columns(2)
            with col1:
                month = st.selectbox("Month", range(1, 13), index=datetime.now().month-1)
            with col2:
                year = st.number_input("Year", min_value=2020, max_value=2030, value=datetime.now().year)

            if st.button("Generate Report"):
                payments_df['Payment_Date'] = pd.to_datetime(payments_df['Payment_Date'])
                monthly_payments = payments_df[
                    (payments_df['Payment_Date'].dt.month == month) &
                    (payments_df['Payment_Date'].dt.year == year)
                ]

                if monthly_payments.empty:
                    st.warning(f"No payments found for {month}/{year}")
                else:
                    st.subheader(f"Monthly Report - {month}/{year}")

                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total Transactions", len(monthly_payments))
                    with col2:
                        st.metric("Total Amount", f"₹{monthly_payments['Amount_Paid'].sum():,.2f}")
                    with col3:
                        st.metric("Unique Students", monthly_payments['Student_ID'].nunique())

                    # Daily breakdown
                    st.subheader("Daily Breakdown")
                    daily_breakdown = monthly_payments.groupby(monthly_payments['Payment_Date'].dt.day)['Amount_Paid'].sum()
                    st.bar_chart(daily_breakdown)

                    st.dataframe(monthly_payments, use_container_width=True)

                    # Export
                    buffer = BytesIO()
                    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                        monthly_payments.to_excel(writer, index=False, sheet_name='Monthly_Report')
                    buffer.seek(0)

                    st.download_button(
                        label="💾 Download Report",
                        data=buffer,
                        file_name=f"monthly_report_{month}_{year}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )

        elif report_type == "Custom Date Range Report":
            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input("Start Date")
            with col2:
                end_date = st.date_input("End Date", datetime.now())

            if st.button("Generate Report"):
                payments_df['Payment_Date'] = pd.to_datetime(payments_df['Payment_Date'])
                range_payments = payments_df[
                    (payments_df['Payment_Date'].dt.date >= start_date) &
                    (payments_df['Payment_Date'].dt.date <= end_date)
                ]

                if range_payments.empty:
                    st.warning(f"No payments found between {start_date} and {end_date}")
                else:
                    st.subheader(f"Report: {start_date} to {end_date}")

                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total Transactions", len(range_payments))
                    with col2:
                        st.metric("Total Amount", f"₹{range_payments['Amount_Paid'].sum():,.2f}")
                    with col3:
                        st.metric("Unique Students", range_payments['Student_ID'].nunique())

                    st.dataframe(range_payments, use_container_width=True)

                    # Export
                    buffer = BytesIO()
                    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                        range_payments.to_excel(writer, index=False, sheet_name='Custom_Report')
                    buffer.seek(0)

                    st.download_button(
                        label="💾 Download Report",
                        data=buffer,
                        file_name=f"report_{start_date}_to_{end_date}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )

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
                last_payment = payments_df[payments_df['Student_ID'] == student_id]
                last_payment_date = last_payment['Payment_Date'].max() if not last_payment.empty else "Never"

                defaulters.append({
                    'Student_ID': student_id,
                    'Name': student['Name'],
                    'Standard': student['Standard'],
                    'Total_Fee': total_fee,
                    'Paid': paid,
                    'Pending': pending,
                    'Last_Payment': last_payment_date,
                    'Contact': student.get('Address', 'N/A')
                })

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

            # Export
            buffer = BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                defaulters_df.to_excel(writer, index=False, sheet_name='Defaulters')
            buffer.seek(0)

            st.download_button(
                label="💾 Export Defaulters List",
                data=buffer,
                file_name=f"defaulters_list_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

if __name__ == "__main__":
    main()
