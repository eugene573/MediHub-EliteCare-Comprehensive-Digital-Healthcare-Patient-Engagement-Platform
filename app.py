import os
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from werkzeug.exceptions import BadRequestKeyError
from datetime import datetime
from werkzeug.utils import secure_filename
from flask_pymongo import PyMongo
from pymongo import MongoClient
from flask_cors import CORS

# Connect to MongoDB (use your URI here)
client = MongoClient("mongodb+srv://eugenefong2002:fong55668921@cluster0.5mjroyf.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")

# Select the database you want to work with
db = client['test']

# Collections
admin_collection = db['admins']
patients_collection = db['patients']
nurses_collection = db['nurses']
doctors_collection = db['doctors']
appointments_collection = db['appointments']
prescriptions_collection = db['prescriptions']
medications_collection = db['medications']

# Set up the upload folder and allowed extensions
UPLOAD_FOLDER = 'static/uploads'  # Ensure this folder exists or create it
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}  # Allowed file types

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a random secret key for security
app.config["MONGO_URI"] = "mongodb+srv://eugenefong2002:fong55668921@cluster0.5mjroyf.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
mongo = PyMongo(app)
# Configure upload folder
UPLOAD_FOLDER = 'static/uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    
# Dummy data for Admin
admin = {'username': 'Admin', 'password': '9999', 'email': 'admin@example.com', 'role': 'Admin', 'contactNumber': '012-2358761', 'pimage':'https://www.perfocal.com/blog/content/images/2021/01/Perfocal_17-11-2019_TYWFAQ_100_standard-3.jpg'}

# Dummy data for patients
patients = [
    {'id': 1, 'username': 'Alice', 'password': '1234', 'email': 'alice@example.com', 'contactNumber': '016-7165348', 'role': 'Patient', 'address': '13th Street. 47 W 13th St, New York, NY 10011, USA', 'pimage':'https://www.perfocal.com/blog/content/images/2021/01/Perfocal_17-11-2019_TYWFAQ_100_standard-3.jpg'},
    {'id': 2, 'username': 'Bob', 'password': '1234', 'email': 'bob@example.com', 'contactNumber': '012-2894590', 'role':'Patient', 'address': 'XXX', 'pimage':'https://plus.unsplash.com/premium_photo-1689977968861-9c91dbb16049?fm=jpg&q=60&w=3000&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8MXx8cHJvZmlsZSUyMHBpY3R1cmV8ZW58MHx8MHx8fDA%3D'},
    {'id': 3, 'username': 'Lily', 'password': '1234', 'email': 'lily@example.com', 'contactNumber': '012-2894569', 'role':'Patient', 'address': 'XXX', 'pimage':'https://www.profilebakery.com/wp-content/uploads/2023/04/AI-Profile-Picture.jpg'},
    {'id': 4, 'username': 'Ray', 'password': '1234', 'email': 'ray@example.com', 'contactNumber': '012-1127338', 'role':'Patient', 'address': 'XXX', 'pimage':'https://i.pinimg.com/474x/98/51/1e/98511ee98a1930b8938e42caf0904d2d.jpg'},
    {'id': 5, 'username': 'Cael', 'password': '1234', 'email': 'cael@example.com', 'contactNumber': '012-2891232', 'role':'Patient', 'address': 'XXX', 'pimage':'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQSoQFvYAr4KD4S-iecBnmLmPf7zuyFyHkd8w&s'}
]

