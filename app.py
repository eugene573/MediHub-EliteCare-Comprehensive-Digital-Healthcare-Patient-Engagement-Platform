import os
import random
import paypalrestsdk
import json
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from werkzeug.exceptions import BadRequestKeyError
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
#from flask_pymongo import PyMongo
#from pymongo import MongoClient
from flask_cors import CORS
from flask_mail import Mail, Message
from dotenv import load_dotenv
from collections import defaultdict

# Connect to MongoDB (use your URI here)
#client = MongoClient("mongodb+srv://eugenefong2002:fong55668921@cluster0.5mjroyf.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")

# Select the database you want to work with
#db = client['test']

# Collections
#admin_collection = db['admins']
#patients_collection = db['patients']
#nurses_collection = db['nurses']
#doctors_collection = db['doctors']
#appointments_collection = db['appointments']
#prescriptions_collection = db['prescriptions']
#medications_collection = db['medications']

# Configure PayPal SDK
paypalrestsdk.configure({
    "mode": "sandbox",  # Change to 'live' for production
    "client_id": "AfwdTxdUXUNswokDBXNY1kNjYp0VZaqzk4HpED704rAbg8IWu7WAlXE0Q1DP10yiwoODHEWF7I4CUZnF",
    "client_secret": "ENsvIkGLuNzNz-D6msKZvqDWInyxABpdppH2QnztpJ2dIwVLxlYDplPMjwMo1b9y6PXZsHkiA_Kpmhex"
})

# Set up the upload folder and allowed extensions
UPLOAD_FOLDER = 'static/uploads'  # Ensure this folder exists or create it
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}  # Allowed file types

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Load environment variables (if using .env for storing sensitive info)
load_dotenv()

app = Flask(__name__)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # Replace with your SMTP server (e.g., Gmail)
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'eugenefong2002@gmail.com'  # Replace with your email address
app.config['MAIL_PASSWORD'] = 'ygvn kand nwit apdg'  # Replace with your email password
app.config['MAIL_DEFAULT_SENDER'] = 'eugenefong2002@gmail.com'  # Default sender (your email)
mail = Mail(app)
app.secret_key = 'your_secret_key'  # Change this to a random secret key for security
#app.config["MONGO_URI"] = "mongodb+srv://eugenefong2002:fong55668921@cluster0.5mjroyf.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
#mongo = PyMongo(app)
# Configure upload folder
UPLOAD_FOLDER = 'static/uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    
# Dummy data for Admin
admin = {'username': 'Admin', 'password': '9999', 'email': 'admin@example.com', 'role': 'Admin', 'contactNumber': '012-2358761', 'pimage':'https://cdn.prod.website-files.com/639ff8596ae419fae300b099/641017314cc67fbb88c517a7_good-linkedin-profile-photo-right-expression-1000x1000.jpeg'}

# Dummy data for patients
patients = [
    {'id': 1, 'username': 'Eugene Fong', 'password': '1234', 'email': 'eugenefong2002@gmail.com', 'contactNumber': '016-7165348', 'role': 'Patient', 'address': '420 Jalan Kota Iskandar, 79200 Iskandar Puteri, Johor, Malaysia.', 'pimage':'https://media.istockphoto.com/id/597958694/photo/young-adult-male-student-in-the-lobby-of-a-university.jpg?s=612x612&w=0&k=20&c=QaNEzmcKrLJzmwOcu2lgwm1B7rm3Ouq2McYYdmoMGpU='},
    {'id': 2, 'username': 'Bob Goh', 'password': '1234', 'email': 'bob@example.com', 'contactNumber': '012-2894590', 'role':'Patient', 'address': '708 Jalan Rahmat,83000 Batu Pahat, Johor, Malaysia.', 'pimage':'https://plus.unsplash.com/premium_photo-1689977968861-9c91dbb16049?fm=jpg&q=60&w=3000&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8MXx8cHJvZmlsZSUyMHBpY3R1cmV8ZW58MHx8MHx8fDA%3D'},
    {'id': 3, 'username': 'Lily Tan', 'password': '1234', 'email': 'lily@example.com', 'contactNumber': '012-2894569', 'role':'Patient', 'address': '271 Jalan Renggam, 86000 Kluang, Johor, Malaysia.', 'pimage':'https://www.profilebakery.com/wp-content/uploads/2023/04/AI-Profile-Picture.jpg'},
    {'id': 4, 'username': 'Ray Wu', 'password': '1234', 'email': 'ray@example.com', 'contactNumber': '012-1127338', 'role':'Patient', 'address': '101 Jalan Skudai, 81300 Skudai, Johor, Malaysia.', 'pimage':'https://i.pinimg.com/474x/98/51/1e/98511ee98a1930b8938e42caf0904d2d.jpg'},
    {'id': 5, 'username': 'Cael Ang', 'password': '1234', 'email': 'cael@example.com', 'contactNumber': '012-2891232', 'role':'Patient', 'address': '339 Jalan Trus, 80000 Johor Bahru, Johor, Malaysia.', 'pimage':'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQSoQFvYAr4KD4S-iecBnmLmPf7zuyFyHkd8w&s'}
]

# Dummy data for nurses
nurses = [
    {'id': 1, 'username': 'Joy Li', 'password': '3456', 'role': 'Nurse', 'fee': '80', 'email': 'joy@example.com', 'contactNumber': '016-7234429', 'specialization': 'Pediatrics', 'intro': 'Miss Joy graduated with an MBBS from Manipal Academy of Higher Education (MAHE). She is a General Practitioner with experience in treating medical conditions of any age group.', 'pimage':'https://media.istockphoto.com/id/1329569957/photo/happy-young-female-doctor-looking-at-camera.jpg?s=612x612&w=0&k=20&c=7Wq_Y2cl0T4op6Wg_3DFc-xtZfCqTTDvfaXkPGyrHDM='},
    {'id': 2, 'username': 'Kate Wong', 'password': '3456', 'role': 'Nurse', 'fee': '80', 'email': 'kate@example.com', 'contactNumber': '012-6234675', 'specialization': 'Cardiology', 'intro': 'Miss Kate graduated with an MBBS from International Islamic University Malaysia. She has over 7 years of experience as a practicing doctor.', 'pimage':'https://media.istockphoto.com/id/1330046035/photo/headshot-portrait-of-smiling-female-doctor-in-hospital.jpg?s=612x612&w=0&k=20&c=fsNQPbmFIxoKA-PXl3G745zj7Cvr_cFIGsYknSbz_Tg='},
    {'id': 3, 'username': 'Kim Ang', 'password': '3456', 'role': 'Nurse', 'fee': '80', 'email': 'kim@example.com', 'contactNumber': '012-3324699', 'specialization': 'Ophthalmology', 'intro': 'Miss Kim graduated with an MBBS from Jawaharlal Nehru Medical College - KLE University (Belgaum) INDIA. She has 9 years of experience as a practicing doctor.', 'pimage':'https://www.shutterstock.com/image-photo/head-shot-woman-wearing-white-600nw-1529466836.jpg'},
    {'id': 4, 'username': 'Ryan Lee', 'password': '3456', 'role': 'Nurse', 'fee': '80', 'email': 'ryan@example.com', 'contactNumber': '012-2595432', 'specialization': 'General Practice', 'intro': 'Mr Ryan graduated with an MBBS from Jawaharlal Nehru Medical College - KLE University (Belgaum) INDIA. She has 9 years of experience as a practicing doctor.', 'pimage':'https://media.istockphoto.com/id/1468678624/photo/nurse-hospital-employee-and-portrait-of-black-man-in-a-healthcare-wellness-and-clinic-feeling.jpg?s=612x612&w=0&k=20&c=AGQPyeEitUPVm3ud_h5_yVX4NKY9mVyXbFf50ZIEtQI='},
    {'id': 5, 'username': 'Tim Tan', 'password': '3456', 'role': 'Nurse', 'fee': '80', 'email': 'tim@example.com', 'contactNumber': '012-2595887', 'specialization': 'Dermatology', 'intro': 'Mr Tim graduated with an MBBS from Jawaharlal Nehru Medical College - KLE University (Belgaum) INDIA. She has 9 years of experience as a practicing doctor.', 'pimage':'https://img.freepik.com/free-photo/front-view-male-nurse-studio_23-2150796762.jpg?semt=ais_hybrid'},
    {'id': 6, 'username': 'Yasmin Yeo', 'password': '3456', 'role': 'Nurse', 'fee': '80', 'email': 'yasmin@example.com', 'contactNumber': '012-2441178', 'specialization': 'Family Medicine', 'intro': 'Miss Yasmin graduated with an MBBS from Jawaharlal Nehru Medical College - KLE University (Belgaum) INDIA. She has 9 years of experience as a practicing doctor.', 'pimage':'https://plus.unsplash.com/premium_photo-1682141165192-7b4678fe96c8?fm=jpg&q=60&w=3000&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8MXx8bnVyc2VzfGVufDB8fDB8fHww'},
    {'id': 7, 'username': 'Shanice Tang', 'password': '3456', 'role': 'Nurse', 'fee': '80', 'email': 'shanice@example.com', 'contactNumber': '012-9544321', 'specialization': 'Obstetrics and Gynecology', 'intro': 'Miss Shanice graduated with an MBBS from Jawaharlal Nehru Medical College - KLE University (Belgaum) INDIA. She has 9 years of experience as a practicing doctor.', 'pimage':'https://media.istockphoto.com/id/1406698322/photo/young-female-nurse-with-folded-arms-standing-in-hospital.jpg?s=612x612&w=0&k=20&c=e9m9bHOguGXk84VrW5Kc-wPdb876ofLn_F27iRY8gGU='},
    {'id': 8, 'username': 'Corinne Koh', 'password': '3456', 'role': 'Nurse', 'fee': '80', 'email': 'corinne@example.com', 'contactNumber': '012-1237640', 'specialization': 'Obstetrics and Gynecology', 'intro': 'Miss Corinne graduated with an MBBS from Jawaharlal Nehru Medical College - KLE University (Belgaum) INDIA. She has 9 years of experience as a practicing doctor.', 'pimage':'https://yt3.googleusercontent.com/o7Ve1CElx13g5hFN_cD-dAIKelIw2UJ4J9dcwg03PCkZQwFExLY7oNU6Vh6i_GA4MufKyYGZaA=s900-c-k-c0x00ffffff-no-rj'}
]

