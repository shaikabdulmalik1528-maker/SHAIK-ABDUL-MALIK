# 🤟 Sign Language Learning & Assessment Platform

![Python](https://img.shields.io/badge/Python-3.12+-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?logo=fastapi)
![OpenCV](https://img.shields.io/badge/OpenCV-Computer%20Vision-green?logo=opencv)
![MediaPipe](https://img.shields.io/badge/MediaPipe-Hand%20Tracking-orange)
![License](https://img.shields.io/badge/License-MIT-blue)
![Status](https://img.shields.io/badge/Status-Active-success)

An AI-powered **Sign Language Learning & Assessment Platform** that leverages **Computer Vision**, **Machine Learning**, and **FastAPI** to recognize sign language gestures in real time. The platform is designed to help users learn, practice, and assess sign language through an interactive and scalable system.

> 🚀 Developed as part of the **Infosys Springboard AI Internship**.

---

# 📖 Project Overview

The Sign Language Learning & Assessment Platform combines **MediaPipe**, **OpenCV**, and **FastAPI** to detect hand landmarks, process gesture data, and provide AI-powered sign language predictions.

The project follows a **layered architecture**, separating the API, business logic, and AI modules to ensure scalability and maintainability.

---

# ✨ Features

- ✅ FastAPI REST API
- ✅ Health Check Endpoint
- ✅ Gesture Prediction Endpoint (Dummy Response)
- ✅ Swagger API Documentation
- ✅ Real-Time Webcam Hand Tracking
- ✅ MediaPipe Hand Landmark Detection
- ✅ 21 Hand Landmark Extraction
- ✅ JSON Landmark Export
- ✅ Dataset Analysis Tool
- ✅ CSV Report Generation
- ✅ Thumb–Index Distance Calculator
- 🔄 AI-based Gesture Recognition (Upcoming)
- 🔄 Learning & Assessment Dashboard (Upcoming)

---

# 🛠️ Tech Stack

## Backend
- FastAPI
- Uvicorn
- Pydantic

## Programming Language
- Python 3.12+

## Computer Vision
- OpenCV
- MediaPipe

## Data Processing
- NumPy
- Pandas

## Machine Learning
- TensorFlow *(Upcoming)*

## Version Control
- Git
- GitHub

---

# 🏗️ Project Architecture

```
Client (Web / Mobile)
          │
          ▼
     FastAPI Backend
          │
          ▼
   Gesture Service Layer
          │
          ▼
 Hand Tracking Module
          │
          ▼
 OpenCV + MediaPipe
          │
          ▼
 Machine Learning Model (Upcoming)
```

---

# 📂 Project Structure

```text
SignLanguagePlatform/
│
├── backend/
│   ├── app/
│   │   ├── ai/
│   │   │   └── hand_tracking/
│   │   │       ├── __init__.py
│   │   │       ├── camera.py
│   │   │       ├── detector.py
│   │   │       ├── hand_detector.py
│   │   │       ├── landmark_extractor.py
│   │   │       └── utils.py
│   │   │
│   │   ├── api/
│   │   │   ├── health.py
│   │   │   └── prediction.py
│   │   │
│   │   ├── schemas/
│   │   │   └── prediction.py
│   │   │
│   │   ├── services/
│   │   │   └── gesture_service.py
│   │   │
│   │   └── main.py
│   │
│   ├── requirements.txt
│   └── captures/
│
├── datasets/
├── frontend/        (Upcoming)
├── LICENSE
├── .gitignore
└── README.md
```

---

# 🚀 Getting Started

## 1. Clone the Repository

```bash
git clone https://github.com/YOUR_GITHUB_USERNAME/SignLanguagePlatform.git
```

---

## 2. Navigate to the Backend

```bash
cd SignLanguagePlatform/backend
```

---

## 3. Create a Virtual Environment

```bash
python -m venv venv
```

---

## 4. Activate the Virtual Environment

### Windows

```bash
venv\Scripts\activate
```

### Linux / macOS

```bash
source venv/bin/activate
```

---

## 5. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 6. Run the FastAPI Server

```bash
python -m uvicorn app.main:app --reload
```

The server will start at:

```
http://127.0.0.1:8000
```

---

# 📘 API Documentation

FastAPI automatically generates interactive API documentation.

Swagger UI

```
http://127.0.0.1:8000/docs
```

ReDoc

```
http://127.0.0.1:8000/redoc
```

---

# 📡 API Endpoints

## Health Check

```
GET /health
```

Example Response

```json
{
  "status": "running",
  "message": "Backend is working correctly"
}
```

---

## Prediction API

```
GET /predict
```

Example Response

```json
{
  "prediction": "Hello",
  "confidence": 0.98,
  "processing_time": 0.012
}
```

---

# 📊 Dataset Analysis

Run the dataset analysis script:

```bash
python dataset_analysis.py
```

Output:

- Dataset Statistics
- CSV Report Generation
- Data Summary

---

# 🎮 Keyboard Controls

| Key | Action |
|------|--------|
| **P** | Print Hand Landmarks |
| **S** | Save Landmark JSON |
| **Q** | Quit Application |

---

# 📈 Current Progress

- ✅ Project Initialization
- ✅ FastAPI Backend Setup
- ✅ Health API
- ✅ Prediction API
- ✅ Swagger Documentation
- ✅ MediaPipe Hand Detection
- ✅ Webcam Integration
- ✅ Hand Landmark Extraction
- ✅ JSON Landmark Export
- ✅ Dataset Analysis
- ✅ CSV Report Generation
- ✅ Thumb–Index Distance Calculator
- ✅ AI Module Refactoring
- 🔄 Gesture Classification
- 🔄 Model Training
- 🔄 Learning Dashboard
- 🔄 User Authentication
- 🔄 Deployment

---

# 🛣️ Future Roadmap

- AI Gesture Classification
- ASL Alphabet Recognition
- Dynamic Word Recognition
- Sentence Prediction
- Voice Output
- User Authentication
- Progress Tracking Dashboard
- Learning Modules
- Assessment & Quiz System
- Performance Analytics
- Cloud Deployment
- Mobile Application Support

---

# 📸 Screenshots

> Add screenshots as your project progresses.




### Real-Time Hand Tracking

```
screenshots/webcam_demo.png
```

### Swagger Documentation

```
screenshots/swagger_ui.png
```

### Dataset Analysis

```
screenshots/dataset_analysis.png
```

### JSON Landmark Output

```
screenshots/json_output.png
```

---

# 🤝 Contributing

Contributions are welcome.

1. Fork the repository.
2. Create a feature branch.
3. Commit your changes.
4. Push the branch.
5. Open a Pull Request.

---

# 👨‍💻 Author

**Shaik Abdul Malik**

🎓 Final Year B.Tech Student

💻 AI | Computer Vision | Full Stack Development

🔗 GitHub: https://github.com/shaikabdulmalik1528-maker

---

# 📄 License

This project is licensed under the **MIT License**.

See the `LICENSE` file for more information.

---

# ⭐ Support

If you found this project helpful, consider giving it a ⭐ on GitHub.

Your support helps motivate future improvements and development.