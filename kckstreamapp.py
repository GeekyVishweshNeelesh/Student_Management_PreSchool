import streamlit as st
import pandas as pd
import os
from datetime import datetime
import re

# Page configuration
st.set_page_config(
    page_title="Student Management System",
    page_icon="🎓",
    layout="wide"
)

# Excel file path
EXCEL_FILE = "students_data.xlsx"

# Standard options with sections
STANDARDS = [
    "Playground - Section A", "Playground - Section B",
    "Nursery - Section A", "Nursery - Section B",
    "Jr.KG - Section A", "Jr.KG - Section B",
    "Sr.KG - Section A", "Sr.KG - Section B"
]

# Age options (2 to 10)
AGE_OPTIONS = [2, 3, 4, 5, 6, 7, 8, 9, 10]

# Initialize Excel file if it doesn't exist
def initialize_excel():
    if not os.path.exists(EXCEL_FILE):
        df = pd.DataFrame(columns=[
            'Student_ID', 'Name', 'Standard', 'Blood_Group',
            'Address', 'Aadhar_Details', 'Age'
        ])
        df.to_excel(EXCEL_FILE, index=False)
        return df
    else:
        return pd.read_excel(EXCEL_FILE)

# Load data from Excel
def load_data():
    try:
        df = pd.read_excel(EXCEL_FILE)
        if df.empty:
            df = pd.DataFrame(columns=[
                'Student_ID', 'Name', 'Standard', 'Blood_Group',
                'Address', 'Aadhar_Details', 'Age'
            ])
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame(columns=[
            'Student_ID', 'Name', 'Standard', 'Blood_Group',
            'Address', 'Aadhar_Details', 'Age'
        ])

# Save data to Excel
def save_data(df):
    try:
        df.to_excel(EXCEL_FILE, index=False)
        return True
    except Exception as e:
        st.error(f"Error saving data: {e}")
        return False

# Generate unique student ID
def generate_student_id(df):
    if df.empty:
        return "STU001"
    else:
        last_id = df['Student_ID'].max()
        num = int(last_id[3:]) + 1
        return f"STU{num:03d}"

# Validate Aadhar number
def validate_aadhar(aadhar):
    pattern = r'^\d{12}$'
    return bool(re.match(pattern, aadhar.replace(" ", "")))