# Dummy data for doctors
doctors = [
    {'id': 1, 'username': 'John Wong', 'password': '2345', 'role': 'Doctor', 'fee': '50', 'email': 'john@example.com', 'contactNumber': '018-4987676', 'specialization': 'Cardiology', 'intro': 'Dr John graduated with an MBBS from Melaka Manipal Medical College. He has over 10 years of experience as a practicing doctor and is currently running her own clinic in the heart of Kuala Lumpur.', 'pimage':'https://img.freepik.com/free-photo/doctor-offering-medical-teleconsultation_23-2149329007.jpg'},
    {'id': 2, 'username': 'Smith Lee', 'password': '2345', 'role': 'Doctor', 'fee': '80', 'email': 'smith@example.com', 'contactNumber': '016-1652679', 'specialization': 'Orthopedics', 'intro': 'Dr Smith graduated from Universitas Padjadjaran of Indonesia in 2008, and has 12 years of experience as a practising doctor in Malaysia.', 'pimage':'https://www.smhbhopal.com/upload/doctors/1694428861.jpg'},
    {'id': 3, 'username': 'Jim Koh', 'password': '2345', 'role': 'Doctor', 'fee': '80', 'email': 'jim@example.com', 'specialization': 'Dermatology', 'contactNumber': '012-1322428', 'intro': 'Dr Jim graduated with a Medical Degree from Crimea State University in 2010. He has over 10 years of experience as a general practitioner and provided consultation for various medical conditions.', 'pimage':'https://www.hjhospitals.org/photos/doctors/_MG_1170t.jpg'},
    {'id': 4, 'username': 'Amy Ho', 'password': '2345', 'role': 'Doctor', 'fee': '80', 'email': 'amy@example.com', 'specialization': 'Ophthalmology', 'contactNumber': '012-1322428', 'intro': 'Dr Amy graduated with a Medical Degree from Crimea State University in 2010. He has over 10 years of experience as a general practitioner and provided consultation for various medical conditions.', 'pimage':'https://img.freepik.com/premium-photo/smiling-korean-young-female-doctor-profile-photo_1279815-42632.jpg'},
    {'id': 5, 'username': 'Chris Lee', 'password': '2345', 'role': 'Doctor', 'fee': '80', 'email': 'chris@example.com', 'specialization': 'Neurology', 'contactNumber': '012-1322428', 'intro': 'Dr Chris graduated with a Medical Degree from Crimea State University in 2010. He has over 10 years of experience as a general practitioner and provided consultation for various medical conditions.', 'pimage':'https://images.pexels.com/photos/8460090/pexels-photo-8460090.jpeg?cs=srgb&dl=pexels-cristian-rojas-8460090.jpg&fm=jpg'},
    {'id': 6, 'username': 'Bily Heng', 'password': '2345', 'role': 'Doctor', 'fee': '80', 'email': 'bily@example.com', 'specialization': 'Pediatrics', 'contactNumber': '012-1322428', 'intro': 'Dr Bily graduated with a Medical Degree from Crimea State University in 2010. He has over 10 years of experience as a general practitioner and provided consultation for various medical conditions.', 'pimage':'https://st4.depositphotos.com/3776273/39461/i/450/depositphotos_394613312-stock-photo-covid-19-preventing-virus-healthcare.jpg'},
    {'id': 7, 'username': 'Ariana Dan', 'password': '2345', 'role': 'Doctor', 'fee': '80', 'email': 'ariana@example.com', 'specialization': 'Orthopedics', 'contactNumber': '012-1322428', 'intro': 'Dr Ariana graduated with a Medical Degree from Crimea State University in 2010. He has over 10 years of experience as a general practitioner and provided consultation for various medical conditions.', 'pimage':'https://plus.unsplash.com/premium_photo-1664474647299-7ef90322be6c?fm=jpg&q=60&w=3000&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8MXx8d29tZW4lMjBkb2N0b3J8ZW58MHx8MHx8fDA%3D'},
    {'id': 8, 'username': 'Estelle Fong', 'password': '2345', 'role': 'Doctor', 'fee': '80', 'email': 'estelle@example.com', 'specialization': 'Family Medicine', 'contactNumber': '012-1322428', 'intro': 'Dr Estelle graduated with a Medical Degree from Crimea State University in 2010. He has over 10 years of experience as a general practitioner and provided consultation for various medical conditions.', 'pimage':'https://img.freepik.com/premium-photo/expert-female-doctor-clinic-environment_993044-4525.jpg'},
    {'id': 9, 'username': 'Patrick Lau', 'password': '2345', 'role': 'Doctor', 'fee': '80', 'email': 'patrick@example.com', 'specialization': 'Obstetrics and Gynecology', 'contactNumber': '012-1763321', 'intro': 'Dr Patrick graduated with a Medical Degree from Crimea State University in 2010. He has over 10 years of experience as a general practitioner and provided consultation for various medical conditions.', 'pimage':'https://thumbs.dreamstime.com/b/young-doctor-work-10916012.jpg'},
    {'id': 10, 'username': 'Natalia Goh', 'password': '2345', 'role': 'Doctor', 'fee': '80', 'email': 'natalia@example.com', 'specialization': 'General Practice', 'contactNumber': '012-6653199', 'intro': 'Dr Natalia graduated with a Medical Degree from Crimea State University in 2010. He has over 10 years of experience as a general practitioner and provided consultation for various medical conditions.', 'pimage':'https://images.pexels.com/photos/5215024/pexels-photo-5215024.jpeg?cs=srgb&dl=pexels-shkrabaanthony-5215024.jpg&fm=jpg'}
]

# Sample timeslot data
timeslot_data = {
    "2024-11-05": [
        {"time": "12:00 pm - 01:30 pm", "status": "available"},
        {"time": "02:00 pm - 03:30 pm", "status": "taken"},
        {"time": "04:00 pm - 05:30 pm", "status": "over"}
    ],
}

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
    {'id': 1, 'patient_id': 1, 'doctor_id': 5, 'date': '2024-08-12', 'time': '9:00 am - 10:00 am', 'type': 'telemedicine', 'meeting_room_code':'543230'},
    {'id': 2, 'patient_id': 3, 'doctor_id': 3, 'date': '2024-12-28', 'time': '1:00 pm - 2:00 pm', 'type': 'telemedicine', 'meeting_room_code':'987647'},
    {'id': 3, 'patient_id': 1, 'doctor_id': 1, 'date': '2024-08-25', 'time': '3:00 pm - 4:00 pm', 'type': 'telemedicine', 'meeting_room_code':'392146'},
    {'id': 4, 'patient_id': 1, 'nurse_id': 3, 'date': '2024-12-16', 'time': '3:00 pm - 4:00 pm', 'type': 'home visit'},

    {'id': 5, 'patient_id': 1, 'doctor_id': 1, 'date': '2025-01-06', 'time': '3:00 pm - 4:00 pm', 'type': 'telemedicine', 'meeting_room_code':'642187'},
    {'id': 6, 'patient_id': 3, 'nurse_id': 3, 'date': '2025-01-13', 'time': '1:00 pm - 2:00 pm', 'type': 'home visit'},
    {'id': 7, 'patient_id': 2, 'doctor_id': 2, 'date': '2025-01-09', 'time': '9:00 am - 10:00 am', 'type': 'telemedicine', 'meeting_room_code':'436231'},
    {'id': 8, 'patient_id': 4, 'nurse_id': 4, 'date': '2024-11-13', 'time': '11:00 am - 12:00 pm', 'type': 'home visit'},
    {'id': 9, 'patient_id': 5, 'doctor_id': 5, 'date': '2024-11-13', 'time': '3:00 pm - 4:00 pm', 'type': 'telemedicine', 'meeting_room_code':'912042'},
    {'id': 10, 'patient_id': 1, 'doctor_id': 2, 'date': '2024-11-13', 'time': '1:00 pm - 2:00 pm', 'type': 'telemedicine', 'meeting_room_code':'492741'},
    {'id': 11, 'patient_id': 1, 'nurse_id': 1, 'date': '2024-12-17', 'time': '11:00 am - 12:00 pm', 'type': 'home visit'},
]

# Dummy feedback data
feedback_list = [
    {'name': 'Ray Wu', 'pimage':'https://i.pinimg.com/474x/98/51/1e/98511ee98a1930b8938e42caf0904d2d.jpg', 'message': 'Great service, really helpful!'},
    {'name': 'Lily Tan', 'pimage':'https://www.profilebakery.com/wp-content/uploads/2023/04/AI-Profile-Picture.jpg', 'message': 'Very informative, will use again.'},
    {'name': 'Cael Ang', 'pimage':'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQSoQFvYAr4KD4S-iecBnmLmPf7zuyFyHkd8w&s', 
     'message': 'I love the ease of scheduling appointments!'}
]

# Dummy data for prescriptions
prescriptions = [
     
    {
     "id": 1,
        "author_username": "John Wong",
        "author_email": "john@example.com",
        "patient_id": "2",
        "patient_username": "Bob Goh",
        "patient_email": "bob@example.com",
        "medications": [
            {
                "medication": "Ibuprofen",
                "dosage": "3",
                "instructions": "Take two after meals",
                "price": "60.0",
                "image_url": "https://5.imimg.com/data5/SELLER/Default/2023/9/344827499/TG/YT/FY/192270567/ibuprofen-tablet-400mg.png"
            },
            {
                "medication": "Ciprofloxacin",
                "dosage": "2",
                "instructions": "Take one every 6 hours as needed",
                "price": "80.0",
                "image_url": "https://cdn.shopify.com/s/files/1/1290/8299/products/Ciprofloxacin500mgboxcopy.png?v=1603264196"
            },
            {
                "medication": "Lisinopril",
                "dosage": "1",
                "instructions": "Take one after breakfast and lunch",
                "price": "50.0",
                "image_url": "https://5.imimg.com/data5/SELLER/Default/2023/1/JR/YJ/LF/29824675/lisinopril-20-mg-tablet.jpg"
            }
        ],
        "total_price": "250.0",
        "date": "2024-11-23",
        "is_paid": True
    },

 
{
    "id": 2,
    "author_username": "John Wong",
    "author_email": "john@example.com",
    "patient_id": "1",
    "patient_username": "Eugene Fong",
    "patient_email": "eugenefong2002@gmail.com",
    "medications": [
        {
            "medication": "Ibuprofen",
            "dosage": "1",
            "instructions": "Take one every 6 hours as needed",
            "price": "20.0",
            "image_url": "https://5.imimg.com/data5/SELLER/Default/2023/9/344827499/TG/YT/FY/192270567/ibuprofen-tablet-400mg.png"
        }
    ],
    "total_price": "70.0",
    "date": "2025-01-06",
    "is_paid": True
    },

{
        "id": 3,
        "author_username": "John Wong",
        "author_email": "john@example.com",
        "patient_id": "5",
        "patient_username": "Cael Ang",
        "patient_email": "cael@example.com",
        "medications": [
            {
                "medication": "Paracetamol",
                "dosage": "1",
                "instructions": "Take two after meals",
                "price": "10.0",
                "image_url": "https://guardian.com.my/media/catalog/product/1/2/121115012_axcel_pcm_500mg_tab_10sx10.jpg?auto=webp&format=pjpg&width=640&height=800&fit=cover"
            }
        ],
        "total_price": "90.0",
        "date": "2024-08-13",
        "is_paid": True
    },

      {
        "id": 4,
        "author_username": "John Wong",
        "author_email": "john@example.com",
        "patient_id": "3",
        "patient_username": "Lily Tan",
        "patient_email": "lily@example.com",
        "medications": [
            {
                "medication": "Paracetamol",
                "dosage": "1",
                "instructions": "Take two after meals",
                "price": "10.0",
                "image_url": "https://guardian.com.my/media/catalog/product/1/2/121115012_axcel_pcm_500mg_tab_10sx10.jpg?auto=webp&format=pjpg&width=640&height=800&fit=cover"
            }
        ],
        "total_price": "100.0",
        "date": "2024-08-15",
        "is_paid": True
    },
     {
        "id": 5,
        "author_username": "Smith Lee",
        "author_email": "smith@example.com",
        "patient_id": "4",
        "patient_username": "Ray Wu",
        "patient_email": "ray@example.com",
        "medications": [
            {
                "medication": "Paracetamol",
                "dosage": "1",
                "instructions": "Take two after meals",
                "price": "10.0",
                "image_url": "https://guardian.com.my/media/catalog/product/1/2/121115012_axcel_pcm_500mg_tab_10sx10.jpg?auto=webp&format=pjpg&width=640&height=800&fit=cover"
            }
        ],
        "total_price": "80.0",
        "date": "2024-08-20",
        "is_paid": True
    },

    
]