# Dummy data for nurses
nurses = [
    {'id': 1, 'username': 'Joy', 'password': '3456', 'role': 'Nurse', 'email': 'joy@example.com', 'contactNumber': '016-7234429', 'specialization': 'Pediatrics', 'intro': 'Miss Joy graduated with an MBBS from Manipal Academy of Higher Education (MAHE). She is a General Practitioner with experience in treating medical conditions of any age group.', 'pimage':'https://media.istockphoto.com/id/1329569957/photo/happy-young-female-doctor-looking-at-camera.jpg?s=612x612&w=0&k=20&c=7Wq_Y2cl0T4op6Wg_3DFc-xtZfCqTTDvfaXkPGyrHDM='},
    {'id': 2, 'username': 'Kate', 'password': '3456', 'role': 'Nurse', 'email': 'kate@example.com', 'contactNumber': '012-6234675', 'specialization': 'Cardiology', 'intro': 'Miss Kate graduated with an MBBS from International Islamic University Malaysia. She has over 7 years of experience as a practicing doctor.', 'pimage':'https://media.istockphoto.com/id/1330046035/photo/headshot-portrait-of-smiling-female-doctor-in-hospital.jpg?s=612x612&w=0&k=20&c=fsNQPbmFIxoKA-PXl3G745zj7Cvr_cFIGsYknSbz_Tg='},
    {'id': 3, 'username': 'Kim', 'password': '3456', 'role': 'Nurse', 'email': 'kim@example.com', 'contactNumber': '012-3324699', 'specialization': 'Ophthalmology', 'intro': 'Miss Kim graduated with an MBBS from Jawaharlal Nehru Medical College - KLE University (Belgaum) INDIA. She has 9 years of experience as a practicing doctor.', 'pimage':'https://www.shutterstock.com/image-photo/head-shot-woman-wearing-white-600nw-1529466836.jpg'},
    {'id': 4, 'username': 'Ryan', 'password': '3456', 'role': 'Nurse', 'email': 'ryan@example.com', 'contactNumber': '012-2595432', 'specialization': 'General Practice', 'intro': 'Mr Ryan graduated with an MBBS from Jawaharlal Nehru Medical College - KLE University (Belgaum) INDIA. She has 9 years of experience as a practicing doctor.', 'pimage':'https://media.istockphoto.com/id/1468678624/photo/nurse-hospital-employee-and-portrait-of-black-man-in-a-healthcare-wellness-and-clinic-feeling.jpg?s=612x612&w=0&k=20&c=AGQPyeEitUPVm3ud_h5_yVX4NKY9mVyXbFf50ZIEtQI='},
    {'id': 5, 'username': 'Tim', 'password': '3456', 'role': 'Nurse', 'email': 'tim@example.com', 'contactNumber': '012-2595887', 'specialization': 'Dermatology', 'intro': 'Mr Tim graduated with an MBBS from Jawaharlal Nehru Medical College - KLE University (Belgaum) INDIA. She has 9 years of experience as a practicing doctor.', 'pimage':'https://img.freepik.com/free-photo/front-view-male-nurse-studio_23-2150796762.jpg?semt=ais_hybrid'},
    {'id': 6, 'username': 'Yasmin', 'password': '3456', 'role': 'Nurse', 'email': 'yasmin@example.com', 'contactNumber': '012-2441178', 'specialization': 'Family Medicine', 'intro': 'Miss Yasmin graduated with an MBBS from Jawaharlal Nehru Medical College - KLE University (Belgaum) INDIA. She has 9 years of experience as a practicing doctor.', 'pimage':'https://plus.unsplash.com/premium_photo-1682141165192-7b4678fe96c8?fm=jpg&q=60&w=3000&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8MXx8bnVyc2VzfGVufDB8fDB8fHww'},
    {'id': 7, 'username': 'Shanice', 'password': '3456', 'role': 'Nurse', 'email': 'shanice@example.com', 'contactNumber': '012-9544321', 'specialization': 'Obstetrics and Gynecology', 'intro': 'Miss Shanice graduated with an MBBS from Jawaharlal Nehru Medical College - KLE University (Belgaum) INDIA. She has 9 years of experience as a practicing doctor.', 'pimage':'https://media.istockphoto.com/id/1406698322/photo/young-female-nurse-with-folded-arms-standing-in-hospital.jpg?s=612x612&w=0&k=20&c=e9m9bHOguGXk84VrW5Kc-wPdb876ofLn_F27iRY8gGU='},
    {'id': 8, 'username': 'Corinne', 'password': '3456', 'role': 'Nurse', 'email': 'corinne@example.com', 'contactNumber': '012-1237640', 'specialization': 'Obstetrics and Gynecology', 'intro': 'Miss Corinne graduated with an MBBS from Jawaharlal Nehru Medical College - KLE University (Belgaum) INDIA. She has 9 years of experience as a practicing doctor.', 'pimage':'https://yt3.googleusercontent.com/o7Ve1CElx13g5hFN_cD-dAIKelIw2UJ4J9dcwg03PCkZQwFExLY7oNU6Vh6i_GA4MufKyYGZaA=s900-c-k-c0x00ffffff-no-rj'}
]

