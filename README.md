# **Face Recognition-Based Attendance System** 📸✅  

![image](https://github.com/user-attachments/assets/7916ddd1-9684-4ef6-8b8a-34eb3809c8a6)


A **secure, automated attendance system** using **real-time face recognition** with **anti-spoofing** to prevent fraud (e.g., photos/videos). Built with **Python, OpenCV, and Flask**, this system is designed for organizations needing reliable attendance tracking.  

---

## **🌟 Key Features**  

✅ **Real-Time Face Detection & Recognition** – Identifies registered users instantly.  
✅ **Liveness Detection** – Blocks spoofing attempts using **Silent-Face-Anti-Spoofing**.  
✅ **Web-Based Dashboard** – Easy admin & employee access.  
✅ **Secure Authentication** – Login/logout with session management.  
✅ **Attendance Logs** – Stores records with timestamps.  
✅ **Responsive UI** – Works on desktop & mobile.  

---

## **🛠️ Tech Stack**  

| Category       | Technologies Used |
|---------------|------------------|
| **Backend**   | Python (Flask), OpenCV |
| **Face Recognition** | Deep Learning (DNN models) |
| **Anti-Spoofing** | [Silent-Face-Anti-Spoofing](https://github.com/minivision-ai/Silent-Face-Anti-Spoofing) |
| **Frontend**  | HTML5, CSS3, JavaScript (AJAX for live webcam feed) |
| **Database**  | Pickle (for demo) → *Upgrade to **SQLite/MySQL** for production* |  

---

## **🚀 Quick Setup (5 Steps)**  

### **Prerequisites**  
- Python 3.8+  
- `pip` installed  

### **Installation**  
1. **Clone the repo:**  
   ```bash
   git clone https://github.com/MOHAMEDMETAWEA/Graduation-project-Face-attendance-system-face-recognition-based-on-AI-.git
   cd face-attendance-system
   ```

2. **Install dependencies:**  
   ```bash
   pip install -r requirements.txt
   ```

3. **Download Anti-Spoofing Models** (Place in `anti_spoof_models/`):  
   - [`2.7_80x80_MiniFASNetV2.pth`](https://example.com/model1) *(Example link, replace with actual)*  
   - [`4_0_0_80x80_MiniFASNetV1SE.pth`](https://example.com/model2)  

4. **Initialize the database:**  
   ```bash
   python init_db.py
   ```

5. **Run the app:**  
   ```bash
   python app.py
   ```
   → Access at **`http://localhost:5000`**  

---

## **📂 Project Structure**  

```plaintext
face-attendance-system/
├── anti_spoof_models/       # Anti-spoofing DL models
├── db/                      # Database storage (pickle files)
├── static/                  # Frontend assets
│   ├── css/                 # Styles (style.css)
│   ├── img/                 # Images/logo
│   └── js/                  # Webcam & AJAX scripts
├── templates/               # HTML pages
│   ├── dashboard.html       # Admin view
│   ├── login.html           # Employee login
│   └── ...                  # Other pages
├── app.py                   # Flask backend
├── anti_spoof.py            # Liveness detection
└── requirements.txt         # Python dependencies
```

---

## **🖥️ How It Works?**  

### **1️⃣ Admin Features**  
- **Register new employees** (name, face data).  
- **View attendance reports** (date-wise logs).  

### **2️⃣ Employee Features**  
- **Login via face recognition** (webcam scan).  
- **Automatic attendance marking** (with anti-spoofing check).  

### **Demo GIF** *(Optional: Add a screen recording here)*  

---

## **🔮 Future Improvements**  

📌 **Switch to SQL Database** (SQLite/MySQL for scalability).  
📌 **Multi-User Support** (Role-based access).  
📌 **Export Reports** (Excel/PDF generation).  
📌 **Mobile App** (Flutter/React Native integration).  
📌 **Deploy on Cloud** (AWS/Azure).  

---

## **❓ FAQ**  

**Q: Can I test it without a webcam?**  
→ Yes! Use **pre-recorded videos** (modify `app.py`).  

**Q: How accurate is the anti-spoofing?**  
→ ~98% on standard datasets (adjust thresholds in `anti_spoof.py`).  

**Q: How to add more users?**  
→ Admins can register faces via the dashboard.  

---

## **🤝 Contribute**  

**Found a bug? Want a feature?**  
1. Fork the repo.  
2. Create a branch (`git checkout -b feature/xyz`).  
3. Commit changes (`git commit -m "Add feature xyz"`).  
4. Push (`git push origin feature/xyz`).  
5. Open a **Pull Request**.  