# Dummy data for medication stock
medications = [
    {
        'id': 1,
        'name': 'Paracetamol',
        'description': 'Used for pain relief and fever reduction.',
        'quantity': 100,
        'price': 10.00,  # Price per unit
        'expiry_date': '2025-12-31',
        'supplier': 'PharmaCorp',
        'image': 'https://guardian.com.my/media/catalog/product/1/2/121115012_axcel_pcm_500mg_tab_10sx10.jpg?auto=webp&format=pjpg&width=640&height=800&fit=cover'
    },
    {
        'id': 2,
        'name': 'Amoxicillin',
        'description': 'An antibiotic used to treat various infections.',
        'quantity': 200,
        'price': 20.00,  # Price per unit
        'expiry_date': '2024-08-15',
        'supplier': 'MedSupply Co.',
        'image': 'https://5.imimg.com/data5/ANDROID/Default/2023/4/302037696/HU/JI/VN/116627000/product-jpeg-500x500.jpg'
    },
    {
        'id': 3,
        'name': 'Ibuprofen',
        'description': 'Nonsteroidal anti-inflammatory drug used for pain, fever, and inflammation.',
        'quantity': 150,
        'price': 30.00,  # Price per unit
        'expiry_date': '2026-03-21',
        'supplier': 'HealthPharma',
        'image': 'https://5.imimg.com/data5/SELLER/Default/2023/9/344827499/TG/YT/FY/192270567/ibuprofen-tablet-400mg.png'
    },
    {
        'id': 4,
        'name': 'Ciprofloxacin',
        'description': 'Antibiotic used to treat a variety of bacterial infections.',
        'quantity': 75,
        'price': 40.00,  # Price per unit
        'expiry_date': '2023-11-30',
        'supplier': 'Global Meds Inc.',
        'image': 'https://cdn.shopify.com/s/files/1/1290/8299/products/Ciprofloxacin500mgboxcopy.png?v=1603264196'
    },
    {
        'id': 5,
        'name': 'Lisinopril',
        'description': 'Medication used to treat high blood pressure and heart failure.',
        'quantity': 120,
        'price': 50.00,  # Price per unit
        'expiry_date': '2027-07-12',
        'supplier': 'CardioMeds',
        'image': 'https://5.imimg.com/data5/SELLER/Default/2023/1/JR/YJ/LF/29824675/lisinopril-20-mg-tablet.jpg'
    }
]

# Insert data into MongoDB collections
#admin_collection.insert_one(admin)
#patients_collection.insert_many(patients)
#nurses_collection.insert_many(nurses)
#doctors_collection.insert_many(doctors)
#appointments_collection.insert_many(appointments)
#prescriptions_collection.insert_many(prescriptions)
#medications_collection.insert_many(medications)

#print("Data inserted successfully!")

# Insert data into MongoDB collections, checking if the data already exists

# Insert admin data (only if not already present)
#if admin_collection.count_documents({'email': admin['email']}) == 0:
#    admin_collection.insert_one(admin)

# Insert patients data (only if not already present)
#for patient in patients:
#   if patients_collection.count_documents({'email': patient['email']}) == 0:
#        patients_collection.insert_one(patient)

# Insert nurses data (only if not already present)
#for nurse in nurses:
#    if nurses_collection.count_documents({'email': nurse['email']}) == 0:
#        nurses_collection.insert_one(nurse)

# Insert doctors data (only if not already present)
#for doctor in doctors:
#    if doctors_collection.count_documents({'email': doctor['email']}) == 0:
#        doctors_collection.insert_one(doctor)

# Insert appointments data (only if not already present)
#for appointment in appointments:
#    if appointments_collection.count_documents({'id': appointment['id']}) == 0:
#        appointments_collection.insert_one(appointment)

# Insert prescriptions data (only if not already present)
#for prescription in prescriptions:
#    if prescriptions_collection.count_documents({'id': prescription['id']}) == 0:
#        prescriptions_collection.insert_one(prescription)

# Insert medications data (only if not already present)
#for medication in medications:
#    if medications_collection.count_documents({'name': medication['name']}) == 0:
#        medications_collection.insert_one(medication)

#print("Data inserted successfully without duplication!")

def get_doctor_name(doctor_id):
    return next((doctor['username'] for doctor in doctors if doctor['id'] == doctor_id), "Unknown Doctor")

def get_nurse_name(nurse_id):
    return next((nurse['username'] for nurse in nurses if nurse['id'] == nurse_id), "Unknown Nurse")

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

# Helper function to convert time to 24-hour format
def convert_to_24hr_format(time_str):
    return datetime.strptime(time_str, '%I:%M %p')  

def merge_appointments(source_id, target_id):
    source_appt = next((a for a in appointments if a['id'] == source_id), None)
    target_appt = next((a for a in appointments if a['id'] == target_id), None)
    
    if source_appt and target_appt and source_appt['date'] == target_appt['date']:
        source_appt['time'] = target_appt['time']
        return True
    return False
# -----------------------------------------------------------------------------------------------------

@app.route('/merge_appointments', methods=['POST'])
def handle_merge():
    source_id = int(request.form.get('source_id'))
    target_id = int(request.form.get('target_id'))
    
    success = merge_appointments(source_id, target_id)
    if success:
        return jsonify({"status": "success"})
    return jsonify({"status": "error", "message": "Could not merge appointments"}), 400

@app.route('/get_taken_times', methods=['POST'])
def get_taken_times():
    doctor_id = request.json.get('doctor_id')
    selected_date = request.json.get('date')

    # Query your database for appointments on the selected date for the given doctor
    # Replace this with your actual query
    appointments = appointments.query.filter_by(doctor_id=doctor_id, date=selected_date).all()
    taken_times = [appointment.time for appointment in appointments]

    return jsonify(taken_times=taken_times)
# ----------------------------- Home Page -------------------------------------------------------------
@app.route('/')
def index():
    username = session.get('username')
    role = session.get('role')  

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

    return render_template('index.html', user=user, username=username, role=role)

# Route to handle feedback submission
@app.route('/submit-feedback', methods=['POST'])
def submit_feedback():
    name = request.form['name']
    message = request.form['message']
    pimage = request.form['pimage']
    
    # Append the new feedback to the dummy list
    feedback_list.append({'name': name, 'message': message, 'pimage': pimage})
    
    # Flash message to confirm submission
    flash("Your feedback has been submitted successfully!", "success")
    
    # Redirect to a confirmation page or the home page
    return redirect(url_for('index'))

# Route for the admin page to view feedback
@app.route('/admin/feedback')
def admin_feedback_page():
    username = session.get('username')
    role = session.get('role')
    feedback_data = feedback_list
    
    user = None
    if role == 'admin' and username == admin.get('username'):
        user = admin
    elif role == 'doctor':
        user = next((doc for doc in doctors if doc['username'] == username), None)
    elif role == 'nurse':
        user = next((nurse for nurse in nurses if nurse['username'] == username), None)
    elif role == 'patient':
        user = next((pat for pat in patients if pat['username'] == username), None)

    # Render the feedback page with the feedback data
    return render_template('Admin/feedback.html', feedback=feedback_data,username=username, role=role, user=user)

# View Doctors List
@app.route('/view_doctors', methods=['GET', 'POST'])
def view_doctors():
    username = session.get('username')
    role = session.get('role')
    search = request.args.get('search', '')
    specialization = request.args.get('specialization', '')

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

    # Filtering
    filtered_doctors = doctors
    if search:
        filtered_doctors = [doc for doc in filtered_doctors if search.lower() in doc['username'].lower()]
    if specialization:
        filtered_doctors = [doc for doc in filtered_doctors if doc['specialization'] == specialization]
    return render_template('view_doctors.html', doctors=filtered_doctors, role=role, user=user, username=username)

# View Nurse List
@app.route('/view_nurses')
def view_nurses():
    username = session.get('username')
    role = session.get('role')
    search = request.args.get('search', '')
    specialization = request.args.get('specialization', '')

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

    # Filtering 
    filtered_nurses = nurses
    if search:
        filtered_nurses = [doc for doc in filtered_nurses if search.lower() in doc['username'].lower()]
    if specialization:
        filtered_nurses = [doc for doc in filtered_nurses if doc['specialization'] == specialization]
    return render_template('view_nurses.html', nurses=filtered_nurses, role=role, user=user, username=username)

# View Specialization
@app.route('/view_specialization')
def view_specialization():
    username = session.get('username')
    role = session.get('role')

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

    return render_template('view_specialization.html', role=role, user=user, username=username)

# MediHub
@app.route('/MediHub')
def MediHub():
    username = session.get('username')
    role = session.get('role')

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

    return render_template('MediHub.html', role=role, user=user, username=username)

# ContactUS
@app.route('/contactUs')
def contactUs():
    username = session.get('username')
    role = session.get('role')

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

    return render_template('contactUs.html', role=role, user=user, username=username)

# FAQ
@app.route('/FAQ')
def FAQ():
    username = session.get('username')
    role = session.get('role')

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

    return render_template('FAQ.html', role=role, user=user, username=username)
# -------------------------------------------------------------------------------------------------------------------

# ----------------------------- MEETING FUNCTION -------------------------------------------------------------------
@app.route('/meeting')
def meeting():
    username = session.get('username')
    role = session.get('role')  

     # Fetch user based on role
    user = None
    if role == 'doctor':
        user = next((doc for doc in doctors if doc['username'] == username), None)
    elif role == 'nurse':
        user = next((nurse for nurse in nurses if nurse['username'] == username), None)
    elif role == 'patient':
        user = next((pat for pat in patients if pat['username'] == username), None)

    return render_template('meeting.html', username=username, role=role, user=user)

# MEETING
@app.route("/join", methods=["GET", "POST"])
def join():
    username = session.get('username')
    role = session.get('role')  

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

    if request.method == "POST":
        room_id = request.form.get("roomID")
        return redirect(f"/meeting?roomID={room_id}")
    return render_template("join.html", username=username, role=role, user=user)

