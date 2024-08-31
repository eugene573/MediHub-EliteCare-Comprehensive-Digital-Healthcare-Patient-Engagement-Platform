import os
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from werkzeug.exceptions import BadRequestKeyError
from datetime import datetime
from werkzeug.utils import secure_filename

# Set up the upload folder and allowed extensions
UPLOAD_FOLDER = 'static/uploads/certifications'  # Ensure this folder exists or create it
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'jpg', 'png'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a random secret key for security

# Configure upload folder
UPLOAD_FOLDER = 'static/uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Dummy data for Admin
admin = {'username': 'admin', 'password': '9999', 'email': 'admin@example.com', 'role': 'Admin', 'contactNumber': '012-2358761'}

# Dummy data for patients
patients = [
    {'id': 1, 'username': 'alice', 'password': '1234', 'email': 'alice@example.com', 'contactNumber': '016-7165348', 'role': 'Patient', 'address': '13th Street. 47 W 13th St, New York, NY 10011, USA'},
    {'id': 2, 'username': 'bob', 'password': '1234', 'email': 'bob@example.com', 'contactNumber': '012-2894590', 'role':'Patient', 'address': 'XXX'}
]

# Dummy data for nurses
nurses = [
    {'id': 1, 'username': 'joy', 'password': '3456', 'role': 'Nurse', 'email': 'joy@example.com', 'contactNumber': '016-7234429', 'specialization': 'Pediatrics', 'approved': True},
    {'id': 2, 'username': 'kate', 'password': '3456', 'role': 'Nurse', 'email': 'kate@example.com', 'contactNumber': '012-6234675', 'specialization': 'General', 'approved': True}
]

# Dummy data for doctors
doctors = [
    {'id': 1, 'username': 'john', 'password': '2345', 'role': 'Doctor', 'email': 'john@example.com', 'contactNumber': '018-4987676', 'specialization': 'Cardiology', 'approved': True},
    {'id': 2, 'username': 'smith', 'password': '2345', 'role': 'Doctor', 'email': 'smith@example.com', 'contactNumber': '016-1652679', 'specialization': 'Dermatology', 'approved': True},
    {'id': 3, 'username': 'jim', 'password': '2345', 'role': 'Doctor', 'email': 'jim@example.com', 'specialization': 'Dermatology', 'contactNumber': '012-1322428', 'approved': True}
]

# Dummy data for appointments
appointments = [
    {'id': 1, 'patient_id': 1, 'doctor_id': 1, 'date': '2024-08-12', 'time': '10:00', 'type': 'telemedicine'},
    {'id': 2, 'patient_id': 1, 'doctor_id': 2, 'date': '2024-10-01', 'time': '11:00', 'type': 'telemedicine'},
    {'id': 3, 'patient_id': 2, 'doctor_id': 2, 'date': '2024-08-25', 'time': '12:00', 'type': 'telemedicine'}
]

# Dummy data for prescriptions
prescriptions = [
    {
        "id": 1,
        "patient_id": "P001",
        "patient_name": "John Doe",
        "medication": "Lisinopril",
        "dosage": "10 mg",
        "instructions": "Take once daily with food",
        "date": "2024-08-01"
    },
    {
        "id": 2,
        "patient_id": "P002",
        "patient_name": "Jane Smith",
        "medication": "Metformin",
        "dosage": "500 mg",
        "instructions": "Take twice daily with meals",
        "date": "2024-08-05"
    },
    {
        "id": 3,
        "patient_id": "P003",
        "patient_name": "Alice Johnson",
        "medication": "Atorvastatin",
        "dosage": "20 mg",
        "instructions": "Take once daily in the evening",
        "date": "2024-08-10"
    },
    {
        "id": 4,
        "patient_id": "P004",
        "patient_name": "Bob Brown",
        "medication": "Amlodipine",
        "dosage": "5 mg",
        "instructions": "Take once daily in the morning",
        "date": "2024-08-15"
    },
    {
        "id": 5,
        "patient_id": "P005",
        "patient_name": "Emily Davis",
        "medication": "Omeprazole",
        "dosage": "20 mg",
        "instructions": "Take once daily before breakfast",
        "date": "2024-08-20"
    }
]

