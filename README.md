# 🤖 Intrabot-AI

**Intrabot-AI** is an **offline-first organizational chatbot** designed to answer employee queries by retrieving information from secure internal databases. It ensures **data privacy, security, and reliability** by running completely offline. When offline data is insufficient, it can **fallback to Google Gemini API** for extended answers.

---

## 🚀 Features

- **Offline-First** → Retrieves answers from local knowledge base (ChromaDB + embeddings)
- **Role-Based Access** → Employees, HR, IT, and Admins see only what they are authorized to view
- **Gemini Fallback** → When the local database lacks answers, Gemini API provides extended support
- **Secure & Private** → No sensitive organizational data is sent outside unless explicitly needed
- **Lightweight & Fast** → Works without internet dependency
- **Custom Chat UI** → User-friendly interface for employees

---

## 🛠️ Tech Stack

- **Frontend:** React / Streamlit (Chatbox UI)
- **Backend:** FastAPI (Python)
- **Vector DB:** ChromaDB
- **Embeddings:** all-MiniLM-L6-v2 (Sentence Transformers)
- **LLM (Offline):** GPT4All / LLaMA (optional)
- **Fallback Model:** Google Gemini (`gemini-pro`)

---

## 📂 Project Structure

```
Intrabot-AI/
├── frontend/                    # React/Streamlit UI
├── offline-org-chatbot/         # Core chatbot logic
├── src/                        # Source code modules
├── venv/                       # Virtual environment
├── api.py                      # FastAPI backend
├── gemini_client.py            # Google Gemini integration
├── rbac.py                     # Role-based access control
├── retrieval.py                # Document retrieval logic
├── requirements.txt            # Dependencies
├── .gitignore                  # Git ignore rules
└── README.md                   # Documentation
```

---

## ⚡ Setup & Installation

### 1. Clone the repository
```bash
git clone https://github.com/Adesh2204/Intrabot-AI.git
cd Intrabot-AI
```

### 2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate    # Mac/Linux
venv\Scripts\activate      # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set environment variables
Create a `.env` file and add:
```bash
GEMINI_API_KEY=your_api_key_here
```

### 5. Start the application

#### Backend Server
```bash
python api.py
# or
uvicorn api:app --reload
```

#### Frontend (if using Streamlit)
```bash
streamlit run frontend/app.py
```

#### Frontend (if using React)
```bash
cd frontend
npm install
npm start
```

---

## 🎯 Usage

1. **Open the chat UI**
2. **Ask questions like:**
   - "How do I apply for leave?" → (Offline HR docs answer)
   - "Write a leave application draft" → (Gemini fallback answer)
   - "How do I reset my office email password?" → (Offline IT docs answer)
3. **Role-based responses** based on your access level

---

## 📸 Screenshots

### 🔹 Chatbot Interface
![Intrabot-AI Interface](https://github.com/Adesh2204/Intrabot-AI/blob/main/image.png)

*Showcasing the clean, user-friendly chat interface*

---

## 🌟 Future Enhancements

- **Multilingual support** (Hindi, Spanish, etc.)
- **Voice-enabled chatbot** with speech recognition
- **Analytics dashboard** for admins to track usage
- **Integration** with Slack, MS Teams, and ERP systems
- **Mobile app** for on-the-go access
- **Advanced RBAC** with department-wise permissions

---

## 🤝 Contributing

1. Fork the project
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📜 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Authors

- **Adesh2204** - *Lead Developer* - [@Adesh2204](https://github.com/Adesh2204)
- **Team Intrabot-AI** - *Hackathon 2025*

---

## 🏆 Acknowledgments

- Developed during **Hackathon 2025**
- Inspired by the need for secure, offline-first enterprise chatbots
- Thanks to the open-source community for amazing tools and libraries

---

## 🚨 Security & Privacy

- **Data Privacy**: All organizational data stays on-premises
- **Secure by Design**: No external data transmission unless explicitly needed
- **Role-Based Access**: Users only see information they're authorized to access
- **Audit Trail**: All interactions are logged for compliance

Built with ❤️ for secure enterprise communication