# Main app
def main():
    st.title("🎓 Student Management System")
    st.markdown("---")

    # Initialize Excel file
    initialize_excel()

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
    menu = st.sidebar.radio(
        "Select Operation:",
        ["📊 View Students", "➕ Add Student", "✏️ Update Student", "🗑️ Delete Student", "📥 Import from Excel", "📈 Analytics"]
    )

    # Load data
    df = load_data()

    # VIEW STUDENTS
    if menu == "📊 View Students":
        st.header("📊 All Students")

        if df.empty:
            st.info("No students in the database. Add students to get started!")
        else:
            # Search functionality
            col1, col2 = st.columns([2, 1])
            with col1:
                search_term = st.text_input("🔍 Search by Name or Student ID:", "")
            with col2:
                filter_standard = st.selectbox("Filter by Standard:", ["All"] + sorted(df['Standard'].unique().tolist()))

            # Filter data
            filtered_df = df.copy()
            if search_term:
                filtered_df = filtered_df[
                    filtered_df['Name'].str.contains(search_term, case=False, na=False) |
                    filtered_df['Student_ID'].str.contains(search_term, case=False, na=False)
                ]
            if filter_standard != "All":
                filtered_df = filtered_df[filtered_df['Standard'] == filter_standard]

            st.dataframe(filtered_df, use_container_width=True, height=400)
            st.info(f"📊 Total Students: {len(filtered_df)}")

            # Export to Excel
            if st.button("💾 Export Current View to Excel"):
                export_file = f"students_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                filtered_df.to_excel(export_file, index=False)
                st.success(f"✅ Data exported to {export_file}")

    # ADD STUDENT
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
                # Validation
                if not name or standard == "Select" or blood_group == "Select" or age == "Select" or not address or not aadhar:
                    st.error("❌ Please fill all required fields!")
                elif not validate_aadhar(aadhar):
                    st.error("❌ Invalid Aadhar number! Must be 12 digits.")
                else:
                    # Add student
                    new_id = generate_student_id(df)
                    new_student = pd.DataFrame({
                        'Student_ID': [new_id],
                        'Name': [name],
                        'Standard': [standard],
                        'Blood_Group': [blood_group],
                        'Address': [address],
                        'Aadhar_Details': [aadhar],
                        'Age': [age]
                    })

                    df = pd.concat([df, new_student], ignore_index=True)

                    if save_data(df):
                        st.success(f"✅ Student added successfully! Student ID: {new_id}")
                        st.balloons()
                    else:
                        st.error("❌ Failed to save student data!")

    # UPDATE STUDENT
    elif menu == "✏️ Update Student":
        st.header("✏️ Update Student Information")

        if df.empty:
            st.warning("No students available to update!")
        else:
            student_id = st.selectbox("Select Student ID:", df['Student_ID'].tolist())

            if student_id:
                student_data = df[df['Student_ID'] == student_id].iloc[0]

                with st.form("update_student_form"):
                    col1, col2 = st.columns(2)

                    with col1:
                        name = st.text_input("Name *", value=student_data['Name'])

                        # Get index for standard
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
                        # Get index for age
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
                            df.loc[df['Student_ID'] == student_id, 'Name'] = name
                            df.loc[df['Student_ID'] == student_id, 'Standard'] = standard
                            df.loc[df['Student_ID'] == student_id, 'Blood_Group'] = blood_group
                            df.loc[df['Student_ID'] == student_id, 'Address'] = address
                            df.loc[df['Student_ID'] == student_id, 'Aadhar_Details'] = aadhar
                            df.loc[df['Student_ID'] == student_id, 'Age'] = age

                            if save_data(df):
                                st.success("✅ Student updated successfully!")
                            else:
                                st.error("❌ Failed to update student data!")

    # DELETE STUDENT
    elif menu == "🗑️ Delete Student":
        st.header("🗑️ Delete Student")

        if df.empty:
            st.warning("No students available to delete!")
        else:
            student_id = st.selectbox("Select Student ID to Delete:", df['Student_ID'].tolist())

            if student_id:
                student_data = df[df['Student_ID'] == student_id].iloc[0]

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

                col1, col2, col3 = st.columns([1, 1, 2])
                with col1:
                    if st.button("🗑️ Confirm Delete", type="primary"):
                        df = df[df['Student_ID'] != student_id]
                        if save_data(df):
                            st.success("✅ Student deleted successfully!")
                            st.rerun()
                        else:
                            st.error("❌ Failed to delete student!")

    # IMPORT FROM EXCEL
    elif menu == "📥 Import from Excel":
        st.header("📥 Import Students from Excel")

        st.info("📋 **Excel File Requirements:**\n"
                "- Must have columns: Name, Standard, Blood_Group, Address, Aadhar_Details, Age\n"
                "- Standard must be one of: Playground/Nursery/Jr.KG/Sr.KG - Section A/B\n"
                "- Blood Group: A+, A-, B+, B-, O+, O-, AB+, AB-\n"
                "- Age: 2-10\n"
                "- Aadhar: 12 digits")

        # Download template
        st.subheader("📥 Step 1: Download Template")

        # Create template dataframe with sample data
        template_df = pd.DataFrame({
            'Name': ['Sample Student'],
            'Standard': ['Playground - Section A'],
            'Blood_Group': ['A+'],
            'Address': ['Sample Address'],
            'Aadhar_Details': ['123456789012'],
            'Age': [5]
        })

        # Convert to Excel in memory
        from io import BytesIO
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

        # File uploader
        uploaded_file = st.file_uploader("Choose an Excel file", type=['xlsx', 'xls'])

        if uploaded_file is not None:
            try:
                # Read uploaded file
                import_df = pd.read_excel(uploaded_file)

                st.subheader("📊 Preview of Uploaded Data")
                st.dataframe(import_df.head(10), use_container_width=True)
                st.info(f"Total rows in file: {len(import_df)}")

                # Validation
                required_columns = ['Name', 'Standard', 'Blood_Group', 'Address', 'Aadhar_Details', 'Age']
                missing_columns = [col for col in required_columns if col not in import_df.columns]

                if missing_columns:
                    st.error(f"❌ Missing required columns: {', '.join(missing_columns)}")
                else:
                    # Validate data
                    valid_rows = []
                    invalid_rows = []

                    for idx, row in import_df.iterrows():
                        errors = []

                        # Check required fields
                        if pd.isna(row['Name']) or str(row['Name']).strip() == '':
                            errors.append("Name is empty")

                        # Validate Standard
                        if row['Standard'] not in STANDARDS:
                            errors.append(f"Invalid Standard: {row['Standard']}")

                        # Validate Blood Group
                        valid_blood_groups = ["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"]
                        if row['Blood_Group'] not in valid_blood_groups:
                            errors.append(f"Invalid Blood Group: {row['Blood_Group']}")

                        # Validate Age
                        try:
                            age = int(row['Age'])
                            if age not in AGE_OPTIONS:
                                errors.append(f"Age must be between 2-10, got: {age}")
                        except:
                            errors.append(f"Invalid Age: {row['Age']}")

                        # Validate Aadhar
                        if not validate_aadhar(str(row['Aadhar_Details'])):
                            errors.append("Invalid Aadhar (must be 12 digits)")

                        if errors:
                            invalid_rows.append({'Row': idx + 2, 'Errors': ', '.join(errors)})
                        else:
                            valid_rows.append(row)

                    # Display validation results
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("✅ Valid Rows", len(valid_rows))
                    with col2:
                        st.metric("❌ Invalid Rows", len(invalid_rows))

                    if invalid_rows:
                        st.warning("⚠️ Some rows have errors:")
                        error_df = pd.DataFrame(invalid_rows)
                        st.dataframe(error_df, use_container_width=True)

                    # Import options
                    if valid_rows:
                        st.markdown("---")
                        st.subheader("Import Options")

                        import_mode = st.radio(
                            "Choose import mode:",
                            ["Append to existing data", "Replace all existing data"]
                        )

                        skip_duplicates = st.checkbox("Skip duplicate Aadhar numbers", value=True)

                        if st.button("📥 Import Students", type="primary"):
                            # Prepare data for import
                            valid_df = pd.DataFrame(valid_rows)

                            # Check for duplicates if option is selected
                            if skip_duplicates and not df.empty:
                                existing_aadhars = set(df['Aadhar_Details'].astype(str))
                                valid_df = valid_df[~valid_df['Aadhar_Details'].astype(str).isin(existing_aadhars)]
                                st.info(f"📊 After removing duplicates: {len(valid_df)} students to import")

                            if len(valid_df) > 0:
                                # Generate Student IDs
                                new_students = []
                                for _, row in valid_df.iterrows():
                                    if import_mode == "Append to existing data":
                                        new_id = generate_student_id(df)
                                        df = pd.concat([df, pd.DataFrame([{'Student_ID': new_id}])], ignore_index=True)
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

                                # Create new dataframe
                                new_df = pd.DataFrame(new_students)

                                # Apply import mode
                                if import_mode == "Replace all existing data":
                                    final_df = new_df
                                else:
                                    final_df = pd.concat([df, new_df], ignore_index=True)
                                    # Remove the temporary rows we added for ID generation
                                    final_df = final_df[final_df['Name'].notna()]

                                # Save to Excel
                                if save_data(final_df):
                                    st.success(f"✅ Successfully imported {len(new_students)} students!")
                                    st.balloons()
                                    st.info("Please refresh the page or go to 'View Students' to see the imported data.")
                                else:
                                    st.error("❌ Failed to save imported data!")
                            else:
                                st.warning("⚠️ No valid students to import after filtering!")

            except Exception as e:
                st.error(f"❌ Error reading file: {str(e)}")
                st.info("Please make sure the file is a valid Excel file (.xlsx or .xls)")

    # ANALYTICS
    elif menu == "📈 Analytics":
        st.header("📈 Student Analytics")

        if df.empty:
            st.info("No data available for analytics!")
        else:
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Total Students", len(df))
            with col2:
                st.metric("Total Standards", df['Standard'].nunique())
            with col3:
                avg_age = df['Age'].astype(float).mean()
                st.metric("Average Age", f"{avg_age:.1f}")
            with col4:
                most_common_bg = df['Blood_Group'].mode()[0]
                st.metric("Most Common Blood Group", most_common_bg)

            st.markdown("---")

            col1, col2 = st.columns(2)

            with col1:
                st.subheader("Students by Standard")
                standard_counts = df['Standard'].value_counts().sort_index()
                st.bar_chart(standard_counts)

            with col2:
                st.subheader("Students by Blood Group")
                blood_group_counts = df['Blood_Group'].value_counts()
                st.bar_chart(blood_group_counts)

            st.markdown("---")
            st.subheader("Age Distribution")
            age_counts = df['Age'].astype(int).value_counts().sort_index()
            st.line_chart(age_counts)

if __name__ == "__main__":
    main()