# Dummy data for pending approvals
pending_approvals = [
    {'id': 1, 'username': 'Wee', 'password': '2345', 'role': 'Doctor', 'email': 'wee@example.com', 'specialization': 'Dermatology', 'contactNumber': '012-1322428'},
    {'id': 2, 'username': 'KE', 'password': '3456', 'role': 'Nurse', 'email': 'ke@example.com', 'contactNumber': '012-6232333', 'specialization': 'General'}

]

# Dummy data for medication stock
medications = [
    {
        'id': 1,
        'medication_name': 'Paracetamol',
        'description': 'Used for pain relief and fever reduction.',
        'quantity': 100,
        'price': 0.10,  # Price per unit
        'expiry_date': '2025-12-31',
        'supplier': 'PharmaCorp',
        'image_url': 'https://guardian.com.my/media/catalog/product/1/2/121115012_axcel_pcm_500mg_tab_10sx10.jpg?auto=webp&format=pjpg&width=640&height=800&fit=cover'
    },
    {
        'id': 2,
        'medication_name': 'Amoxicillin',
        'description': 'An antibiotic used to treat various infections.',
        'quantity': 200,
        'price': 0.50,  # Price per unit
        'expiry_date': '2024-08-15',
        'supplier': 'MedSupply Co.',
        'image_url': 'https://5.imimg.com/data5/ANDROID/Default/2023/4/302037696/HU/JI/VN/116627000/product-jpeg-500x500.jpg'
    },
    {
        'id': 3,
        'medication_name': 'Ibuprofen',
        'description': 'Nonsteroidal anti-inflammatory drug used for pain, fever, and inflammation.',
        'quantity': 150,
        'price': 0.20,  # Price per unit
        'expiry_date': '2026-03-21',
        'supplier': 'HealthPharma',
        'image_url': 'https://5.imimg.com/data5/SELLER/Default/2023/9/344827499/TG/YT/FY/192270567/ibuprofen-tablet-400mg.png'
    },
    {
        'id': 4,
        'medication_name': 'Ciprofloxacin',
        'description': 'Antibiotic used to treat a variety of bacterial infections.',
        'quantity': 75,
        'price': 1.00,  # Price per unit
        'expiry_date': '2023-11-30',
        'supplier': 'Global Meds Inc.',
        'image_url': 'https://cdn.shopify.com/s/files/1/1290/8299/products/Ciprofloxacin500mgboxcopy.png?v=1603264196'
    },
    {
        'id': 5,
        'medication_name': 'Lisinopril',
        'description': 'Medication used to treat high blood pressure and heart failure.',
        'quantity': 120,
        'price': 0.15,  # Price per unit
        'expiry_date': '2027-07-12',
        'supplier': 'CardioMeds',
        'image_url': 'https://5.imimg.com/data5/SELLER/Default/2023/1/JR/YJ/LF/29824675/lisinopril-20-mg-tablet.jpg'
    }
]

# ------------------------- Custom filter to format time ------------------------------------------------------------
@app.template_filter('format_time')
def format_time(value):
    try:
        return datetime.strptime(value, '%H:%M').strftime('%I:%M %p')
    except ValueError:
        return value
# -----------------------------------------------------------------------------------------------------

# ----------------------------- Home Page -------------------------------------------------------------
@app.route('/')
def index():
    username = session.get('username')
    role = session.get('role')  # Ensure role is stored in session or retrieved from the database
    return render_template('index.html', username=username, role=role)

# -------------------------- Auth ---------------------------------------------------------------------
# Register Function
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            username = request.form.get('username')
            contactNumber = request.form.get('contactNumber')
            password = request.form.get('password')
            email = request.form.get('email')
            role = request.form.get('role')

            # Check if any field is missing
            if not all([username, password, email, role, contactNumber]):
                return render_template('Auth/register.html', message="All fields are required.", error=True)

            # Validate role
            if role not in ['Patient', 'Doctor', 'Nurse']:
                return render_template('Auth/register.html', message="Invalid role selected.", error=True)

            # Create new user
            new_user = {
                'id': len(patients) + len(doctors) + len(pending_approvals) + 1,
                'username': username,
                'password': password,
                'email': email,
                'contactNumber': contactNumber,
                'role': role,
                'approved': False  # Set approval status to False initially
            }

            # Handle user roles
            if role == 'Patient':
                patients.append(new_user)
                session['username'] = username
                session['role'] = 'patient'
                return render_template('Patient/patient_register_success.html')
            elif role in ['Doctor', 'Nurse']:
                 return render_template('Auth/register_success.html', message="Your account needs to be approved by an admin.")
        except BadRequestKeyError:
            return render_template('Auth/register.html', message="Bad request. Please try again.", error=True)
    
    return render_template('Auth/register.html')