# Dummy data for doctors
doctors = [
    {'id': 1, 'username': 'John', 'password': '2345', 'role': 'Doctor', 'email': 'john@example.com', 'contactNumber': '018-4987676', 'specialization': 'Cardiology', 'intro': 'Dr John graduated with an MBBS from Melaka Manipal Medical College. He has over 10 years of experience as a practicing doctor and is currently running her own clinic in the heart of Kuala Lumpur.', 'pimage':'https://img.freepik.com/free-photo/doctor-offering-medical-teleconsultation_23-2149329007.jpg'},
    {'id': 2, 'username': 'Smith', 'password': '2345', 'role': 'Doctor', 'email': 'smith@example.com', 'contactNumber': '016-1652679', 'specialization': 'Orthopedics', 'intro': 'Dr Smith graduated from Universitas Padjadjaran of Indonesia in 2008, and has 12 years of experience as a practising doctor in Malaysia.', 'pimage':'https://www.smhbhopal.com/upload/doctors/1694428861.jpg'},
    {'id': 3, 'username': 'Jim', 'password': '2345', 'role': 'Doctor', 'email': 'jim@example.com', 'specialization': 'Dermatology', 'contactNumber': '012-1322428', 'intro': 'Dr Jim graduated with a Medical Degree from Crimea State University in 2010. He has over 10 years of experience as a general practitioner and provided consultation for various medical conditions.', 'pimage':'https://www.hjhospitals.org/photos/doctors/_MG_1170t.jpg'},
    {'id': 4, 'username': 'Amy', 'password': '2345', 'role': 'Doctor', 'email': 'amy@example.com', 'specialization': 'Ophthalmology', 'contactNumber': '012-1322428', 'intro': 'Dr Amy graduated with a Medical Degree from Crimea State University in 2010. He has over 10 years of experience as a general practitioner and provided consultation for various medical conditions.', 'pimage':'https://img.freepik.com/premium-photo/smiling-korean-young-female-doctor-profile-photo_1279815-42632.jpg'},
    {'id': 5, 'username': 'Chris', 'password': '2345', 'role': 'Doctor', 'email': 'chris@example.com', 'specialization': 'Neurology', 'contactNumber': '012-1322428', 'intro': 'Dr Chris graduated with a Medical Degree from Crimea State University in 2010. He has over 10 years of experience as a general practitioner and provided consultation for various medical conditions.', 'pimage':'https://images.pexels.com/photos/8460090/pexels-photo-8460090.jpeg?cs=srgb&dl=pexels-cristian-rojas-8460090.jpg&fm=jpg'},
    {'id': 6, 'username': 'Bily', 'password': '2345', 'role': 'Doctor', 'email': 'bily@example.com', 'specialization': 'Pediatrics', 'contactNumber': '012-1322428', 'intro': 'Dr Bily graduated with a Medical Degree from Crimea State University in 2010. He has over 10 years of experience as a general practitioner and provided consultation for various medical conditions.', 'pimage':'https://st4.depositphotos.com/3776273/39461/i/450/depositphotos_394613312-stock-photo-covid-19-preventing-virus-healthcare.jpg'},
    {'id': 7, 'username': 'Ariana', 'password': '2345', 'role': 'Doctor', 'email': 'ariana@example.com', 'specialization': 'Orthopedics', 'contactNumber': '012-1322428', 'intro': 'Dr Ariana graduated with a Medical Degree from Crimea State University in 2010. He has over 10 years of experience as a general practitioner and provided consultation for various medical conditions.', 'pimage':'https://plus.unsplash.com/premium_photo-1664474647299-7ef90322be6c?fm=jpg&q=60&w=3000&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8MXx8d29tZW4lMjBkb2N0b3J8ZW58MHx8MHx8fDA%3D'},
    {'id': 8, 'username': 'Estelle', 'password': '2345', 'role': 'Doctor', 'email': 'estelle@example.com', 'specialization': 'Family Medicine', 'contactNumber': '012-1322428', 'intro': 'Dr Estelle graduated with a Medical Degree from Crimea State University in 2010. He has over 10 years of experience as a general practitioner and provided consultation for various medical conditions.', 'pimage':'https://img.freepik.com/premium-photo/expert-female-doctor-clinic-environment_993044-4525.jpg'},
    {'id': 9, 'username': 'Patrick', 'password': '2345', 'role': 'Doctor', 'email': 'patrick@example.com', 'specialization': 'Obstetrics and Gynecology', 'contactNumber': '012-1763321', 'intro': 'Dr Patrick graduated with a Medical Degree from Crimea State University in 2010. He has over 10 years of experience as a general practitioner and provided consultation for various medical conditions.', 'pimage':'https://img.freepik.com/free-photo/annoyed-young-male-doctor-wearing-medical-robe-stethoscope-around-his-neck-putting-hand-belly-with-closed-eyes-isolated-white-with-copy-space_141793-76538.jpg?size=626&ext=jpg&ga=GA1.1.2008272138.1723334400&semt=ais_hybrid'},
    {'id': 10, 'username': 'Natalia', 'password': '2345', 'role': 'Doctor', 'email': 'natalia@example.com', 'specialization': 'General Practice', 'contactNumber': '012-6653199', 'intro': 'Dr Natalia graduated with a Medical Degree from Crimea State University in 2010. He has over 10 years of experience as a general practitioner and provided consultation for various medical conditions.', 'pimage':'https://images.pexels.com/photos/5215024/pexels-photo-5215024.jpeg?cs=srgb&dl=pexels-shkrabaanthony-5215024.jpg&fm=jpg'}
]