# -------------------------- Auth ---------------------------------------------------------------------
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
                flash("Profile image is required.", "error")
                return render_template('Auth/register.html')
            
            file = request.files['pimage']

            # Check if any field is missing
            if not all([username, password, email, role, contactNumber]) or not file or not allowed_file(file.filename):
                flash("Field missing!", "error")
                return render_template('Auth/register.html')

            # Check if the email already exists
            existing_user = next((user for user in patients if user['email'] == email), None)
            if existing_user:
                flash("This email has been used!", "error")
                return render_template('Auth/register.html')

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
            flash("You have been registered successfully!", "success")
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

            # Check if the user is an ADMIN
            if username == admin['username'] and password == admin['password']:
                session['username'] = username
                session['role'] = 'admin'
                role = session.get('role')  

                 # Fetch user based on role
                user = None
                if role == 'admin' and username == admin.get('username'):
                    user = admin

                if remember_me:
                    session.permanent = True
                
                flash("Welcome back to MediHub!", "success")
                return redirect(url_for('admin_dashboard'))

              # Check if the user is a DOCTOR
            for user in doctors:
                if username == user['username'] and password == user['password']:
                    session['username'] = username
                    session['id'] = user['id']  # Use user['id'] here instead of doctor['id']
                    session['role'] = user['role'].lower()

                    role = session.get('role')  
                
                    # Fetch user based on role
                    user = None
                    if role == 'doctor':
                        user = next((doc for doc in doctors if doc['username'] == username), None)
                
                    if remember_me:
                        session.permanent = True

                    flash("Welcome back to MediHub!", "success")
                    return redirect(url_for('doctor_appointments'))

            # Check if the user is a NURSE
            for user in nurses:
                if username == user['username'] and password == user['password']:
                        session['username'] = username
                        session['id'] = user['id']  # Use user['id'] here instead of nurse['id']
                        session['role'] = user['role'].lower()

                        role = session.get('role')  
                
                         # Fetch user based on role
                        user = None
                        if role == 'nurse':
                             user = next((nurse for nurse in nurses if nurse['username'] == username), None)
                        

                        if remember_me:
                            session.permanent = True

                        flash("Welcome back to MediHub!", "success")
                        return redirect(url_for('nurse_appointments'))

            # Check if the user is a PATIENT
            for patient in patients:
                if username == patient['username'] and password == patient['password']:
                    session['id'] = patient['id']
                    session['username'] = username
                    session['role'] = 'patient'
                    role = session.get('role')  
                
                    # Fetch user based on role
                    user = None
                    if role == 'patient':
                        user = next((pat for pat in patients if pat['username'] == username), None)

                    if remember_me:
                        session.permanent = True
                    flash("Welcome back to MediHub!", "success")
                    return redirect(url_for('index'))

            # Failed login
            return render_template('Auth/login.html', message="Invalid username or password.", error=True)
        except BadRequestKeyError:
            return render_template('Auth/login.html', message="Bad request. Please try again.", error=True)
        
    flash("Login successfully!", "success")
    return render_template('Auth/login.html')

# Logout Function
@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('username', None)
    session.pop('role', None)
    session.clear()  # Clears all session data

    flash("You have been logout successfully!", "success")
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
        
    flash("Profile image has been updated successfully!", "success")
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

    flash("Profile has been updated successfully!", "success")
    return render_template('Profile/view_profile.html', user=user, role=role, username=username)
# ---------------------------------------------------------------------------------------------------

# -------------------------- Patient --------------------------------------------------------------------------
# Route for the Patient Dashboard
@app.route('/patient')
def patient_dashboard():
    email = session.get('email')
    role = session.get('role')  # Ensure role is stored in session or retrieved from the database
    if role != 'patient':
        return redirect(url_for('index'))  # Redirect to the index page if not logged in as patient
    
    # Retrieve the user based on role
    user = None
    if role == 'admin' and email == admin['email']:
        user = admin
    elif role == 'doctor':
        user = next((doc for doc in doctors if doc['email'] == email), None)
    elif role == 'nurse':
        user = next((nurse for nurse in nurses if nurse['email'] == email), None)
    elif role == 'patient':
        user = next((pat for pat in patients if pat['email'] == email), None)

    return render_template('index.html', email=email, user=user, role=role, appointments=appointments)

# ------------------------------------------- Patient Book Telemedicine Appointment ---------------------------------------------------
@app.route('/patient/telemedicine', methods=['GET', 'POST'])
def book_telemedicine_appointment():
    username = session.get('username')
    role = session.get('role')
    current_date = datetime.now().strftime('%Y-%m-%d')

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
        return redirect(url_for('login'))

    if request.method == 'POST':
        patient_id = session.get('id')

        try:
            # Retrieve form data
            selected_doctor_id = request.form.get('doctor')
            appointment_date = request.form.get('date')
            appointment_time = request.form.get('time')

            # Validate the form fields
            if not selected_doctor_id or not appointment_date or not appointment_time:
                error_message = "All fields are required."
                return render_template(
                    'Patient/telemedicine.html',
                    username=username,
                    user=user,
                    role=role,
                    current_date=current_date,
                    doctors=doctors,
                    error_message=error_message,
                )

            # Convert doctor_id to integer
            doctor_id = int(selected_doctor_id)

            # Generate a random six-digit meeting room code
            meeting_room_code = random.randint(100000, 999999)

            # Create new appointment
            new_appointment = {
                'id': len(appointments) + 1,
                'patient_id': patient_id,
                'doctor_id': doctor_id,
                'person_id': doctor_id,  # For telemedicine, person_id is the same as doctor_id
                'date': appointment_date,
                'time': appointment_time,
                'type': 'telemedicine',
                'meeting_room_code': meeting_room_code,  # Add meeting room code here
            }
            appointments.append(new_appointment)

            # Send email reminder to the patient
            patient_email = user.get('email')  # Assuming the patient has an 'email' key
            patient_username = user.get('username')  # Get the username
            send_email_reminder(patient_email, patient_username, appointment_date, appointment_time)

            # Flash success message
            flash("Appointment has been made successfully! A reminder email has been sent to you.", "success")
            return redirect(url_for('patient_appointments'))

        except Exception as e:
            print(f"Error booking telemedicine appointment: {e}")
            return render_template(
                'Patient/telemedicine.html',
                user=user,
                role=role,
                current_date=current_date,
                doctors=doctors,
                error_message="Failed to book the appointment. Please try again.",
            )

    return render_template(
        'Patient/telemedicine.html',
        user=user,
        role=role,
        current_date=current_date,
        doctors=doctors,
        appointments=appointments,
    )

# Function to send email reminder
def send_email_reminder(patient_email, patient_username, appointment_date, appointment_time):
    subject = "Telemedicine Appointment Reminder"
    body = f"Dear {patient_username},\n\nThis is a reminder for your upcoming telemedicine appointment on {appointment_date} at {appointment_time}.\n\n" \
           f"Please be ready at the scheduled time.\n\nBest regards,\nMediHub Healthcare Team"

    sender_email = app.config['MAIL_DEFAULT_SENDER']  # Ensure this is correctly set in your config
    msg = Message(subject, recipients=[patient_email], body=body, sender=sender_email)

    try:
        print(f"Sending email to {patient_email}...")
        mail.send(msg)
        print(f"Email sent successfully to {patient_email}")
    except Exception as e:
        print(f"Error sending email: {e}")

# --------------------------------- Patient Book Home Visit -------------------------------------------------------
@app.route('/patient/home_visit', methods=['GET', 'POST'])
def book_home_visit_appointment():
    username = session.get('username')
    role = session.get('role')
    current_date = datetime.now().strftime('%Y-%m-%d')
    
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

    # Check if the user has an address
    if role == 'patient' and (not user or not user.get('address')): 
        flash("Please update your address before booking a home visit appointment.", "error")
        return render_template(
            'Profile/view_profile.html',
            user=user,
            role=role,
            current_date=current_date,
            nurses=nurses,
            error_message="Please update your address before booking a home visit appointment."
        )
    
    if request.method == 'POST':
        patient_id = session.get('id')
        
        try:
            selected_nurse_id = request.form.get('nurse')
            appointment_date = request.form.get('date')
            appointment_time = request.form.get('time')

            if not selected_nurse_id or not appointment_date or not appointment_time:
                error_message = "All fields are required."
                return render_template(
                    'Patient/home_visit.html',
                    user=user,
                    role=role,
                    current_date=current_date,
                    nurses=nurses,
                    error_message=error_message
                )
            
            # Convert nurse_id to integer
            nurse_id = int(selected_nurse_id)

            new_appointment = {
                'id': len(appointments) + 1,
                'patient_id': patient_id,
                'nurse_id': nurse_id,
                'person_id': nurse_id,
                'date': appointment_date,
                'time': appointment_time,
                'type': 'home visit'
            }
            appointments.append(new_appointment)

            # Send email reminder to the patient
            patient_email = user.get('email')  # Assuming the patient has an 'email' key
            patient_username = user.get('username')  # Get the username
            send_home_visit_email_reminder(patient_email, patient_username, appointment_date, appointment_time)

            # Flash success message
            flash("Appointment has been made successfully! A reminder email has been sent to you.", "success")
            return redirect(url_for('patient_appointments'))

        except Exception as e:
            print(f"Error booking home visit appointment: {e}")
            return render_template(
                'Patient/home_visit.html',
                user=user,
                role=role,
                current_date=current_date,
                nurses=nurses,
                error_message="Failed to book the appointment. Please try again."
            )
    
    return render_template(
        'Patient/home_visit.html',
        user=user,
        role=role,
        current_date=current_date,
        nurses=nurses,
        appointments=appointments
    )

# Function to send home visit email reminder
def send_home_visit_email_reminder(patient_email, patient_username, appointment_date, appointment_time):
    subject = "Home Visit Appointment Reminder"
    body = f"Dear {patient_username},\n\nThis is a reminder for your upcoming home visit appointment on {appointment_date} at {appointment_time}.\n\n" \
           f"Please be ready at the scheduled time.\n\nBest regards,\nMediHub Healthcare Team"

    sender_email = app.config['MAIL_DEFAULT_SENDER']  # Ensure this is correctly set in your config
    msg = Message(subject, recipients=[patient_email], body=body, sender=sender_email)

    try:
        print(f"Sending email to {patient_email}...")
        mail.send(msg)
        print(f"Email sent successfully to {patient_email}")
    except Exception as e:
        print(f"Error sending email: {e}")
    