@app.route('/patient_register_success')
def patient_register_success():
    return render_template('Patient/patient_register_success.html')

# Login Function
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            username = request.form.get('username')
            password = request.form.get('password')
            remember_me = request.form.get('remember_me')  # Get remember me checkbox value

            if not username or not password:
                return render_template('Auth/login.html', message="Username and password are required.", error=True)

            # Check if the user is an admin
            if username == admin['username'] and password == admin['password']:
                session['username'] = username
                session['role'] = 'admin'
                if remember_me:
                    session.permanent = True
                return redirect(url_for('admin_dashboard'))

            # Check if the user is a doctor or nurse
            for user in doctors + nurses:
                if username == user['username'] and password == user['password']:
                    if user.get('approved'):
                        session['username'] = username
                        session['role'] = user['role'].lower()
                        if remember_me:
                            session.permanent = True
                        return redirect(url_for('index'))
                    else:
                        return render_template('Auth/login.html', message="Your account is awaiting admin approval.", error=True)

            # Check if the user is a patient
            for patient in patients:
                if username == patient['username'] and password == patient['password']:
                    session['id'] = patient['id']
                    session['username'] = username
                    session['role'] = 'patient'
                    if remember_me:
                        session.permanent = True
                    return redirect(url_for('index'))

            # Failed login
            return render_template('login.html', message="Invalid username or password.", error=True)
        except BadRequestKeyError:
            return render_template('login.html', message="Bad request. Please try again.", error=True)

    return render_template('Auth/login.html')

# Logout Function
@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('username', None)
    session.pop('role', None)
    return redirect(url_for('login'))

# Forgot Password
@app.route('/forgot_password')
def forgot_password():
    return render_template('Auth/forgot_password.html')
# -------------------------------------------------------------------------------------------------------

# ---------------------- Profile Settings ---------------------------------------------------------------
# View Profile
@app.route('/profile')
def view_profile():
    username = session.get('username')
    role = session.get('role')

    # Check if user is logged in
    if not username:
        return redirect(url_for('login'))

    # Fetch user based on role
    user = None
    if role == 'admin' and username == admin.get('username'):
        user = admin
    elif role == 'doctor':
        user = next((doc for doc in doctors if doc['username'] == username), None)
    elif role == 'nurse':
        user = next((nurse for nurse in nurses if nurse['username'] == username), None)
    elif role == 'patient':
        user = next((pat for pat in patients if pat['username'] == username), None)
    else:
        return redirect(url_for('index'))

    # If no user is found, redirect to home page or show an error
    if user is None:
        return redirect(url_for('index'))

    return render_template('Profile/view_profile.html', user=user, username=username, role=role)

# Edit Profile
@app.route('/profile/edit', methods=['GET', 'POST'])
def edit_profile():
    username = session.get('username')
    role = session.get('role')

    if not username:
        return redirect(url_for('login'))

    # Retrieve the user based on role
    user = None
    if role == 'admin' and username == admin['username']:
        user = admin
    elif role == 'doctor':
        user = next((doc for doc in doctors if doc['username'] == username), None)
    elif role == 'nurse':
        user = next((nurse for nurse in nurses if nurse['username'] == username), None)
    elif role == 'patient':
        user = next((pat for pat in patients if pat['username'] == username), None)

    if not user:
        return redirect(url_for('index'))

    if request.method == 'POST':
        # Update the user's profile information
        user['username'] = request.form['username']
        user['email'] = request.form['email']
        user['contactNumber'] = request.form['contactNumber']
        user['password'] = request.form['password']  # Remember to hash the password!

        if role == 'doctor' or role == 'nurse':
            user['specialization'] = request.form['specialization']
        if role == 'patient':
            user['address'] = request.form['address']

        # Update user in their respective collection
        if role == 'admin':
            admin.update(user)
        elif role == 'doctor':
            for doctor in doctors:
                if doctor['username'] == username:
                    doctor.update(user)
                    break
        elif role == 'nurse':
            for nurse in nurses:
                if nurse['username'] == username:
                    nurse.update(user)
                    break
        elif role == 'patient':
            for patient in patients:
                if patient['username'] == username:
                    patient.update(user)
                    break

        return redirect(url_for('view_profile'))

    return render_template('Profile/edit_profile.html', user=user, username=username, role=role)