# Extracting specializations from the existing dummy data
nurse_specializations = [nurse['specialization'] for nurse in nurses]
doctor_specializations = [doctor['specialization'] for doctor in doctors]

# Creating a new dummy data set for specializations
specializations = {
    'nurses': list(set(nurse_specializations)),  # Using set to avoid duplicates
    'doctors': list(set(doctor_specializations))  # Using set to avoid duplicates
}

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

# Insert data into MongoDB collections
admin_collection.insert_one(admin)
patients_collection.insert_many(patients)
nurses_collection.insert_many(nurses)
doctors_collection.insert_many(doctors)
appointments_collection.insert_many(appointments)
prescriptions_collection.insert_many(prescriptions)
medications_collection.insert_many(medications)

print("Data inserted successfully!")

# Insert data into MongoDB collections, checking if the data already exists

# Insert admin data (only if not already present)
if admin_collection.count_documents({'email': admin['email']}) == 0:
    admin_collection.insert_one(admin)

# Insert patients data (only if not already present)
for patient in patients:
    if patients_collection.count_documents({'email': patient['email']}) == 0:
        patients_collection.insert_one(patient)

# Insert nurses data (only if not already present)
for nurse in nurses:
    if nurses_collection.count_documents({'email': nurse['email']}) == 0:
        nurses_collection.insert_one(nurse)

# Insert doctors data (only if not already present)
for doctor in doctors:
    if doctors_collection.count_documents({'email': doctor['email']}) == 0:
        doctors_collection.insert_one(doctor)

