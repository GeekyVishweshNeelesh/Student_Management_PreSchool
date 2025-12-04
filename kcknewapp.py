import streamlit as st
import pandas as pd
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
import os
from datetime import datetime
import json
import io

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================
st.set_page_config(
    page_title="School Management System",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# CUSTOM CSS & STYLING - ENHANCED MENU FONT SIZE AND BOLDNESS
# ============================================================================
st.markdown("""
    <style>
    /* Main container styling */
    .main {
        padding: 20px;
        background-color: #f5f7fa;
    }
    
    /* Card styling */
    .card {
        background-color: white;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin: 10px 0;
    }
    
    /* Header styling */
    h1 {
        color: #1f3a93;
        text-align: center;
        margin-bottom: 30px;
        font-size: 2.5em;
        font-weight: 900;
    }
    
    h2 {
        color: #2d5aa0;
        border-bottom: 3px solid #2d5aa0;
        padding-bottom: 10px;
        margin-top: 20px;
    }
    
    /* Success and error messages */
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        padding: 15px;
        margin: 10px 0;
    }
    
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 5px;
        padding: 15px;
        margin: 10px 0;
    }
    
    /* Button styling */
    .stButton > button {
        background-color: #2d5aa0;
        color: white;
        border-radius: 5px;
        padding: 10px 20px;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background-color: #1f3a93;
        transform: scale(1.02);
    }
    
    /* Input field styling */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > select {
        border-radius: 5px;
        border: 2px solid #2d5aa0;
        padding: 10px;
    }
    
    /* Table styling */
    .stDataFrame {
        width: 100%;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    
    </style>
""", unsafe_allow_html=True)

# ============================================================================
# SIDEBAR STYLING - ENHANCED MAIN MENU AND OPERATIONS
# ============================================================================
st.sidebar.markdown('''
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@700;800;900&display=swap');
        
        /* Main sidebar styling */
        [data-testid="stSidebar"] {
            background: linear-gradient(135deg, #1f3a93 0%, #2d5aa0 100%);
            font-size: 44px;
        }
        
        /* Sidebar labels */
        [data-testid="stSidebar"] label {
            font-size: 44px !important;
            font-weight: 800;
            color: #ffffff;
        }
        
        /* MAIN MENU AND OPERATIONS HEADERS - EXTRA BOLD AND LARGE */
        [data-testid="stSidebar"] .stRadio > label {
            font-size: 80px !important;
            font-weight: 900;
            color: #ffffff;
            text-shadow: 5px 5px 10px rgba(0,0,0,0.6), 2px 2px 4px rgba(0,0,0,0.8);
            letter-spacing: 2px;
            -webkit-text-stroke: 1.5px rgba(0,0,0,0.5);
            line-height: 1.2;
            font-family: 'Poppins', 'Arial Black', sans-serif;
            margin: 15px 0;
            padding: 20px 0;
            text-transform: uppercase;
            word-wrap: break-word;
        }
        
        /* MENU ITEMS - EXTRA BOLD AND LARGE */
        [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label {
            font-size: 75px !important;
            padding: 25px 10px;
            font-weight: 900;
            color: #ffffff;
            text-shadow: 5px 5px 10px rgba(0,0,0,0.6), 2px 2px 4px rgba(0,0,0,0.8);
            -webkit-text-stroke: 1.5px rgba(0,0,0,0.5);
            line-height: 1.3;
            font-family: 'Poppins', 'Arial Black', sans-serif;
            margin: 12px 0;
            border-radius: 8px;
            transition: all 0.3s ease;
        }
        
        /* Menu item hover effect */
        [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:hover {
            background-color: rgba(255,255,255,0.15);
            transform: scale(1.05);
        }
        
        /* Selected menu item */
        [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label[aria-checked="true"] {
            background-color: rgba(255,255,255,0.25);
            border-left: 5px solid #ffd700;
            padding-left: 15px;
        }
        
        /* Sidebar title */
        [data-testid="stSidebar"] h1 {
            font-size: 56px !important;
            font-weight: 900;
            color: #ffffff;
            text-shadow: 4px 4px 8px rgba(0,0,0,0.6);
            -webkit-text-stroke: 1px rgba(0,0,0,0.4);
            margin-bottom: 30px;
            font-family: 'Poppins', 'Arial Black', sans-serif;
        }
        
        /* Sidebar text and paragraphs */
        [data-testid="stSidebar"] p {
            font-size: 32px !important;
            color: #ffffff;
            font-weight: 700;
            margin: 10px 0;
        }
        
        /* Expander styling */
        [data-testid="stSidebar"] .streamlit-expander {
            background-color: rgba(255,255,255,0.1);
            border-radius: 8px;
            border: 2px solid rgba(255,255,255,0.2);
        }
        
        /* Section dividers */
        [data-testid="stSidebar"] hr {
            border-color: rgba(255,255,255,0.3);
            margin: 20px 0;
        }
    </style>
''', unsafe_allow_html=True)

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

@st.cache_resource
def initialize_student_excel():
    """Initialize or load student Excel file"""
    if not os.path.exists('students.xlsx'):
        df = pd.DataFrame(columns=['Student_ID', 'Name', 'Standard', 'Blood_Group', 'Address', 'Aadhar_Details', 'Age'])
        with pd.ExcelWriter('students.xlsx', engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Students')
        return df
    return pd.read_excel('students.xlsx')

@st.cache_resource
def initialize_fee_structure():
    """Initialize fee structure"""
    if not os.path.exists('fee_structure.xlsx'):
        df = pd.DataFrame({
            'Standard': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            'Monthly_Fee': [1000, 1500, 2000, 2500, 3000, 3500, 4000, 4500, 5000, 5500]
        })
        with pd.ExcelWriter('fee_structure.xlsx', engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Fee_Structure')
        return df
    return pd.read_excel('fee_structure.xlsx')

@st.cache_resource
def initialize_fee_payments():
    """Initialize fee payments tracking"""
    if not os.path.exists('fee_payments.xlsx'):
        df = pd.DataFrame(columns=['Payment_ID', 'Student_ID', 'Month', 'Year', 'Amount_Paid', 'Payment_Date', 'Status'])
        with pd.ExcelWriter('fee_payments.xlsx', engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Payments')
        return df
    return pd.read_excel('fee_payments.xlsx')

def get_next_student_id():
    """Generate next student ID"""
    students_df = pd.read_excel('students.xlsx')
    if len(students_df) == 0:
        return 1001
    return int(students_df['Student_ID'].max()) + 1

def save_to_excel(data, filename, sheet_name):
    """Save data to Excel file"""
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        data.to_excel(writer, index=False, sheet_name=sheet_name)

# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main():
    # Initialize session state
    if 'refresh' not in st.session_state:
        st.session_state.refresh = False
    
    # Initialize data
    initialize_student_excel()
    initialize_fee_structure()
    initialize_fee_payments()
    
    # ========================================================================
    # SIDEBAR WITH ENHANCED MENU STYLING
    # ========================================================================
    st.sidebar.markdown("""---""")
    
    st.sidebar.title("📚 School Management")
    
    # Main menu
    st.sidebar.markdown("<div style='font-size:80px; font-weight:900; color:white; text-shadow: 5px 5px 10px rgba(0,0,0,0.6);'>🎓 MAIN MENU</div>", unsafe_allow_html=True)
    
    main_menu = st.sidebar.radio(
        "Select Main Option:",
        ["📊 Dashboard", "👥 Students Management"],
        label_visibility="collapsed"
    )
    
    # Operations menu
    st.sidebar.markdown("<div style='font-size:80px; font-weight:900; color:white; text-shadow: 5px 5px 10px rgba(0,0,0,0.6); margin-top: 30px;'>⚙️ OPERATIONS</div>", unsafe_allow_html=True)
    
    if main_menu == "📊 Dashboard":
        operations = st.sidebar.radio(
            "Select Operation:",
            ["📈 Overview", "💰 Fee Management", "📊 Reports"],
            label_visibility="collapsed"
        )
    else:
        operations = st.sidebar.radio(
            "Select Operation:",
            ["📊 View Students", "➕ Add Student", "✏️ Update Student", "🗑️ Delete Student", "📥 Import from Excel"],
            label_visibility="collapsed"
        )
    
    st.sidebar.markdown("---")
    
    # ========================================================================
    # MAIN CONTENT AREA
    # ========================================================================
    
    st.markdown("<h1>📚 School Management System</h1>", unsafe_allow_html=True)
    
    # Dashboard
    if main_menu == "📊 Dashboard":
        if operations == "📈 Overview":
            col1, col2, col3 = st.columns(3)
            
            students_df = pd.read_excel('students.xlsx')
            payments_df = pd.read_excel('fee_payments.xlsx')
            
            with col1:
                st.metric("Total Students", len(students_df))
            with col2:
                total_fees = payments_df['Amount_Paid'].sum() if len(payments_df) > 0 else 0
                st.metric("Total Fees Collected", f"₹{total_fees:,.2f}")
            with col3:
                pending_payments = len(payments_df[payments_df['Status'] == 'Pending']) if len(payments_df) > 0 else 0
                st.metric("Pending Payments", pending_payments)
            
            st.markdown("### 📊 Student Distribution by Standard")
            if len(students_df) > 0:
                standard_dist = students_df['Standard'].value_counts().sort_index()
                st.bar_chart(standard_dist)
        
        elif operations == "💰 Fee Management":
            st.markdown("### 💰 Fee Structure Management")
            fee_df = pd.read_excel('fee_structure.xlsx')
            st.dataframe(fee_df, use_container_width=True)
            
            st.markdown("### 📝 Record Payment")
            col1, col2, col3 = st.columns(3)
            with col1:
                students_df = pd.read_excel('students.xlsx')
                student_names = students_df['Name'].tolist()
                selected_student = st.selectbox("Select Student", student_names)
            with col2:
                month = st.selectbox("Month", ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"])
            with col3:
                year = st.number_input("Year", value=datetime.now().year, min_value=2020)
            
            amount = st.number_input("Amount (₹)", min_value=0.0)
            
            if st.button("Record Payment"):
                payments_df = pd.read_excel('fee_payments.xlsx')
                student_id = students_df[students_df['Name'] == selected_student]['Student_ID'].values[0]
                new_payment = {
                    'Payment_ID': len(payments_df) + 1,
                    'Student_ID': student_id,
                    'Month': month,
                    'Year': year,
                    'Amount_Paid': amount,
                    'Payment_Date': datetime.now().date(),
                    'Status': 'Paid'
                }
                payments_df = pd.concat([payments_df, pd.DataFrame([new_payment])], ignore_index=True)
                save_to_excel(payments_df, 'fee_payments.xlsx', 'Payments')
                st.success("✅ Payment recorded successfully!")
    
    # Students Management
    else:
        if operations == "📊 View Students":
            st.markdown("### 👥 All Students")
            students_df = pd.read_excel('students.xlsx')
            if len(students_df) > 0:
                st.dataframe(students_df, use_container_width=True)
            else:
                st.info("No students found. Add students to get started!")
        
        elif operations == "➕ Add Student":
            st.markdown("### ➕ Add New Student")
            with st.form("add_student_form"):
                col1, col2 = st.columns(2)
                with col1:
                    name = st.text_input("Student Name")
                    standard = st.number_input("Standard", min_value=1, max_value=12)
                with col2:
                    blood_group = st.selectbox("Blood Group", ["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"])
                    age = st.number_input("Age", min_value=3, max_value=18)
                
                address = st.text_area("Address")
                aadhar = st.text_input("Aadhar Number")
                
                submitted = st.form_submit_button("Add Student")
                
                if submitted:
                    if name and address and aadhar:
                        students_df = pd.read_excel('students.xlsx')
                        new_student = {
                            'Student_ID': get_next_student_id(),
                            'Name': name,
                            'Standard': standard,
                            'Blood_Group': blood_group,
                            'Address': address,
                            'Aadhar_Details': aadhar,
                            'Age': age
                        }
                        students_df = pd.concat([students_df, pd.DataFrame([new_student])], ignore_index=True)
                        save_to_excel(students_df, 'students.xlsx', 'Students')
                        st.success(f"✅ Student {name} added successfully with ID: {new_student['Student_ID']}")
                    else:
                        st.error("❌ Please fill all required fields!")
        
        elif operations == "✏️ Update Student":
            st.markdown("### ✏️ Update Student Information")
            students_df = pd.read_excel('students.xlsx')
            
            if len(students_df) > 0:
                student_names = students_df['Name'].tolist()
                selected_student = st.selectbox("Select Student", student_names)
                student_data = students_df[students_df['Name'] == selected_student].iloc[0]
                
                with st.form("update_student_form"):
                    col1, col2 = st.columns(2)
                    with col1:
                        new_name = st.text_input("Student Name", value=student_data['Name'])
                        new_standard = st.number_input("Standard", value=int(student_data['Standard']), min_value=1, max_value=12)
                    with col2:
                        new_blood_group = st.selectbox("Blood Group", ["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"], index=["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"].index(student_data['Blood_Group']))
                        new_age = st.number_input("Age", value=int(student_data['Age']), min_value=3, max_value=18)
                    
                    new_address = st.text_area("Address", value=student_data['Address'])
                    new_aadhar = st.text_input("Aadhar Number", value=student_data['Aadhar_Details'])
                    
                    submitted = st.form_submit_button("Update Student")
                    
                    if submitted:
                        students_df.loc[students_df['Name'] == selected_student, 'Name'] = new_name
                        students_df.loc[students_df['Name'] == new_name, 'Standard'] = new_standard
                        students_df.loc[students_df['Name'] == new_name, 'Blood_Group'] = new_blood_group
                        students_df.loc[students_df['Name'] == new_name, 'Age'] = new_age
                        students_df.loc[students_df['Name'] == new_name, 'Address'] = new_address
                        students_df.loc[students_df['Name'] == new_name, 'Aadhar_Details'] = new_aadhar
                        save_to_excel(students_df, 'students.xlsx', 'Students')
                        st.success("✅ Student updated successfully!")
            else:
                st.info("No students found!")
        
        elif operations == "🗑️ Delete Student":
            st.markdown("### 🗑️ Delete Student")
            students_df = pd.read_excel('students.xlsx')
            
            if len(students_df) > 0:
                student_names = students_df['Name'].tolist()
                selected_student = st.selectbox("Select Student to Delete", student_names)
                
                if st.button("Delete Student", type="secondary"):
                    students_df = students_df[students_df['Name'] != selected_student]
                    save_to_excel(students_df, 'students.xlsx', 'Students')
                    st.success(f"✅ Student {selected_student} deleted successfully!")
            else:
                st.info("No students found!")
        
        elif operations == "📥 Import from Excel":
            st.markdown("### 📥 Import Students from Excel")
            uploaded_file = st.file_uploader("Upload Excel file", type=['xlsx'])
            
            if uploaded_file:
                try:
                    imported_df = pd.read_excel(uploaded_file)
                    st.markdown("### Preview of data to import:")
                    st.dataframe(imported_df, use_container_width=True)
                    
                    if st.button("Import Students"):
                        students_df = pd.read_excel('students.xlsx')
                        
                        # Add Student IDs if not present
                        if 'Student_ID' not in imported_df.columns:
                            start_id = get_next_student_id()
                            imported_df.insert(0, 'Student_ID', range(start_id, start_id + len(imported_df)))
                        
                        students_df = pd.concat([students_df, imported_df], ignore_index=True)
                        save_to_excel(students_df, 'students.xlsx', 'Students')
                        st.success(f"✅ {len(imported_df)} students imported successfully!")
                
                except Exception as e:
                    st.error(f"❌ Error importing file: {str(e)}")

if __name__ == "__main__":
    main()