# ---------------------------------------------------------------------------------------------------

# -------------------------- Patient --------------------------------------------------------------------------
# Route for the Patient Dashboard
@app.route('/patient')
def patient_dashboard():
    username = session.get('username')
    role = session.get('role')  # Ensure role is stored in session or retrieved from the database
    if role != 'patient':
        return redirect(url_for('index'))  # Redirect to the index page if not logged in as patient
    return render_template('index.html', username=username, appointments=appointments)

# Patient Book Telemedicine Appointment
@app.route('/patient/telemedicine', methods=['GET', 'POST'])
def book_telemedicine_appointment():
    if 'id' not in session:
        return redirect(url_for('login'))
    
    username = session.get('username')
    role = session.get('role')
    current_date = datetime.now().strftime('%Y-%m-%d')  # Get current date in YYYY-MM-DD format
    
    if request.method == 'POST':
        patient_id = session.get('id')
        if not patient_id:
            return redirect(url_for('login'))
        
        # Validate form data here
        try:
            new_appointment = {
                'id': len(appointments) + 1,
                'patient_id': patient_id,
                'doctor_id': int(request.form['doctor']),
                'date': request.form['date'],
                'time': request.form['time'],
                'type': 'telemedicine'
            }
            appointments.append(new_appointment)
            
            patient_appointments = [app for app in appointments if app['patient_id'] == patient_id]
            
            # Set success message
             # Flash success message
            flash("Appointment has been made successfully!", "success")
            return render_template('Patient/patient_appointments.html',
                                  username=username,
                                  role=role,
                                  appointments=patient_appointments,
                                  current_date=current_date,
                                  doctors=doctors)  

        except Exception as e:
            # Log the error (you can use logging here)
            print(f"Error booking appointment: {e}")
            return render_template('Patient/patient_appointments.html',
                                  username=username,
                                  role=role,
                                  appointments=patient_appointments,
                                  current_date=current_date,
                                  doctors=doctors,
                                  success_message="Failed to book the appointment. Please try again.")  # Pass failure message
    
    return render_template('Patient/telemedicine.html', 
                          doctors=doctors, 
                          username=username, 
                          role=role, 
                          current_date=current_date)  # Ensure doctors is included here

# Patient Book Home Visit 
@app.route('/patient/home_visit', methods=['GET', 'POST'])
def book_home_visit_appointment():
    if 'id' not in session:
        return redirect(url_for('login'))
    
    username = session.get('username')
    role = session.get('role')
    current_date = datetime.now().strftime('%Y-%m-%d')
    
    if request.method == 'POST':
        patient_id = session.get('id')
        if not patient_id:
            return redirect(url_for('login'))
        
        try:
            selected_role = request.form.get('role')
            selected_id = int(request.form.get('person'))
            appointment_date = request.form.get('date')
            appointment_time = request.form.get('time')

            if not selected_role or not selected_id or not appointment_date or not appointment_time:
                error_message = "All fields are required."
                return render_template('Patient/home_visit.html',
                                      username=username,
                                      role=role,
                                      current_date=current_date,
                                      doctors=doctors,
                                      nurses=nurses,
                                      error_message=error_message)
            
            new_appointment = {
                'id': len(appointments) + 1,
                'patient_id': patient_id,
                'person_id': selected_id,
                'role': selected_role,
                'date': appointment_date,
                'time': appointment_time,
                'type': 'home visit',
                'doctor_id': selected_id if selected_role == 'doctor' else None,  # Add doctor_id if applicable
                'nurse_id': selected_id if selected_role == 'nurse' else None    # Add nurse_id if applicable
            }
            appointments.append(new_appointment)
                    
                    
            # Flash success message
            flash("Appointment has been made successfully!", "success")
            return redirect(url_for('patient_appointments'))

        except Exception as e:
            print(f"Error booking home visit appointment: {e}")
            return render_template('Patient/home_visit.html',
                                  username=username,
                                  role=role,
                                  current_date=current_date,
                                  doctors=doctors,
                                  nurses=nurses,
                                  error_message="Failed to book the appointment. Please try again.")
    
    return render_template('Patient/home_visit.html',
                          username=username,
                          role=role,
                          current_date=current_date,
                          doctors=doctors,
                          nurses=nurses)