# Insert appointments data (only if not already present)
for appointment in appointments:
    if appointments_collection.count_documents({'id': appointment['id']}) == 0:
        appointments_collection.insert_one(appointment)

# Insert prescriptions data (only if not already present)
for prescription in prescriptions:
    if prescriptions_collection.count_documents({'id': prescription['id']}) == 0:
        prescriptions_collection.insert_one(prescription)

# Insert medications data (only if not already present)
for medication in medications:
    if medications_collection.count_documents({'medication_name': medication['medication_name']}) == 0:
        medications_collection.insert_one(medication)

print("Data inserted successfully without duplication!")

# ------------------------- Custom filter to format time ------------------------------------------------------------
@app.template_filter('format_time')
def format_time(value):
    try:
        return datetime.strptime(value, '%H:%M').strftime('%I:%M %p')
    except ValueError:
        return value
    
# Route to display the uploaded image
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return f"File uploaded successfully: <img src='{url_for('static', filename='uploads/' + filename)}' alt='pimage'>"
# -----------------------------------------------------------------------------------------------------

# ----------------------------- Home Page -------------------------------------------------------------
@app.route('/')
def index():
    username = session.get('username')
    role = session.get('role')  # Ensure role is stored in session or retrieved from the database
    return render_template('index.html', username=username, role=role)

@app.route('/meeting')
def meeting():
    username = session.get('username')
    role = session.get('role')  
    return render_template('meeting.html', username=username, role=role)

# MEETING
@app.route("/join", methods=["GET", "POST"])
def join():
    username = session.get('username')
    role = session.get('role')  
    if request.method == "POST":
        room_id = request.form.get("roomID")
        return redirect(f"/meeting?roomID={room_id}")
    return render_template("join.html", username=username, role=role)

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
            
            # Handle file upload
            if 'pimage' not in request.files:
                return render_template('Auth/register.html', message="Profile image is required.", error=True)
            
            file = request.files['pimage']

            # Check if any field is missing
            if not all([username, password, email, role, contactNumber]) or not file or not allowed_file(file.filename):
                return render_template('Auth/register.html', message="All fields are required and the image must be valid.", error=True)

            # Secure the filename and save the image
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            # Create new patient account
            new_user = {
                'id': len(patients) + 1,  # Adjust ID logic as per your storage mechanism
                'username': username,
                'password': password,
                'email': email,
                'contactNumber': contactNumber,
                'role': role,
                'approved': True,  # Patients can be approved immediately
                'pimage': url_for('static', filename='uploads/' + filename)  # Store the image URL
            }

            patients.append(new_user)
            session['username'] = username
            session['role'] = 'patient'
            return redirect(url_for('index'))
        
        except BadRequestKeyError:
            return render_template('Auth/register.html', message="Bad request. Please try again.", error=True)

    return render_template('Auth/register.html')

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
                return render_template('Admin/admin_dashboard.html', username=username, doctors=doctors, nurses=nurses)

            # Check if the user is a Doctor
            for user in doctors:
                if username == user['username'] and password == user['password']:
                        session['username'] = username
                        session['role'] = user['role'].lower()
                        if remember_me:
                            session.permanent = True
                        return redirect(url_for('doctor_dashboard'))

            # Check if the user is a Nurse
            for user in nurses:
                if username == user['username'] and password == user['password']:
                        session['username'] = username
                        session['role'] = user['role'].lower()
                        if remember_me:
                            session.permanent = True
                        return redirect(url_for('nurse_dashboard'))

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
            return render_template('Auth/login.html', message="Invalid username or password.", error=True)
        except BadRequestKeyError:
            return render_template('Auth/login.html', message="Bad request. Please try again.", error=True)

    return render_template('Auth/login.html')

# Logout Function
@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('username', None)
    session.pop('role', None)
    return redirect(url_for('index'))

# Forgot Password
@app.route('/forgot_password')
def forgot_password():
    return render_template('Auth/forgot_password.html')