# --------------------------------- Patient View Appointment -------------------------------------------------
@app.route('/patient/appointments')
def patient_appointments():
    patient_id = session.get('id')
    
    # Fetch appointments for the current patient
    patient_appointments = [app for app in appointments if app['patient_id'] == patient_id]
 
    current_date = datetime.now().strftime('%Y-%m-%d')
    username = session.get('username')
    role = session.get('role')
    search_start_date = request.args.get('search_start_date')  # Get the start date from the query params
    search_end_date = request.args.get('search_end_date')  # Get the end date from the query params

    # Ensure time format consistency by stripping leading/trailing spaces
    for app in patient_appointments:
        app['time'] = app['time'].strip()  # Remove extra spaces

    # Sort appointments by date and time
    appointments_sorted = sorted(patient_appointments, key=lambda x: (
        datetime.strptime(x['date'], '%Y-%m-%d'),
        convert_to_24hr_format(x['time'].split(' - ')[0])  # Get the start time and convert to 24-hour format
    ))
    
    # If a date range is provided, filter appointments by the range
    if search_start_date and search_end_date:
        appointments_sorted = [
            appt for appt in appointments_sorted
            if search_start_date <= appt['date'] <= search_end_date
        ]
    elif search_start_date:
        appointments_sorted = [appt for appt in appointments_sorted if appt['date'] >= search_start_date]
    elif search_end_date:
        appointments_sorted = [appt for appt in appointments_sorted if appt['date'] <= search_end_date]

    no_appointments_found = len(appointments_sorted) == 0

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

    return render_template(
        'Patient/patient_appointments.html',
        user=user,
        username=username,
        role=role,
        appointments=appointments_sorted,
        current_date=current_date,
        doctors=doctors,
        nurses=nurses,
        search_start_date=search_start_date,
        search_end_date=search_end_date,
        no_appointments_found=no_appointments_found
    )

# Delete Appointment
@app.route('/patient/appointments/delete/<int:appointment_id>', methods=['POST'])
def delete_appointment(appointment_id):
    global appointments
    # Find the appointment by ID and remove it from the list
    appointments = [app for app in appointments if app['id'] != appointment_id]
    
    flash("Appointment has been deleted successfully!", "success")
    return redirect(url_for('patient_appointments'))

# ----------------------------- PAYPAL ----------------------------------------------------------------------------
@app.route('/direct_payment')
def direct_payment():
    prescription_id = request.args.get('prescription_id')  # Get prescription ID from query params

    # Find the prescription in the dummy data
    prescription = next((pres for pres in prescriptions if str(pres['id']) == prescription_id), None)

    if not prescription:
        flash("Prescription not found.", "error")
        return redirect(url_for('patient_view_prescription'))

    # Extract details from the prescription for payment
    name = prescription['patient_username']
    email = session.get('email', 'patient_email')  # Replace with the user's email logic
    amount = prescription['total_price']

    # Create a PayPal payment
    payment = paypalrestsdk.Payment({
        "intent": "sale",
        "payer": {"payment_method": "paypal"},
        "redirect_urls": {
            "return_url": url_for('payment_success', prescription_id=prescription_id, _external=True),
            "cancel_url": url_for('payment_cancelled', prescription_id=prescription_id, _external=True)
        },
        "transactions": [{
            "amount": {"total": amount, "currency": "MYR"},
            "description": f"Payment for prescription {prescription_id}"
        }]
    })

    if payment.create():
        for link in payment.links:
            if link.rel == "approval_url":
                approval_url = link.href
                return redirect(approval_url)
    else:
        app.logger.error(f"PayPal payment creation failed: {payment.error}")
        flash("Payment failed. Please try again.", "error")
        return redirect(url_for('patient_view_prescription'))

@app.route('/payment_success')
def payment_success():
    prescription_id = request.args.get('prescription_id')  # Get prescription ID from query params
    patient_username = session.get('username')

    # Find and mark the prescription as paid
    for pres in prescriptions:
        if str(pres['id']) == prescription_id and pres['patient_username'] == patient_username:
            pres['is_paid'] = True
            app.logger.info(f"Prescription {prescription_id} marked as paid.")

            # Retrieve patient email and prescription date
            patient_email = next((pat['email'] for pat in patients if pat['username'] == patient_username), None)
            prescription_date = pres.get('date')

            # Send payment success email
            if patient_email and prescription_date:
                send_payment_success_email(patient_email, patient_username, prescription_date)
            break

    flash("Thank you! Payment was successful. A payment conformation email has been sent to you.", "success")
    return redirect(url_for('patient_view_prescription'))


def send_payment_success_email(patient_email, patient_username, prescription_date):
    subject = "Payment Successful - MediHub"
    body = f"Dear {patient_username},\n\nYour payment for the prescription dated {prescription_date} has been successfully processed.\n\n" \
           f"Thank you for choosing MediHub!\n\nBest regards,\nMediHub Healthcare Team"

    try:
        # Compose and send email
        msg = Message(subject, recipients=[patient_email])
        msg.body = body
        mail.send(msg)
        app.logger.info(f"Payment confirmation email sent to {patient_email}.")
    except Exception as e:
        app.logger.error(f"Failed to send email: {e}")


@app.route('/payment_cancelled')
def payment_cancelled():
    return "Payment was cancelled. Please try again."

@app.route('/patient_view_prescription')
def patient_view_prescription():
    username = session.get('username')
    role = session.get('role')
    search_start_date = request.args.get('search_start_date')  # Get the start date from query params
    search_end_date = request.args.get('search_end_date')  # Get the end date from query params

    # Ensure the user is logged in as a patient
    if role != 'patient' or not username:
        return redirect(url_for('index'))  # Redirect if not a patient or email is missing

    # Retrieve the patient based on email
    user = next((pat for pat in patients if pat['username'] == username), None)

    if not user:
        flash("User not found!", "error")
        return redirect(url_for('index'))

    # Get prescriptions for the logged-in patient
    patient_prescriptions = [
        pres for pres in prescriptions
        if pres.get('patient_username') == user.get('username')  # Use user's username
    ]

    # Filter prescriptions by date range if provided
    if search_start_date and search_end_date:
        patient_prescriptions = [
            pres for pres in patient_prescriptions
            if search_start_date <= pres['date'] <= search_end_date
        ]

    # Sort prescriptions by date (latest to earliest)
    patient_prescriptions = sorted(
        patient_prescriptions,
        key=lambda x: datetime.strptime(x['date'], '%Y-%m-%d'),
        reverse=True
    )

    # Generate image URLs
    for pres in patient_prescriptions:
        if pres.get('image'):
            pres['image_url'] = url_for('static', filename='uploads/' + pres['image'])

    return render_template(
        'Patient/patient_prescription.html',
        user=user,
        username=username,
        prescriptions=patient_prescriptions,
        role=role,
        search_start_date=search_start_date,
        search_end_date=search_end_date,
        no_prescriptions_found=len(patient_prescriptions) == 0
    )


@app.route('/view_prescription_as_bill')
def view_prescription_as_bill():
    prescription_id = request.args.get('prescription_id')
    # Fetch the prescription details using the ID
    prescription = next((p for p in prescriptions if p['id'] == int(prescription_id)), None)
    if not prescription or not prescription.get('is_paid'):
        flash("Prescription not found or payment not completed.", "danger")
        return redirect('Patient/patient_view_prescription')

    # Render a template showing the prescription as a bill
    return render_template('Patient/patient_bill_template.html', prescription=prescription)

@app.route('/toggle_payment_status', methods=['POST'])
def toggle_payment_status():
    prescription_id = request.form.get('prescription_id')
    prescription = next((pres for pres in prescriptions if str(pres['id']) == prescription_id), None)

    if not prescription:
        flash("Prescription not found.", "error")
        return redirect(url_for('view_prescriptions'))

    # Toggle the payment status
    prescription['is_paid'] = not prescription['is_paid']

    flash("Payment status updated successfully.", "success")
    return redirect(url_for('view_prescriptions'))
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
@app.route('/write_prescription', methods=['GET', 'POST'])
def write_prescription():
    username = session.get('username')
    role = session.get('role')

    if role not in ['doctor', 'nurse']:
        return redirect(url_for('index'))

    user = next((doc for doc in doctors if doc['username'] == username), None) if role == 'doctor' else \
           next((nurse for nurse in nurses if nurse['username'] == username), None)

    if not user:
        return redirect(url_for('index'))

    if request.method == 'POST':
        patient_id = int(request.form['patient_id'])
        medication_ids = request.form.getlist('medication_id[]')
        dosages = request.form.getlist('dosage[]')
        instructions_list = request.form.getlist('instructions[]')
        prices = request.form.getlist('price[]')
        total_price = float(request.form.get('total_price', '0'))

        if not (len(medication_ids) == len(dosages) == len(instructions_list) == len(prices)):
            return render_template(
                'Prescription/write_prescription.html',
                patients=patients,
                role=role,
                username=username,
                user=user,
                medications=medications,
                error="Please ensure each medication entry includes dosage, price, and instructions."
            )

        prescription_id = len(prescriptions) + 1
        medications_list = []

        for med_id, dosage, instructions, price in zip(medication_ids, dosages, instructions_list, prices):
            selected_medication = next((med for med in medications if str(med['id']) == med_id), None)
            if selected_medication:
                medication_entry = {
                    'medication': selected_medication['name'],
                    'dosage': dosage,
                    'instructions': instructions,
                    'price': float(price),
                    'image_url': selected_medication['image']
                }
                medications_list.append(medication_entry)

        prescription = {
            'id': prescription_id,
            'author_username': username,
            'author_role': role,
            'patient_id': patient_id,
            'patient_username': next((pat['username'] for pat in patients if pat['id'] == patient_id), None),
            'medications': medications_list,
            'total_price': total_price,
            'date': datetime.now().strftime('%Y-%m-%d'),
            'is_paid': False
        }
        prescriptions.append(prescription)

        # Send email notification to the patient
        patient = next((pat for pat in patients if pat['id'] == patient_id), None)
        if patient:
            send_email_notification(patient['email'], prescription)

        flash("Prescription has been added successfully! An email has been sent to the patient.", "success")
        patient_username = next((pat['username'] for pat in patients if pat['id'] == patient_id), None)
        return redirect(url_for('view_prescriptions', patient_username=patient_username))

    return render_template(
        'Prescription/write_prescription.html',
        patients=patients,
        role=role,
        username=username,
        user=user,
        medications=medications
    )

def send_email_notification(email, prescription):
    # Fetch the patient's name
    patient = next((pat for pat in patients if pat['id'] == prescription['patient_id']), None)
    patient_username = patient['username'] if patient else "Patient"

    subject = "New Prescription Added"
    body = f"Dear {patient_username},\n\n We are pleased to inform you that a new prescription has been added to your account.\n\n" \
           f"Please log in to your account to proceed with the payment to arrange delivery, Thank You.\n\nBest regards,\nMediHub Healthcare Team"

    try:
        msg = Message(subject, recipients=[email])
        msg.body = body
        mail.send(msg)
        print(f"Email sent to {email}")
    except Exception as e:
        print(f"Error sending email: {e}")


