# 📘 User Manual – Crop-Fertilizer Suggestion System

## 1. Overview

The **Crop-Fertilizer Suggestion System** is an interactive web application built using  
**Python + Streamlit**. It helps users:

- Enter **soil test values** and **crop name**
- Get a **fertilizer recommendation**
- Understand the **soil health** and **chemistry behind the decision**

The system is designed as an **experiential learning tool** for chemistry and agriculture.

---

## 2. System Requirements

### Hardware
- Any standard laptop/desktop that can run Python and a web browser.

### Software
- Python 3.10 or higher (recommended)
- pip (Python package manager)
- Web browser (Chrome, Edge, Firefox, etc.)

---

## 3. Installation & Setup

### Step 1: Extract / place the project

Place the folder `crop_fertilizer_suggester` anywhere on your system, e.g.:

```text
C:\Users\YourName\Desktop\crop_fertilizer_suggester
Step 2: Create and activate virtual environment (recommended)
Open a terminal / command prompt in the project folder:

bash
Copy code
cd crop_fertilizer_suggester

# Create virtual environment
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Activate (Mac / Linux)
source .venv/bin/activate
Step 3: Install dependencies
bash
Copy code
pip install -r requirements.txt
4. Data Files
The system uses CSV files stored inside the data folder.

Folder structure
text
Copy code
data/
├─ raw/
│  ├─ soil_samples_raw.csv
│  ├─ crop_requirements_raw.csv
│  └─ fertilizer_properties_raw.csv
├─ processed/
│  ├─ soil_processed.csv
│  ├─ crop_nutrient_needs.csv
│  ├─ fertilizer_db.csv
│  └─ training_dataset.csv
└─ examples/
   └─ demo_inputs.csv
The most important file for the ML model is:

data/processed/training_dataset.csv → used to train the classifier.

A sample of this file has columns like:

text
Copy code
pH, organic_carbon, nitrogen, phosphorus, potassium,
soil_type, rainfall, temperature, ec, crop, recommended_fertilizer
5. Training the ML Model (Optional but Recommended)
If you want the ML model to be active:

Ensure data/processed/training_dataset.csv exists.

Run this command from project root:

bash
Copy code
python train_model.py
What this script does:

Loads the training dataset

Splits into train/test

Fits preprocessor (scaler + encoder)

Trains a RandomForest classifier

Shows accuracy and classification report

Saves:

models/trained_model.pkl

models/scaler.pkl

If you skip this step:

The app still runs

It will rely only on the rule-based agronomy + chemistry logic

6. Running the Application
From the project root:

bash
Copy code
streamlit run app/app.py
If you face any import issues, you can also try:

bash
Copy code
python -m streamlit run app/app.py
After running this command:

Streamlit will show a local URL in the terminal, e.g.:

text
Copy code
Local URL: http://localhost:8501
Open that link in your web browser.

7. Using the Main Interface
Step 1: Input Section (Left side)
You will see fields like:

Soil pH

Organic Carbon (%)

Available Nitrogen (kg/ha)

Available Phosphorus (kg/ha)

Available Potassium (kg/ha)

Soil type (Loam / Clay / Sandy / etc.)

Seasonal rainfall (mm)

Average temperature (°C)

Electrical conductivity EC (dS/m)

Target crop (Rice, Wheat, Maize, Pulses, Vegetables, Sugarcane, etc.)

After entering these values, click:

“Get fertilizer suggestion”

Step 2: Output Section (Right side)
The right side shows multiple blocks:

Final Recommendation

Recommended fertilizer name (e.g. Urea, DAP, MOP, NPK_17_17_17)

Source of decision:

ML + Rules

Rules only

ML only

Detailed rationale explaining why that fertilizer was chosen.

Soil Health Overview

Soil Health Index (0–1)

Category: Excellent / Good / Moderate / Poor

Factor-wise explanations for:

pH

Organic carbon

Nitrogen

Phosphorus

Potassium

EC

Rule-based Fertilizer Logic

NPK status: low / adequate / high

pH band: acidic / neutral / alkaline

List of fertilizers with:

Nutrient composition

Agronomic reasons

ML Model Insight (if model is trained)

ML-predicted fertilizer label

Class probabilities for each fertilizer type

Chemistry Learn Section

Short notes about:

Nitrogenous, phosphatic, potassic fertilizers

Organic manures

Biofertilizers

How they relate to soil chemistry

8. Typical Use Cases
Case 1: Classroom / Lab experiment
Teacher gives a hypothetical soil test report.

Students enter values in the app.

They observe:

Soil health index

Changes in recommendation when N/P/K values are adjusted

Impact of pH on fertilizer choice.

Case 2: Comparison between crops
Keep soil values same.

Change crop from Rice to Pulses to Vegetables.

Observe:

Different fertilizer strategies

Emphasis on biofertilizers for pulses

Balanced NPK for vegetables.

Case 3: Effect of pH
Fix NPK at moderate levels.

Change pH from 5.0 → 7.0 → 8.5.

See how:

Soil Health Index changes

Fertilizer logic comments on acidic / alkaline soils

P-related recommendations differ.

9. Troubleshooting
9.1 ModuleNotFoundError: No module named 'src'
Make sure you are running from the project root.

Use:

bash
Copy code
streamlit run app/app.py
or:

bash
Copy code
python -m streamlit run app/app.py
Also ensure:

src/__init__.py exists.

The app file app/app.py has correct imports.

9.2 Port already in use
If port 8501 is already used:

Either close the previous Streamlit app

Or run on another port:

bash
Copy code
streamlit run app/app.py --server.port 8502
9.3 Blank / empty outputs
Check that you actually clicked “Get fertilizer suggestion”.

Verify your input values are numeric where required.

Make sure CSV files are inside the correct folders.

10. Educational Notes
This system is designed for learning, not for official agricultural advice.

Use it to understand:

How soil parameters drive fertilizer decisions

Role of chemistry in smart agriculture

For real-world field use, always:

Consult local soil testing labs

Follow official fertilizer recommendation guides

Talk to a qualified agronomist.
## 11. Credits

This project was collaboratively developed by:

- **Monish Kandanuru** – Coder  
- **Shanmukha Sai** – Coder  
- **Parameshwar Sahoo**  
- **Nandan Gowda**  
- **Mohumad Hashim**

### Project Focus:
- Smart Agriculture
- Chemistry of Fertilizers
- Soil Health Analysis
- Experiential Learning using Python & Streamlit

This work represents a team effort combining:
- Programming
- Soil science
- Fertilizer chemistry
- Data-driven decision making