# -------------------------------------------------------------------------------------------------------

# ---------------------- Profile Settings ---------------------------------------------------------------
# Upload Profile Image
@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    username = session.get('username')
    role = session.get('role')
    
    # Check if user is logged in
    if not username:
        return redirect(url_for('login'))

    if request.method == 'POST':
        if 'pimage' not in request.files:
            return "No file part"

        file = request.files['pimage']
        
        if file.filename == '':
            return "No selected file"

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            # Update the user's profile image path
            if role == 'doctor':
                user = next((doc for doc in doctors if doc['username'] == username), None)
            elif role == 'nurse':
                user = next((nurse for nurse in nurses if nurse['username'] == username), None)
            elif role == 'patient':
                user = next((pat for pat in patients if pat['username'] == username), None)
            elif role == 'admin' and username == admin.get('username'):
                user = admin

            if user is not None:
                # Update the image path
                user['pimage'] = f'static/uploads/{filename}'
            
            # Redirect back to the profile page
            return redirect(url_for('view_profile'))
    
    return redirect(url_for('view_profile'))

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
        user['password'] = request.form['password']  

        if role == 'doctor' or role == 'nurse':
            user['specialization'] = request.form['specialization']
            user['intro'] = request.form['intro']
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

    return render_template('Profile/view_profile.html', user=user, role=role)
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

# View Doctors List
@app.route('/view_doctors', methods=['GET', 'POST'])
def view_doctors():
    username = session.get('username')
    role = session.get('role')
    search = request.args.get('search', '')
    specialization = request.args.get('specialization', '')

    # Filtering
    filtered_doctors = doctors
    if search:
        filtered_doctors = [doc for doc in filtered_doctors if search.lower() in doc['username'].lower()]
    if specialization:
        filtered_doctors = [doc for doc in filtered_doctors if doc['specialization'] == specialization]
    return render_template('view_doctors.html', doctors=filtered_doctors, role=role)

# View Nurse List
@app.route('/view_nurses')
def view_nurses():
    username = session.get('username')
    role = session.get('role')
    search = request.args.get('search', '')
    specialization = request.args.get('specialization', '')

    # Filtering 
    filtered_nurses = nurses
    if search:
        filtered_nurses = [doc for doc in filtered_nurses if search.lower() in doc['username'].lower()]
    if specialization:
        filtered_nurses = [doc for doc in filtered_nurses if doc['specialization'] == specialization]
    return render_template('view_nurses.html', nurses=filtered_nurses, role=role)
# -------------------------------------------------------------------------------------------------------------

# ----------------------------------- Get Doctors & Nurses Information ----------------------------------------
def get_doctors():
    return [
        {'id': 1, 'name': 'John', 'username': 'john', 'password': '2345', 'role': 'Doctor', 'email': 'john@example.com', 'contact number': '018-4987676', 'specialization': 'Cardiology'},
        {'id': 2, 'name': 'Smith', 'username': 'smith', 'password': '2345', 'role': 'Doctor', 'email': 'smith@example.com', 'contact number': '016-1652679', 'specialization': 'Dermatology'},
        {'id': 3, 'name': 'Jim', 'username': 'jim', 'password': '2345', 'role': 'Doctor', 'email': 'jim@example.com', 'specialization': 'Dermatology', 'contact number': '012-1322428'}
    ]

