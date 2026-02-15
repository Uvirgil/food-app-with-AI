Perfect, Virgil — îți pregătesc un **README.md optimizat special pentru GitHub**, cu structură profesionistă, badge‑uri, secțiuni clare și un stil care arată impecabil pe pagina repo‑ului.

Poți copia TOT conținutul de mai jos direct în `README.md`.

---

# 🍽️ Food Recognition App with AI  
**Aplicatie inteligenta care recunoaste mancarea din imagini, calculeaza automat caloriile si macronutrientii si salveaza istoricul utilizatorului.**

`https://img.shields.io/badge/Python-3.10+-blue`
`https://img.shields.io/badge/Streamlit-App-red`
`https://img.shields.io/badge/Status-Active-success`
`https://img.shields.io/badge/License-MIT-green`

---

## 📸 Descriere

Aceasta aplicatie foloseste un model AI pentru a analiza imagini cu mancare si a estima valorile nutritionale:

- calorii totale  
- proteine  
- carbohidrati  
- grasimi  

Utilizatorii se pot autentifica, iar fiecare analiza este salvata intr-un istoric personal.  
Aplicatia include filtre, vizualizare imagini si statistici.
🔑 Cerinte pentru AI
Aplicatia necesita o cheie API OpenAI pentru a putea analiza imaginile si a calcula valorile nutritionale.
Fara o cheie valida, functia de recunoastere a mancarii nu va functiona.
Cheia trebuie adaugata in fisierul api.txt din directorul principal al proiectului


---

## 🚀 Functionalitati

### 🔐 Autentificare
- sistem complet de login / signup  
- date salvate in `users.json`  
- fiecare utilizator are propriul istoric

### 🤖 Recunoastere mancare cu AI
- incarci o poza  
- AI identifica preparatul  
- calculeaza automat valorile nutritionale  
- salveaza totul in istoric

### 🧾 Istoric alimentar
- tabel cu toate analizele  
- filtre dupa nume si interval de date  
- imagini afisate la cerere  
- date salvate in `history.json`

### 📊 Grafice (optional)
- calorii pe zile  
- macronutrienti pe zile  
- verdict saptamanal  
- totaluri generale  
*(sectiunea poate fi activata sau comentata)*

---

## 📁 Structura proiectului

```
FOOD APP WITH AI/
app/
│
├── main.py
│
├── core/
│   ├── vision.py
│   ├── auth_manager.py
│   ├── history_manager.py
│   ├── calorie_settings.py
│
└── pages/
    ├── home_page.py
    ├── history_page.py
    ├── stats_page.py
    ├── profile_page.py
```

---

## 🛠️ Tehnologii folosite

- Python 3.10+
- Streamlit
- Pandas
- OpenAI API (sau model compatibil)
- JSON pentru stocare locala

---

## ▶️ Instalare si rulare

### 1. Cloneaza repository-ul

```
git clone https://github.com/<username>/<repo>.git
cd <repo>
```

### 2. Instaleaza dependintele

```
pip install -r requirements.txt
```

### 3. Adauga cheia API in `secret_key.py`

```
OPENAI_API_KEY = "xxxxxxxxxxxxxxxxxxxx"
```

### 4. Porneste aplicatia

```
streamlit run app.py
```

Aplicatia se va deschide automat in browser.

---

## 🔒 Securitate

- cheia API este citita din `api.txt`  
- nu o include in repository public  
- fisierele `.json` pot fi adaugate in `.gitignore` daca vrei sa pastrezi datele private

---

## 📦 Optional: versiune desktop

Aplicatia poate fi impachetata intr-un `.exe` folosind PyInstaller.

---

## 📱 Optional: versiune mobila

Aplicatia poate fi transformata intr-o aplicatie Android/iOS folosind:

- WebView wrapper  
- Flet  
- Flutter + backend Python  

---

## 🧩 Idei de extindere

- export CSV pentru istoric  
- grafice suplimentare  
- obiective zilnice  
- notificari  
- integrare cu smartwatch  

---