# DOCTOR NURSE VIEW PRESCRIPTION
@app.route('/view_prescriptions')
def view_prescriptions():
    username = session.get('username')
    role = session.get('role')

    # Check if user is logged in and authorized
    if role not in ['doctor', 'nurse']:
        return redirect(url_for('index'))  # Redirect unauthorized users

    # Get the logged-in user
    user = None
    if role == 'doctor':
        user = next((doc for doc in doctors if doc['username'] == username), None)
    elif role == 'nurse':
        user = next((nurse for nurse in nurses if nurse['username'] == username), None)

    if not user:
        return redirect(url_for('login'))  # Redirect if user is not found

    # Get today's date
    today = datetime.now()
    today_str = today.strftime('%Y-%m-%d')
    
    # Get yesterday's date
    yesterday = today - timedelta(days=1)
    yesterday_str = yesterday.strftime('%Y-%m-%d')
    
    # Get the date for 7 days ago
    last_7_days = today - timedelta(days=7)
    last_7_days_str = last_7_days.strftime('%Y-%m-%d')

    # Determine if we're filtering for today, yesterday, or last 7 days
    filter_today = request.args.get('filter_today') == 'true'
    filter_yesterday = request.args.get('filter_yesterday') == 'true'
    filter_last_7_days = request.args.get('filter_last_7_days') == 'true'
    
    # Retrieve the patient's email from the query parameter (if provided)
    patient_username = request.args.get('patient_username')

    def matches_date_filter(date):
        """Check if the date matches any active filter."""
        return (
            (filter_today and date == today_str) or
            (filter_yesterday and date == yesterday_str) or
            (filter_last_7_days and date >= last_7_days_str)
        )

    # If no filters are selected, show all prescriptions
    if not (filter_today or filter_yesterday or filter_last_7_days):
        if patient_username:
            user_prescriptions = [
                pres for pres in prescriptions
                if pres.get('author_username') == username and pres.get('patient_username') == patient_username
            ]
        else:
            user_prescriptions = [
                pres for pres in prescriptions
                if pres.get('author_username') == username
            ]
    else:
        # Apply filters
        if patient_username:
            user_prescriptions = [
                pres for pres in prescriptions
                if pres.get('author_username') == username and pres.get('patient_username') == patient_username
                and matches_date_filter(pres.get('date'))
            ]
        else:
            user_prescriptions = [
                pres for pres in prescriptions
                if pres.get('author_username') == username and matches_date_filter(pres.get('date'))
            ]

    # Render the prescriptions page
    return render_template(
        'Prescription/view_prescriptions.html',
        patients=patients,
        prescriptions=user_prescriptions,
        role=role,
        username=username,
        user=user,
        medications=medications,
        prescription=None,
        selected_patient=patient_username,
        filter_today=filter_today,
        filter_yesterday=filter_yesterday,
        filter_last_7_days=filter_last_7_days  
    )

# PRES SEARCH FUNCTION
@app.route('/search_prescriptions', methods=['GET'])
def search_prescriptions():
    username = session.get('username')
    role = session.get('role')

    # Check if user is logged in and authorized
    if role not in ['doctor', 'nurse']:
        return redirect(url_for('index'))

    # Get the logged-in user
    user = None
    if role == 'doctor':
        user = next((doc for doc in doctors if doc['username'] == username), None)
    elif role == 'nurse':
        user = next((nurse for nurse in nurses if nurse['username'] == username), None)

    if not user:
        return redirect(url_for('index'))

    # Retrieve the search query from the URL parameters
    date_start = request.args.get('date_start', '').strip()
    date_end = request.args.get('date_end', '').strip()
    search_results = []

    # Filter prescriptions by date range
    if date_start and date_end:
        search_results = [
            pres for pres in prescriptions
            if pres.get('date') and date_start <= pres['date'] <= date_end
            and pres.get('author_username') == username
        ]

    # Render the template with the search results
    return render_template(
        'Prescription/view_prescriptions.html',
        search_results=search_results,
        date_start=date_start,
        date_end=date_end,
        role=role,
        username=username,
        user=user,
        patients=patients,  # Pass additional required data
        prescriptions=[]  # Avoid template errors; no default prescriptions shown during search
    )

# EDIT PRESCRIPTION FUNCTION
@app.route('/edit_prescription/<int:prescription_id>', methods=['GET', 'POST'])
def edit_prescription(prescription_id):
    username = session.get('username')
    role = session.get('role')

    # Restrict access to doctors and nurses
    if role not in ['doctor', 'nurse']:
        return redirect(url_for('index'))

    # Find the logged-in user
    user = None
    if role == 'doctor':
        user = next((doc for doc in doctors if doc['username'] == username), None)
    elif role == 'nurse':
        user = next((nurse for nurse in nurses if nurse['username'] == username), None)

    # Find the prescription to edit
    prescription = next((pres for pres in prescriptions if pres['id'] == prescription_id), None)
    if not prescription:
        return "Prescription not found", 404

    if request.method == 'POST':
        # Retrieve form data
        patient_id = int(request.form['patient_id'])
        medication_ids = request.form.getlist('medication_id[]')
        dosages = request.form.getlist('dosage[]')
        instructions_list = request.form.getlist('instructions[]')
        prices = request.form.getlist('price[]')
        total_price = float(request.form.get('total_price', '0'))

        # Validate form data consistency
        if not (len(medication_ids) == len(dosages) == len(instructions_list) == len(prices)):
            return render_template(
                'Prescription/edit_prescription.html',
                prescription=prescription,
                medications=medications,
                username=username,
                role=role,
                error="Please ensure each medication entry includes dosage, price, and instructions."
            )

        # Update the prescription with new details
        medications_list = []
        for med_id, dosage, instructions, price in zip(medication_ids, dosages, instructions_list, prices):
            selected_medication = next((med for med in medications if str(med['id']) == med_id), None)
            if selected_medication:
                medication_entry = {
                    'medication': selected_medication['name'],
                    'dosage': dosage,
                    'instructions': instructions,
                    'price': float(price),
                    'image_url': selected_medication['image']
                }
                medications_list.append(medication_entry)

        # Update the prescription
        prescription['patient_id'] = patient_id
        prescription['medications'] = medications_list
        prescription['total_price'] = total_price
        prescription['date'] = datetime.now().strftime('%Y-%m-%d')

        flash("Prescription has been updated successfully!", "success")
        return redirect(url_for('view_prescriptions', patient_username=prescription['patient_username']))

    # Render the edit form with existing prescription details
    return render_template(
        'Prescription/edit_prescription.html',
        prescription=prescription,
        medications=medications,
        username=username,
        role=role
    )

@app.route('/get_prescription/<int:prescription_id>')
def get_prescription(prescription_id):
    # Find the prescription by ID
    prescription = next((pres for pres in prescriptions if pres['id'] == prescription_id), None)
    if not prescription:
        return jsonify({'error': 'Prescription not found'}), 404

    # Return the prescription data as JSON
    return jsonify(prescription)

# DELETE PRESCRIPTION FUNCTION
@app.route('/delete_prescription/<int:prescription_id>', methods=['POST'])
def delete_prescription(prescription_id):
    username = session.get('username')
    role = session.get('role')

    # Restrict access to doctors only
    if role != 'doctor' and role != 'nurse':
        return redirect(url_for('index'))

    # Find the prescription to delete
    prescription = next((pres for pres in prescriptions if pres['id'] == prescription_id), None)
    if not prescription:
        return "Prescription not found", 404

    # Remove the prescription
    prescriptions.remove(prescription)

    flash("Prescription has been deleted successfully!", "success")
    return redirect(url_for('view_prescriptions'))

# -----------------------------------------------------------------------------------------------------------------

# ----------------------------- Doctor -----------------------------------------------------------------------
# Doctor MY Appointment
@app.route('/doctor/appointments', methods=['GET', 'POST'])
def doctor_appointments():
    doctor_id = session.get('id')
    role = session.get('role')
    current_date = datetime.now().strftime('%Y-%m-%d')
    username = session.get('username')
    search_start_date = request.args.get('search_start_date')  # Get the start date from the query params
    search_end_date = request.args.get('search_end_date')  # Get the end date from the query params

    if not doctor_id or role != 'doctor':
        return redirect(url_for('login'))

    doctor_id = int(doctor_id)
    
    # Fetch user based on role
    user = None
    if role == 'doctor':
        user = next((doc for doc in doctors if doc['username'] == username), None)
 
    # Filter appointments for the logged-in doctor
    filtered_appointments = [app for app in appointments if app.get('doctor_id') == doctor_id]

    # Ensure time format consistency by stripping leading/trailing spaces
    for app in filtered_appointments:
        app['time'] = app['time'].strip()  # Remove extra spaces
    
    # Sort appointments by date and time
    appointments_sorted = sorted(filtered_appointments, key=lambda x: (
        datetime.strptime(x['date'], '%Y-%m-%d'),
        convert_to_24hr_format(x['time'].split(' - ')[0])  # Get the start time and convert to 24-hour format
    ))

    # If a search date range is provided, filter appointments by the date range
    if search_start_date and search_end_date:
        appointments_sorted = [
            appt for appt in appointments_sorted
            if search_start_date <= appt['date'] <= search_end_date
        ]
    elif search_start_date:
        appointments_sorted = [appt for appt in appointments_sorted if appt['date'] >= search_start_date]
    elif search_end_date:
        appointments_sorted = [appt for appt in appointments_sorted if appt['date'] <= search_end_date]

    no_appointments_found = len(appointments_sorted) == 0

    # Retrieve current doctor user information
    user = next((doctor for doctor in doctors if doctor['username'] == username), None)

    # Debugging output
    for appointment in appointments_sorted:
        patient = next((p for p in patients if p['id'] == appointment['patient_id']), None)
        doctor = next((d for d in doctors if d['id'] == appointment.get('doctor_id')), None)

    # Pass patients to the template
    return render_template(
        'Doctor/doctor_appointments.html',
        user=user,
        role=role,
        username=username,
        appointments=appointments_sorted,  # Pass filtered appointments
        current_date=current_date,
        doctors=doctors,  # Pass the list of doctors to the template
        patients=patients,
        search_start_date=search_start_date,
        search_end_date=search_end_date,
        no_appointments_found=no_appointments_found  # Pass the list of patients to the template
    )
# -------------------------------------------------------------------------------------------------------------------------

# --------------------------------- Nurse --------------------------------------------------------------------------
# Nurse MY Appointment
@app.route('/nurse/appointments', methods=['GET', 'POST'])
def nurse_appointments():
    nurse_id = session.get('id')
    role = session.get('role')
    current_date = datetime.now().strftime('%Y-%m-%d')
    username = session.get('username')
    search_start_date = request.args.get('search_start_date')  # Get the start date from the query params
    search_end_date = request.args.get('search_end_date')  # Get the end date from the query params
    
    if not nurse_id or role != 'nurse':
        return redirect(url_for('login'))

    nurse_id = int(nurse_id)
    
    # Fetch user based on role
    user = None
    if role == 'nurse':
        user = next((nurse for nurse in nurses if nurse['username'] == username), None)

    # Filter appointments for the logged-in nurse
    filtered_appointments = [app for app in appointments if app.get('nurse_id') == nurse_id]

    # Ensure time format consistency by stripping leading/trailing spaces
    for app in filtered_appointments:
        app['time'] = app['time'].strip()  # Remove extra spaces
    
    # Sort appointments by date and time
    appointments_sorted = sorted(filtered_appointments, key=lambda x: (
        datetime.strptime(x['date'], '%Y-%m-%d'),
        convert_to_24hr_format(x['time'].split(' - ')[0])  # Get the start time and convert to 24-hour format
    ))

    # If a search date range is provided, filter appointments by the date range
    if search_start_date and search_end_date:
        appointments_sorted = [
            appt for appt in appointments_sorted
            if search_start_date <= appt['date'] <= search_end_date
        ]
    elif search_start_date:
        appointments_sorted = [appt for appt in appointments_sorted if appt['date'] >= search_start_date]
    elif search_end_date:
        appointments_sorted = [appt for appt in appointments_sorted if appt['date'] <= search_end_date]

    no_appointments_found = len(appointments_sorted) == 0

    # Retrieve current nurse user information
    user = next((nurse for nurse in nurses if nurse['username'] == username), None)

     # Debugging output
    for appointment in appointments_sorted:
        patient = next((p for p in patients if p['id'] == appointment['patient_id']), None)
        nurse = next((d for d in nurses if d['id'] == appointment.get('nurse_id')), None)

    # Pass patients to the template
    return render_template(
        'Nurse/nurse_appointments.html',
        user=user,
        role=role,
        username=username,
        appointments=appointments_sorted,  # Pass filtered appointments
        current_date=current_date,
        nurses=nurses,  # Pass the list of nurses to the template
        patients=patients,  # Pass the list of patients to the template
        search_start_date=search_start_date,
        search_end_date=search_end_date,
        no_appointments_found=no_appointments_found
    )