def get_nurses():
    return [
    {'id': 1, 'username': 'joy', 'password': '3456', 'role': 'Nurse', 'email': 'joy@example.com', 'contactNumber': '016-7234429', 'specialization': 'Pediatrics'},
    {'id': 2, 'username': 'kate', 'password': '3456', 'role': 'Nurse', 'email': 'kate@example.com', 'contactNumber': '012-6234675', 'specialization': 'General'}
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
    return render_template('Prescription/write_prescription.html', patients=patient_list, role=role, username=username, nurse=nurse, doctor=doctor)

# Doctor & Nurse View Prescription
@app.route('/view_prescriptions')
def view_prescriptions():
    username = session.get('username')
    role = session.get('role')

    if role not in ['doctor', 'nurse']:
        return redirect(url_for('index'))  # Redirect if not a doctor or nurse

    user_prescriptions = [pres for pres in prescriptions]
    return render_template('Prescription/view_prescriptions.html', prescriptions=user_prescriptions,role=role, username=username, nurse=nurse, doctor=doctor)

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
# Route for the Doctor dashboard
@app.route('/doctor/dashboard')
def doctor_dashboard():
    username = session.get('username')
    role = session.get('role')  # Ensure role is stored in session or retrieved from the database
    if role != 'doctor':
        return redirect(url_for('index'))  # Redirect to the index page if not logged in as doctor
    return render_template('Doctor/doctor_dashboard.html', username=username, appointments=appointments)

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
# Route for the Nurse dashboard
@app.route('/nurse/dashboard')
def nurse_dashboard():
    username = session.get('username')
    role = session.get('role')  # Ensure role is stored in session or retrieved from the database
    if role != 'nurse':
        return redirect(url_for('index'))  # Redirect to the index page if not logged in as nurse
    return render_template('Nurse/nurse_dashboard.html', role=role, nurse=nurse, username=username, appointments=appointments)

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

# Admin View Doctors List
@app.route('/admin/view_doctors', methods=['GET', 'POST'])
def admin_view_doctors():
   username = session.get('username')
   role = session.get('role')
   search = request.args.get('search', '')
   specialization = request.args.get('specialization', '')

    # Filtering
   filtered_doctors = doctors
   if search:
        filtered_doctors = [doc for doc in filtered_doctors if search.lower() in doc['username'].lower()]
   if specialization:
        filtered_doctors = [doc for doc in filtered_doctors if doc['specialization'] == specialization]

   return render_template('Admin/admin_view_doctors.html', doctors=filtered_doctors, username=username, role=role)

# Admin View Doctor Intro
@app.route('/admin/view_intro/<int:doctor_id>', methods=['GET'])
def admin_view_intro(doctor_id):
    print(f"Requested doctor ID: {doctor_id}")
    doctor = next((d for d in doctors if d['id'] == doctor_id), None)
    
    if doctor:
        print(f"Doctor found: {doctor}")
        return jsonify(intro=doctor['intro'])
    else:
        print("Doctor not found")
        return jsonify(error="Doctor not found"), 404

    
# Admin View Nurse List
@app.route('/admin/nurses', methods=['GET', 'POST'])
def admin_view_nurses():
    username = session.get('username')
    role = session.get('role')
    search = request.args.get('search', '')
    specialization = request.args.get('specialization', '')

    # Filtering
    filtered_nurses = nurses
    if search:
        filtered_nurses = [doc for doc in filtered_nurses if search.lower() in doc['username'].lower()]
    if specialization:
        filtered_nurses = [doc for doc in filtered_nurses if doc['specialization'] == specialization]

    return render_template('Admin/admin_view_nurses.html', nurses=filtered_nurses, username=username, role=role)

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

# Admin Register Medical Team (Doctor / Nurse)
@app.route('/admin/register_team', methods=['GET', 'POST'])
def register_team():
    # Check if the logged-in user is an admin
    if 'role' not in session or session['role'] != 'admin':
        return render_template('error.html', message="Unauthorized access. Only admins can register medical team.")

    if request.method == 'POST':
        try:
            username = request.form.get('username')
            contactNumber = request.form.get('contactNumber')
            password = request.form.get('password')
            email = request.form.get('email')
            role = request.form.get('role')
            specialization = request.form.get('specialization')
            intro = request.form.get('intro')
            
              # Handle file upload
            if 'pimage' not in request.files:
                return render_template('Auth/register_team.html', message="Profile image is required.", error=True)
            
            file = request.files['pimage']

            # Check if any field is missing
            if not all([username, password, email, role, contactNumber, specialization, intro]) or not file or not allowed_file(file.filename):
                return render_template('Admin/register_team.html', message="All fields are required and the image must be valid.", error=True)

            # Validate role for team
            if role not in ['Doctor', 'Nurse']:
                return render_template('Admin/register_team.html', message="Invalid role selected.", error=True)

            # Secure the filename and save the image
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            # Create new doctor or nurse
            new_team = {
                'id': len(doctors) + len(nurses) + 1,  # Adjust ID logic accordingly
                'username': username,
                'password': password,
                'email': email,
                'contactNumber': contactNumber,
                'role': role,
                'specialization' :specialization,
                'intro': intro,
                'pimage': url_for('static', filename='uploads/' + filename)  # Store the image URL
            }

             # Add new team member to the respective list based on role
            if role == 'Doctor':
                doctors.append(new_team)
                # After successful registration, redirect to the doctor list view
                return redirect(url_for('admin_view_doctors'))
            elif role == 'Nurse':
                nurses.append(new_team)
                # After successful registration, redirect to the nurse list view
                return redirect(url_for('admin_view_nurses'))
        
        except BadRequestKeyError:
            return render_template('Admin/register_team.html', message="Bad request. Please try again.", error=True)

    return render_template('Admin/register_team.html')

# Admin to View All Appointment
@app.route('/admin/appointments')
def admin_appointments():
    # Sort appointments by date and time
    appointments_sorted = sorted(appointments, key=lambda x: (datetime.strptime(x['date'], '%Y-%m-%d'), x['time']))
    username = session.get('username')
    role = session.get('role')
    return render_template('Admin/admin_appointments.html', appointments=appointments_sorted, doctors=doctors, username=username, role=role)

# ---------------------- Admin/Doctor/Nurse Medical Stock Management Function --------------------------------------------------

# View Medical Stock
@app.route('/medication')
def view_medication():
    username = session.get('username')
    role = session.get('role')

    for med in medications:
        try:
            # Convert price to float and format it to two decimal places
            med['price'] = "{:.2f}".format(float(med['price']))
        except (ValueError, TypeError) as e:
            print(f"Error formatting price {med['price']}: {e}")
            med['price'] = "0.00"  # Default value in case of error
    return render_template('Medication/view_stock.html', medications=medications, username=username, role=role)

# Add Medical To Stock
@app.route('/medication/add', methods=['GET', 'POST'])
def add_medication():
    username = session.get('username')
    role = session.get('role')

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
    return render_template('Medication/add_stock.html', medications=medications, username=username, role=role)

# Edit Medical Stock
@app.route('/medication/edit/<int:id>', methods=['GET', 'POST'])
def edit_medication(id):
    username = session.get('username')
    role = session.get('role')

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

    return render_template('Medication/edit_stock.html', medication=medication, username=username, role=role)

# Delete Medical Stock
@app.route('/medication/delete/<int:id>')
def delete_medication(id):
    username = session.get('username')
    role = session.get('role')

    global medications
    medications = [med for med in medications if med['id'] != id]
    flash('Medication deleted successfully!')
    return redirect(url_for('view_medication'))

# Admin/Nurse/Doctor View Patients List
@app.route('/view_patients', methods=['GET', 'POST'])
def view_patients():
    username = session.get('username')
    role = session.get('role')
    search_query = request.args.get('search', '').lower()

    # Filter patients based on the search query
    filtered_patients = [
        patient for patient in patients 
        if search_query in patient['username'].lower() 
    ]

    return render_template('view_patients.html',username=username, patients=filtered_patients, role=role)

# View Patient Address
@app.route('/view_address/<int:patient_id>', methods=['GET'])
def view_address(patient_id):
    # Fetch the patient based on the ID
    patient = next((p for p in patients if p['id'] == patient_id), None)
    if patient:
        return jsonify({'address': patient['address']})
    return jsonify({'error': 'Patient not found'}), 404

# ------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':
    app.run(debug=True)