# Patient View Appointment
@app.route('/patient/appointments')
def patient_appointments():
    patient_id = session.get('id')
    
    # Fetch appointments from the database
    patient_appointments = [app for app in appointments if app['patient_id'] == patient_id]

    # Sort appointments by date and time
    patient_appointments.sort(key=lambda x: (datetime.strptime(x['date'], '%Y-%m-%d'), x['time']))
    
    # Fetch doctors and nurses data from the database
    doctors = get_doctors()  # Replace with actual data retrieval function
    nurses = get_nurses()    # Replace with actual data retrieval function

    current_date = datetime.now().strftime('%Y-%m-%d')
    username = session.get('username')
    role = session.get('role')

    return render_template(
        'Patient/patient_appointments.html',
        username=username,
        role=role,
        appointments=patient_appointments,
        current_date=current_date,
        doctors=doctors,
        nurses=nurses
    )

# Patient View Prescription
@app.route('/patient_view_prescription')
def patient_view_prescription():
    username = session.get('username')
    role = session.get('role')

    if role not in ['patient']:
        return redirect(url_for('index'))  # Redirect if not a doctor or nurse

    user_prescriptions = [pres for pres in prescriptions]
    return render_template('Patient/patient_prescription.html', prescriptions=user_prescriptions,role=role)
# -------------------------------------------------------------------------------------------------------------

# ----------------------------------- Get Doctors & Nurses Information ----------------------------------------
def get_doctors():
    return [
        {'id': 1, 'name': 'John', 'username': 'john', 'password': '2345', 'role': 'Doctor', 'email': 'john@example.com', 'contact number': '018-4987676', 'specialization': 'Cardiology', 'approved': True},
        {'id': 2, 'name': 'Smith', 'username': 'smith', 'password': '2345', 'role': 'Doctor', 'email': 'smith@example.com', 'contact number': '016-1652679', 'specialization': 'Dermatology', 'approved': True},
        {'id': 3, 'name': 'Jim', 'username': 'jim', 'password': '2345', 'role': 'Doctor', 'email': 'jim@example.com', 'specialization': 'Dermatology', 'contact number': '012-1322428'}
    ]

def get_nurses():
    return [
    {'id': 1, 'username': 'joy', 'password': '3456', 'role': 'Nurse', 'email': 'joy@example.com', 'contactNumber': '016-7234429', 'specialization': 'Pediatrics', 'approved': True},
    {'id': 2, 'username': 'kate', 'password': '3456', 'role': 'Nurse', 'email': 'kate@example.com', 'contactNumber': '012-6234675', 'specialization': 'General', 'approved': True}
]
# -----------------------------------------------------------------------------------------------------------------