# -------------------------------------------------------------------------------------------------------------------------

# ----------------------------- Admin ------------------------------------------------------------------------------
# ADMIN VIEW ALL PRESCRIPTIONS
@app.route('/admin_view_prescriptions')
def admin_view_prescriptions():
    role = session.get('role')
    username = session.get('username')
    # Check if user is logged in and authorized as admin
    if role != 'admin':
        return redirect(url_for('index'))  # Redirect unauthorized users

    # Get the logged-in admin user
    user = None
    if role == 'admin' and username == admin.get('username'):
        user = admin
    elif role == 'doctor':
        user = next((doc for doc in doctors if doc['username'] == username), None)
    elif role == 'nurse':
        user = next((nurse for nurse in nurses if nurse['username'] == username), None)
    elif role == 'patient':
        user = next((pat for pat in patients if pat['username'] == username), None)

    # Redirect if admin not found
    if not admin:
        return redirect(url_for('index'))

    # Get today's date
    today = datetime.now()
    today_str = today.strftime('%Y-%m-%d')
    
    # Get yesterday's date
    yesterday = today - timedelta(days=1)
    yesterday_str = yesterday.strftime('%Y-%m-%d')
    
    # Get the date for 7 days ago
    last_7_days = today - timedelta(days=7)
    last_7_days_str = last_7_days.strftime('%Y-%m-%d')

    # Determine if we're filtering for today, yesterday, or last 7 days
    filter_today = request.args.get('filter_today') == 'true'
    filter_yesterday = request.args.get('filter_yesterday') == 'true'
    filter_last_7_days = request.args.get('filter_last_7_days') == 'true'
    
    # Retrieve the patient's username from the query parameter (if provided)
    patient_username = request.args.get('patient_username')

    def matches_date_filter(date):
        """Check if the date matches any active filter."""
        return (
            (filter_today and date == today_str) or
            (filter_yesterday and date == yesterday_str) or
            (filter_last_7_days and date >= last_7_days_str)
        )

    # If no filters are selected, show all prescriptions
    if not (filter_today or filter_yesterday or filter_last_7_days):
        if patient_username:
            all_prescriptions = [
                pres for pres in prescriptions
                if pres.get('patient_username') == patient_username
            ]
        else:
            all_prescriptions = prescriptions
    else:
        # Apply filters
        if patient_username:
            all_prescriptions = [
                pres for pres in prescriptions
                if pres.get('patient_username') == patient_username and matches_date_filter(pres.get('date'))
            ]
        else:
            all_prescriptions = [
                pres for pres in prescriptions
                if matches_date_filter(pres.get('date'))
            ]

    # Render the prescriptions page
    return render_template(
        'Admin/admin_view_prescriptions.html',
        patients=patients,
        prescriptions=all_prescriptions,
        role=role,
        username=username,
        user=admin,
        medications=medications,
        prescription=None,
        selected_patient=patient_username,
        filter_today=filter_today,
        filter_yesterday=filter_yesterday,
        filter_last_7_days=filter_last_7_days  
    )

# Admin PRES SEARCH FUNCTION
@app.route('/admin_search_prescriptions', methods=['GET'])
def admin_search_prescriptions():
    username = session.get('username')
    role = session.get('role')

    # Check if user is logged in and authorized
    if role != 'admin':
        return redirect(url_for('index'))

    # Get the logged-in user
    user = None
    if role == 'admin' and username == admin.get('username'):
        user = admin
    elif role == 'doctor':
        user = next((doc for doc in doctors if doc['username'] == username), None)
    elif role == 'nurse':
        user = next((nurse for nurse in nurses if nurse['username'] == username), None)
    elif role == 'patient':
        user = next((pat for pat in patients if pat['username'] == username), None)

    if not admin:
        return redirect(url_for('index'))

    # Retrieve the search query from the URL parameters
    date_start = request.args.get('date_start', '').strip()
    date_end = request.args.get('date_end', '').strip()
    search_results = []

    # Filter prescriptions by date range
    if date_start and date_end:
        search_results = [
            pres for pres in prescriptions
            if pres.get('date') and date_start <= pres['date'] <= date_end
        ]

    # Render the template with the search results
    return render_template(
        'Admin/admin_view_prescriptions.html',
        search_results=search_results,
        date_start=date_start,
        date_end=date_end,
        role=role,
        username=username,
        user=admin,
        patients=patients,  # Pass additional required data
        prescriptions=[]  # Avoid template errors; no default prescriptions shown during search
    )

@app.route('/admin_toggle_payment_status', methods=['POST'])
def admin_toggle_payment_status():
    prescription_id = request.form.get('prescription_id')
    prescription = next((pres for pres in prescriptions if str(pres['id']) == prescription_id), None)

    if not prescription:
        flash("Prescription not found.", "error")
        return redirect(url_for('admin_view_prescriptions'))

    # Toggle the payment status
    prescription['is_paid'] = not prescription['is_paid']

    flash("Payment status updated successfully.", "success")
    return redirect(url_for('admin_view_prescriptions'))

@app.route('/admin/dashboard')
def admin_dashboard():
    username = session.get('username')
    role = session.get('role')  # Ensure role is stored in session or retrieved from the database
    if role != 'admin':
        return redirect(url_for('index'))  # Redirect to the index page if not logged in as admin
    
    user = None
    if role == 'admin' and username == admin.get('username'):
        user = admin
    elif role == 'doctor':
        user = next((doc for doc in doctors if doc['username'] == username), None)
    elif role == 'nurse':
        user = next((nurse for nurse in nurses if nurse['username'] == username), None)
    elif role == 'patient':
        user = next((pat for pat in patients if pat['username'] == username), None)

    # Calculate total counts for patients, doctors, and nurses
    total_patients = len(patients)
    total_doctors = len(doctors)
    total_nurses = len(nurses)

    # Mock prescriptions data
    prescriptions = [
        {"date": "2024-12-01", "total_price": 100},
        {"date": "2024-12-02", "total_price": 200},
        {"date": "2024-12-03", "total_price": 150},
    ]  

    # Extracting data for the chart
    labels = [item['date'] for item in prescriptions]  # Correctly access 'date' key
    total_prices = [item['total_price'] for item in prescriptions]

    chart_data = {
        "labels": labels,
        "total_prices": total_prices,
    }

    return render_template(
        'Admin/admin_dashboard.html', 
        user=user, 
        username=username, 
        doctors=doctors, 
        nurses=nurses, 
        total_patients=total_patients,  # Pass total patients
        total_doctors=total_doctors,    # Pass total doctors
        total_nurses=total_nurses,      # Pass total nurses
        chart_data=json.dumps(chart_data)
    )

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

   user = None
   if role == 'admin' and username == admin.get('username'):
        user = admin
   elif role == 'doctor':
        user = next((doc for doc in doctors if doc['username'] == username), None)
   elif role == 'nurse':
        user = next((nurse for nurse in nurses if nurse['username'] == username), None)
   elif role == 'patient':
        user = next((pat for pat in patients if pat['username'] == username), None)
 
   return render_template('Admin/admin_view_doctors.html', doctors=filtered_doctors, user=user,username=username, role=role)
    
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


    user = None
    if role == 'admin' and username == admin.get('username'):
        user = admin
    elif role == 'doctor':
        user = next((doc for doc in doctors if doc['username'] == username), None)
    elif role == 'nurse':
        user = next((nurse for nurse in nurses if nurse['username'] == username), None)
    elif role == 'patient':
        user = next((pat for pat in patients if pat['username'] == username), None)

    return render_template('Admin/admin_view_nurses.html', user=user, nurses=filtered_nurses, username=username, role=role)

# Delete Patient (Admin Only)
@app.route('/admin/patients/delete/<int:patient_id>', methods=['POST'])
def admin_delete_patient(patient_id):
    global patients
    patients = [pat for pat in patients if pat['id'] != patient_id]

    flash("Patient has been deleted successfully!", "success")
    return redirect(url_for('view_patients'))

# Delete Doctor (Admin Only)
@app.route('/admin/doctors/delete/<int:doctor_id>', methods=['POST'])
def admin_delete_doctor(doctor_id):
    global doctors
    doctors = [doc for doc in doctors if doc['id'] != doctor_id]

    flash("Doctor has been deleted successfully!", "success")
    return redirect(url_for('admin_view_doctors'))

# Delete Nurse (Admin Only)
@app.route('/admin/nurses/delete/<int:nurse_id>', methods=['POST'])
def admin_delete_nurse(nurse_id):
    global nurses
    nurses = [nurse for nurse in nurses if nurse['id'] != nurse_id]

    flash("Nurse has been deleted successfully!", "success")
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
            fee = request.form.get('fee')
            specialization = request.form.get('specialization')
            intro = request.form.get('intro')
            
              # Handle file upload
            if 'pimage' not in request.files:
                return render_template('Auth/register_team.html', message="Profile image is required.", error=True)
            
            file = request.files['pimage']

            # Check if any field is missing
            if not all([username, password, email, role, fee, contactNumber, specialization, intro]) or not file or not allowed_file(file.filename):
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
                'fee': fee,
                'specialization' :specialization,
                'intro': intro,
                'pimage': url_for('static', filename='uploads/' + filename)  # Store the image URL
            }

             # Add new team member to the respective list based on role
            if role == 'Doctor':
                doctors.append(new_team)
                # After successful registration, redirect to the doctor list view
                flash("Doctor has been registered successfully!", "success")
                return redirect(url_for('admin_view_doctors'))
            elif role == 'Nurse':
                nurses.append(new_team)
                # After successful registration, redirect to the nurse list view
                flash("Nurse has been registered successfully!", "success")
                return redirect(url_for('admin_view_nurses'))
        
        except BadRequestKeyError:
            return render_template('Admin/register_team.html', message="Bad request. Please try again.", error=True)
   
    return render_template('Admin/register_team.html')

