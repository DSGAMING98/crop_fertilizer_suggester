# 🌾 Crop-Fertilizer Suggestion System  
### Smart agriculture & chemistry of fertilizers (Experiential Learning Project)

This project is a **Python + Streamlit** app that suggests suitable **fertilizers for a given crop and soil test report**, while **explaining the chemistry and agronomy logic** behind the recommendation.

It’s designed as an **experiential learning tool** for chemistry + agriculture:
- Students can tweak soil values (pH, NPK, EC, etc.)
- Instantly see **how recommendations change**
- Learn about **fertilizer types, nutrient chemistry, and soil health**

---

## 🧱 Tech Stack

- Python (>= 3.10 recommended)
- Streamlit (UI)
- scikit-learn (ML model for fertilizer prediction)
- pandas, numpy (data handling)
- joblib (saving model & preprocessor)

---

## 📂 Project Structure

```bash
crop_fertilizer_suggester/
│
├─ app/
│  └─ app.py                 # Main Streamlit app
│
├─ src/
│  ├─ __init__.py
│  ├─ config.py              # Paths, constants, fertilizer profiles
│  ├─ data_loader.py         # CSV loaders from /data
│  ├─ preprocess.py          # Scaler + encoder + input builder
│  ├─ soil_health_index.py   # Soil health index & explanations
│  ├─ fertilizer_rules.py    # Rule-based agronomy + chemistry logic
│  └─ recommendation_engine.py # Hybrid (rules + ML) suggestion engine
│
├─ data/
│  ├─ raw/                   # Optional: original soil / crop / fertilizer data
│  ├─ processed/             # Contains training_dataset.csv
│  └─ examples/              # Demo inputs for showcasing the app
│
├─ models/
│  ├─ trained_model.pkl      # ML classifier (created after training)
│  └─ scaler.pkl             # Preprocessor (scaler + one-hot encoder)
│
├─ .streamlit/
│  └─ config.toml            # App theme (colors, fonts)
│
├─ train_model.py            # Script to train the model
├─ requirements.txt          # Python dependencies
└─ README.md                 # This file
⚙️ Setup Instructions
1️⃣ Create & activate virtual environment (recommended)
From inside the crop_fertilizer_suggester folder:

bash
Copy code
# Create venv
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Activate (Mac / Linux)
source .venv/bin/activate
2️⃣ Install dependencies
bash
Copy code
pip install -r requirements.txt
📊 Preparing the training dataset
The ML model is trained from:

data/processed/training_dataset.csv

You must create this file manually (e.g., from your soil test data + recommended fertilizer labels).

Suggested column format
text
Copy code
pH
organic_carbon
nitrogen
phosphorus
potassium
soil_type
rainfall
temperature
ec
crop
recommended_fertilizer
Example (CSV):

csv
Copy code
pH,organic_carbon,nitrogen,phosphorus,potassium,soil_type,rainfall,temperature,ec,crop,recommended_fertilizer
6.5,0.8,80,25,150,Loam,800,28,0.6,Rice,Urea
7.2,0.6,40,12,70,Clay,600,26,0.8,Wheat,DAP
5.5,0.5,35,10,50,Sandy,900,27,0.5,Maize,NPK_17_17_17
Put this file at:

bash
Copy code
data/processed/training_dataset.csv
🧠 Training the Model
Once training_dataset.csv is ready:

bash
Copy code
# From project root:
python train_model.py
What this does:

Loads data/processed/training_dataset.csv

Splits into train/test

Fits the preprocessor (scaler + one-hot encoder)

Trains a RandomForestClassifier

Prints accuracy + classification report

Saves:

models/trained_model.pkl

models/scaler.pkl (full preprocessor object)

If these two files exist, the Streamlit app will automatically:

Use ML prediction (if available)

Also combine it with rule-based logic

If they don’t exist:

App will still run

It will fall back to rule-based fertilizer logic only

🖥️ Running the Streamlit App
From project root:

bash
Copy code
streamlit run app/app.py
Then open the URL shown in the terminal (usually http://localhost:8501).

🧪 How to Use the App (Student View)
Enter soil test values:

pH

Organic carbon %

Available N, P, K

Soil type

Rainfall, temperature, EC

Target crop

Click: “Get fertilizer suggestion”

Right side will show:

✅ Final recommended fertilizer (and whether it came from ML + rules or rules-only)

🌍 Soil Health Index (0–1) + category (Excellent / Good / Moderate / Poor)

📐 Rule-based logic (NPK status, pH band, reasons)

🤖 ML model insight (if trained)

🧬 Chemistry learn section explaining:

nitrogenous / phosphatic / potassic fertilizers

organic manures

biofertilizers

Students can:

Change pH, NPK, crop

Watch the recommendation and explanations change

Understand how soil chemistry connects to fertilizer choice

🧬 Chemistry / Agronomy Concepts Highlighted
Role of pH in nutrient availability

Interpretation of low / adequate / high N, P, K

Difference between:

Urea, ammonium sulphate (N sources)

DAP, SSP (P sources)

MOP (K source)

NPK complex fertilizers

FYM, vermicompost, biofertilizers

Concept of soil health index from multiple parameters

🚀 Future Extensions
Add more crops and localized fertilizer recommendations

Add cost optimization (cheapest fertilizer plan)

Visual graphs:

Soil health vs. time

Over-fertilization impact scenarios

Link to live soil test lab / sensor data

👨‍🏫 Educational Use
This project can be used as:

A lab experiment for students:

“What happens if soil is acidic and N is low?”

“What changes when you switch from Rice to Pulses?”

A mini-project for:

Chemistry of fertilizers

Environmental impact of over-fertilization

Smart agriculture & sustainability

⚠️ Disclaimer
This app gives generic, educational recommendations.
It is not a substitute for:

Local soil testing labs

Official fertilizer recommendation schedules

Certified agronomist advice