# ---------------------------------- Prescription -----------------------------------------------------------------
# Doctor & Nurse Write Prescription
@app.route('/write_prescription', methods=['GET', 'POST'])
def write_prescription():
    username = session.get('username')
    role = session.get('role')

    if not role or role not in ['doctor', 'nurse']:
        return redirect(url_for('index'))  # Redirect if not a doctor or nurse

    if request.method == 'POST':
        patient_id = int(request.form['patient_id'])
        medication = request.form['medication']
        dosage = request.form['dosage']
        instructions = request.form['instructions']

        new_prescription = {
            'id': len(prescriptions) + 1,
            'author_username': username,
            'author_role': role,
            'patient_id': patient_id,
            'medication': medication,
            'dosage': dosage,
            'instructions': instructions,
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        prescriptions.append(new_prescription)
        return redirect(url_for('view_prescriptions'))

    patient_list = [pat for pat in patients]
    return render_template('Prescription/write_prescription.html', patients=patient_list, role=role)

# Doctor & Nurse View Prescription
@app.route('/view_prescriptions')
def view_prescriptions():
    username = session.get('username')
    role = session.get('role')

    if role not in ['doctor', 'nurse']:
        return redirect(url_for('index'))  # Redirect if not a doctor or nurse

    user_prescriptions = [pres for pres in prescriptions]
    return render_template('Prescription/view_prescriptions.html', prescriptions=user_prescriptions,role=role)

# Prescription Page
@app.route('/prescription',methods=['GET'])
def prescription_options():
    username = session.get('username')
    role = session.get('role')
    
    if not username:
        return redirect(url_for('login'))
    
    return render_template('Prescription/prescription.html', username=username, role=role)
# -----------------------------------------------------------------------------------------------------------------

# ----------------------------- Doctor -----------------------------------------------------------------------
# Route for the doctor dashboard
@app.route('/doctor')
def doctor_dashboard():
    username = session.get('username')
    role = session.get('role')  # Ensure role is stored in session or retrieved from the database
    if role != 'doctor':
        return redirect(url_for('index'))  # Redirect to the index page if not logged in as doctor
    return render_template('index.html', username=username, appointments=appointments)

# Doctor MY Appointment
@app.route('/doctor/appointments')
def doctor_appointments():
    doctor_id = session.get('id')
    doctor_appointments = [app for app in appointments if app.get('doctor_id') == doctor_id]
    username = session.get('username')
    role = session.get('role')
    return render_template('Doctor/doctor_appointments.html', username=username, role=role, appointments=doctor_appointments)
# -------------------------------------------------------------------------------------------------------------------------

# --------------------------------- Nurse --------------------------------------------------------------------------
# Nurse MY Appointment
@app.route('/nurse/appointments')
def nurse_appointments():
    nurse_id = session.get('id')
    nurse_appointments = [app for app in appointments if app.get('nurse_id') == nurse_id]
    username = session.get('username')
    role = session.get('role')
    return render_template('Nurse/nurse_appointments.html', username=username, role=role, appointments=nurse_appointments)
# -------------------------------------------------------------------------------------------------------------------------

# ----------------------------- Admin ------------------------------------------------------------------------------
# Route for the admin dashboard
@app.route('/admin/dashboard')
def admin_dashboard():
    username = session.get('username')
    role = session.get('role')  # Ensure role is stored in session or retrieved from the database
    if role != 'admin':
        return redirect(url_for('index'))  # Redirect to the index page if not logged in as admin
    return render_template('Admin/admin_dashboard.html', username=username, doctors=doctors, nurses=nurses)

# Admin View Patients List
@app.route('/admin/view_patients', methods=['GET', 'POST'])
def admin_view_patients():
    search_query = request.args.get('search', '').lower()

    # Filter patients based on the search query
    filtered_patients = [
        patient for patient in patients 
        if search_query in patient['username'].lower() 
    ]

    return render_template('Admin/admin_view_patients.html', patients=filtered_patients)

# Admin View Patient Address
@app.route('/admin/view_address/<int:patient_id>', methods=['GET'])
def admin_view_address(patient_id):
    # Find the patient by ID
    patient = next((p for p in patients if p['id'] == patient_id), None)

    if patient:
        return jsonify(address=patient['address'])
    else:
        return jsonify(error="Patient not found"), 404

# Admin View Doctors List
@app.route('/admin/view_doctors', methods=['GET', 'POST'])
def admin_view_doctors():
    search_query = request.args.get('search', '').lower()

    # Filter patients based on the search query
    filtered_doctors = [
        doctor for doctor in doctors 
        if search_query in doctor['username'].lower() 
    ]

    role = session.get('role')
    if role != 'admin':
        return redirect(url_for('index'))  # Ensure only admins can access this page

    # Filter patients
    doctor_list = [pat for pat in doctors if pat['role'] == 'Doctor']

    return render_template('Admin/admin_view_doctors.html', doctors=filtered_doctors)

# Admin View Nurse List
@app.route('/admin/nurses')
def admin_view_nurses():
    search_query = request.args.get('search', '').lower()

    # Filter nurses based on the search query
    filtered_nurses = [
        nurse for nurse in nurses 
        if search_query in nurse['username'].lower() 
    ]

    return render_template('Admin/admin_view_nurses.html', nurses=filtered_nurses)

# Delete Patient (Admin Only)
@app.route('/admin/patients/delete/<int:patient_id>', methods=['POST'])
def admin_delete_patient(patient_id):
    global patients
    patients = [pat for pat in patients if pat['id'] != patient_id]
    return redirect(url_for('admin_view_patients'))

# Delete Doctor (Admin Only)
@app.route('/admin/doctors/delete/<int:doctor_id>', methods=['POST'])
def admin_delete_doctor(doctor_id):
    global doctors
    doctors = [doc for doc in doctors if doc['id'] != doctor_id]
    return redirect(url_for('admin_view_doctors'))

# Delete Nurse (Admin Only)
@app.route('/admin/nurses/delete/<int:nurse_id>', methods=['POST'])
def admin_delete_nurse(nurse_id):
    global nurses
    nurses = [nurse for nurse in nurses if nurse['id'] != nurse_id]
    return redirect(url_for('admin_view_nurses'))

# Admin View Pending List
@app.route('/admin/pending_approvals')
def admin_pending_approvals():
    username = session.get('username')
    role = session.get('role')

    if role != 'admin':
        return redirect(url_for('index'))

    return render_template('Admin/admin_pending_approvals.html', pending_approvals=pending_approvals)

# Admin Approve Function
@app.route('/admin/approve/<int:user_id>', methods=['POST'])
def admin_approve_user(user_id):
    global pending_approvals

    user = next((u for u in pending_approvals if u['id'] == user_id), None)
    if user:
        user['approved'] = True
        if user['role'] == 'Doctor':
            doctors.append(user)
        elif user['role'] == 'Nurse':
            nurses.append(user)
        pending_approvals = [u for u in pending_approvals if u['id'] != user_id]
    
    return redirect(url_for('admin_pending_approvals'))

# Admin Reject Function
@app.route('/admin/reject/<int:user_id>', methods=['POST'])
def admin_reject_user(user_id):
    global pending_approvals

    pending_approvals = [u for u in pending_approvals if u['id'] != user_id]
    return redirect(url_for('admin_pending_approvals'))

# Admin to View All Appointment
@app.route('/admin/appointments')
def admin_appointments():
    # Sort appointments by date and time
    appointments_sorted = sorted(appointments, key=lambda x: (datetime.strptime(x['date'], '%Y-%m-%d'), x['time']))
    username = session.get('username')
    role = session.get('role')
    return render_template('Admin/admin_appointments.html', appointments=appointments_sorted, doctors=doctors, username=username, role=role)

# Admin Medical Stock Management Function
# View Medical Stock
@app.route('/admin/medication')
def view_medication():
    for med in medications:
        try:
            # Convert price to float and format it to two decimal places
            med['price'] = "{:.2f}".format(float(med['price']))
        except (ValueError, TypeError) as e:
            print(f"Error formatting price {med['price']}: {e}")
            med['price'] = "0.00"  # Default value in case of error
    return render_template('Medication/view_stock.html', medications=medications)

# Add Medical To Stock
@app.route('/admin/medication/add', methods=['GET', 'POST'])
def add_medication():
    if request.method == 'POST':
        # Handle file upload
        file = request.files['image']
        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

        new_medication = {
            'id': len(medications) + 1,
            'medication_name': request.form['medication_name'],
            'description': request.form['description'],
            'quantity': int(request.form['quantity']),
            'price': float(request.form['price']),
            'expiry_date': request.form['expiry_date'],
            'supplier': request.form['supplier'],
            'image': filename if file else None
        }
        medications.append(new_medication)
        flash('Medication added successfully!')
        return redirect(url_for('view_medication'))
    return render_template('Medication/add_stock.html')

# Edit Medical Stock
@app.route('/admin/medication/edit/<int:id>', methods=['GET', 'POST'])
def edit_medication(id):
    medication = next((med for med in medications if med['id'] == id), None)
    if not medication:
        flash('Medication not found!')
        return redirect(url_for('view_medication'))

    if request.method == 'POST':
        # Handle file upload
        file = request.files['image']
        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            medication['image'] = filename

        medication['medication_name'] = request.form['medication_name']
        medication['description'] = request.form['description']
        medication['quantity'] = int(request.form['quantity'])
        medication['price'] = float(request.form['price']) # Price Per Unit
        medication['expiry_date'] = request.form['expiry_date']
        medication['supplier'] = request.form['supplier']
        flash('Medication updated successfully!')
        return redirect(url_for('view_medication'))

    return render_template('Medication/edit_stock.html', medication=medication)

# Delete Medical Stock
@app.route('/admin/medication/delete/<int:id>')
def delete_medication(id):
    global medications
    medications = [med for med in medications if med['id'] != id]
    flash('Medication deleted successfully!')
    return redirect(url_for('view_medication'))
# ------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':
    app.run(debug=True)