# Admin Edit Doctor Information
@app.route('/admin/doctors/edit/<int:doctor_id>', methods=['GET', 'POST'])
def admin_edit_doctor(doctor_id):

    username = session.get('username')
    role = session.get('role')

    user = None
    if role == 'admin' and username == admin.get('username'):
        user = admin
    elif role == 'doctor':
        user = next((doc for doc in doctors if doc['username'] == username), None)
    elif role == 'nurse':
        user = next((nurse for nurse in nurses if nurse['username'] == username), None)
    elif role == 'patient':
        user = next((pat for pat in patients if pat['username'] == username), None)

    # Find the doctor to edit by their ID
    doctor_to_edit = next((doc for doc in doctors if doc['id'] == doctor_id), None)
    
    if not doctor_to_edit:
        return redirect(url_for('admin_view_doctors'))  # If doctor is not found, redirect back to the doctor list

    if request.method == 'POST':
        # Get the updated data from the form
        doctor_to_edit['username'] = request.form['username']
        doctor_to_edit['email'] = request.form['email']
        doctor_to_edit['fee'] = request.form['fee']
        doctor_to_edit['specialization'] = request.form['specialization']
        doctor_to_edit['contactNumber'] = request.form['contactNumber']
        doctor_to_edit['intro'] = request.form['intro']

        flash("Doctor has been updated successfully!", "success")
        return redirect(url_for('admin_view_doctors'))  # After editing, redirect back to the doctors list

    return render_template('Admin/admin_edit_doctor.html', doctor=doctor_to_edit, user=user, username=username, role=role)

# Admin Edit Nurse Information
@app.route('/admin/nurses/edit/<int:nurse_id>', methods=['GET', 'POST'])
def admin_edit_nurse(nurse_id):
   
    username = session.get('username')
    role = session.get('role')

    user = None
    if role == 'admin' and username == admin.get('username'):
        user = admin
    elif role == 'doctor':
        user = next((doc for doc in doctors if doc['username'] == username), None)
    elif role == 'nurse':
        user = next((nurse for nurse in nurses if nurse['username'] == username), None)
    elif role == 'patient':
        user = next((pat for pat in patients if pat['username'] == username), None)
    # Find the nurse to edit by their ID
    nurse_to_edit = next((nurse for nurse in nurses if nurse['id'] == nurse_id), None)

    if not nurse_to_edit:
        return redirect(url_for('admin_view_nurses'))  

    if request.method == 'POST':
        # Get the updated data from the form
        nurse_to_edit['username'] = request.form['username']
        nurse_to_edit['email'] = request.form['email']
        nurse_to_edit['fee'] = request.form['fee']
        nurse_to_edit['specialization'] = request.form['specialization']
        nurse_to_edit['contactNumber'] = request.form['contactNumber']
        nurse_to_edit['intro'] = request.form['intro']

        flash("Nurse has been updated successfully!", "success") 
        return redirect(url_for('admin_view_nurses'))  # After editing, redirect back to the nurses list

    return render_template('Admin/admin_edit_nurse.html', nurse=nurse_to_edit, user=user, username=username, role=role)

# Admin Edit Patient Information
@app.route('/admin/patients/edit/<int:patient_id>', methods=['GET', 'POST'])
def admin_edit_patient(patient_id):

    username = session.get('username')
    role = session.get('role')

    user = None
    if role == 'admin' and username == admin.get('username'):
        user = admin
    elif role == 'doctor':
        user = next((doc for doc in doctors if doc['username'] == username), None)
    elif role == 'nurse':
        user = next((nurse for nurse in nurses if nurse['username'] == username), None)
    elif role == 'patient':
        user = next((pat for pat in patients if pat['username'] == username), None)

    # Find the patient to edit by their ID
    patient_to_edit = next((pat for pat in patients if pat['id'] == patient_id), None)
    
    if not patient_to_edit:
        return redirect(url_for('view_patients'))  

    if request.method == 'POST':
        # Get the updated data from the form
        patient_to_edit['username'] = request.form['username']
        patient_to_edit['email'] = request.form['email']
        patient_to_edit['contactNumber'] = request.form['contactNumber']
        patient_to_edit['address'] = request.form['address']

        flash("Patient has been updated successfully!", "success")
        return redirect(url_for('view_patients'))  # After editing, redirect back to the patients list

    return render_template('Admin/admin_edit_patient.html', patient=patient_to_edit, user=user,role=role)

# Admin to View All Appointment
@app.route('/admin/appointments', methods=['GET', 'POST'])
def admin_appointments():
    search_start_date = request.args.get('search_start_date')  # Get the start date from the query params
    search_end_date = request.args.get('search_end_date')  # Get the end date from the query params

    # Sort appointments by date and time
    appointments_sorted = sorted(appointments, key=lambda x: (
        datetime.strptime(x['date'], '%Y-%m-%d'),
        convert_to_24hr_format(x['time'].split(' - ')[0])  # Get the start time and convert to 24-hour format
    ))

    # Filter appointments by date range if start and end date are provided
    if search_start_date and search_end_date:
        appointments_sorted = [
            appt for appt in appointments_sorted
            if search_start_date <= appt['date'] <= search_end_date
        ]

    no_appointments_found = len(appointments_sorted) == 0

    username = session.get('username')
    role = session.get('role')
    current_date = datetime.now().strftime('%Y-%m-%d')

    user = None
    if role == 'admin' and username == admin.get('username'):
        user = admin
    elif role == 'doctor':
        user = next((doc for doc in doctors if doc['username'] == username), None)
    elif role == 'nurse':
        user = next((nurse for nurse in nurses if nurse['username'] == username), None)
    elif role == 'patient':
        user = next((pat for pat in patients if pat['username'] == username), None)

    # Debugging output
    for appointment in appointments_sorted:
        patient = next((p for p in patients if p['id'] == appointment['patient_id']), None)
        doctor = next((d for d in doctors if d['id'] == appointment.get('doctor_id')), None)
        nurse = next((n for n in nurses if n['id'] == appointment.get('nurse_id')), None)

    return render_template('Admin/admin_appointments.html', appointments=appointments_sorted, username=username, current_date=current_date, user=user, doctors=doctors, nurses=nurses,patients=patients, role=role, search_start_date=search_start_date, search_end_date=search_end_date, no_appointments_found=no_appointments_found)

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
            if 'image' not in med or not med['image']:
                med['image'] = 'default.jpg'  # Assign default image if missing
        except (ValueError, TypeError) as e:
            print(f"Error formatting price {med['price']}: {e}")
            med['price'] = "0.00"  # Default value in case of error

    user = None
    if role == 'admin' and username == admin.get('username'):
        user = admin
    elif role == 'doctor':
        user = next((doc for doc in doctors if doc['username'] == username), None)
    elif role == 'nurse':
        user = next((nurse for nurse in nurses if nurse['username'] == username), None)
    elif role == 'patient':
        user = next((pat for pat in patients if pat['username'] == username), None)
    return render_template('Medication/view_stock.html', medications=medications, user=user, username=username, role=role)

# Add Medical To Stock
@app.route('/medication/add', methods=['GET', 'POST'])
def add_medication():
    username = session.get('username')
    role = session.get('role')

    # Identify the logged-in user
    user = None
    if role == 'admin' and username == admin.get('username'):
        user = admin
    elif role == 'doctor':
        user = next((doc for doc in doctors if doc['username'] == username), None)
    elif role == 'nurse':
        user = next((nurse for nurse in nurses if nurse['username'] == username), None)
    elif role == 'patient':
        user = next((pat for pat in patients if pat['username'] == username), None)

    if request.method == 'POST':
        # Process form data
        name = request.form['name']
        description = request.form['description']
        quantity = int(request.form['quantity'])
        price = float(request.form['price'])
        expiry_date = request.form['expiry_date']
        supplier = request.form['supplier']

        # Handle file upload
        file = request.files.get('image')  # Get the file from the form
        filename = None
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)  # Ensure the directory exists
            file.save(file_path)  # Save the file to the upload folder
        else:
            flash("Invalid file type! Please upload a valid image (png, jpg, jpeg, gif).", "error")

        # Add new medication to the list (or database)
        new_medication = {
            'id': len(medications) + 1,
            'name': name,
            'description': description,
            'quantity': quantity,
            'price': price,
            'expiry_date': expiry_date,
            'supplier': supplier,
            'image': filename,  # Store the filename for the uploaded image
        }
        medications.append(new_medication)

        flash("Medication has been added successfully!", "success")
        return redirect(url_for('view_medication'))

    return render_template('Medication/add_stock.html', medications=medications, user=user, username=username, role=role)


# Edit Medical Stock
@app.route('/medication/edit/<int:id>', methods=['GET', 'POST'])
def edit_medication(id):
    username = session.get('username')
    role = session.get('role')

    user = None
    if role == 'admin' and username == admin.get('username'):
        user = admin
    elif role == 'doctor':
        user = next((doc for doc in doctors if doc['username'] == username), None)
    elif role == 'nurse':
        user = next((nurse for nurse in nurses if nurse['username'] == username), None)
    elif role == 'patient':
        user = next((pat for pat in patients if pat['username'] == username), None)

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

        medication['name'] = request.form['name']
        medication['description'] = request.form['description']
        medication['quantity'] = int(request.form['quantity'])
        medication['price'] = float(request.form['price']) # Price Per Unit
        medication['expiry_date'] = request.form['expiry_date']
        medication['supplier'] = request.form['supplier']

        flash("Medication has been updated successfully!", "success")
        return redirect(url_for('view_medication'))

    return render_template('Medication/edit_stock.html', medication=medication, user=user, username=username, role=role)

# Delete Medical Stock
@app.route('/medication/delete/<int:id>')
def delete_medication(id):
    username = session.get('username')
    role = session.get('role')

    global medications
    medications = [med for med in medications if med['id'] != id]
    
    flash("Medication has been deleted successfully!", "success")
    return redirect(url_for('view_medication'))

# Admin/Nurse/Doctor View Patients List
@app.route('/view_patients', methods=['GET', 'POST'])
def view_patients():
    username = session.get('username')
    role = session.get('role')
    search_query = request.args.get('search', '').lower()

    user = None
    if role == 'admin' and username == admin.get('username'):
        user = admin
    elif role == 'doctor':
        user = next((doc for doc in doctors if doc['username'] == username), None)
    elif role == 'nurse':
        user = next((nurse for nurse in nurses if nurse['username'] == username), None)
    elif role == 'patient':
        user = next((pat for pat in patients if pat['username'] == username), None) 
    # Filter patients based on the search query
    filtered_patients = [
        patient for patient in patients 
        if search_query in patient['username'].lower() 
    ]

    return render_template('view_patients.html',username=username, user=user, patients=filtered_patients, role=role)

# View Patient Address
@app.route('/view_address/<int:patient_id>', methods=['GET'])
def view_address(patient_id):
    # Fetch the patient based on the ID
    patient = next((p for p in patients if p['id'] == patient_id), None)
    if patient:
        return jsonify({'address': patient['address']})
    return jsonify({'error': 'Patient not found'}), 404


if __name__ == '__main__':
    app.run(debug=True)
    #app.run(host="192.168.43.109")