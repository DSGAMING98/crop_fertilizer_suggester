# 🧪 Chemistry of Fertilizers – Notes for Crop-Fertilizer Suggestion System

This document links the **chemistry of fertilizers** with the logic used in the  
**Crop-Fertilizer Suggestion System (Streamlit app)**.

It’s meant for:
- Experiential learning write-up
- Viva / presentation explanation
- Report theory section

---

## 1. Why fertilizers are needed

Plants need essential nutrients for growth:
- **Macronutrients:** N, P, K (major), plus Ca, Mg, S
- **Micronutrients:** Fe, Zn, Cu, Mn, B, Mo, Cl etc.

Natural soil may not supply enough of these in available form, so we add:
- **Mineral fertilizers** (chemical fertilizers)
- **Organic manures**
- **Biofertilizers**

The app focuses mainly on **N, P, K** + basic soil parameters (pH, EC, organic C).

---

## 2. Nitrogenous fertilizers (N fertilizers)

### 2.1 Urea – CO(NH₂)₂

- Contains **46% nitrogen** (very concentrated N source).
- In soil, urea undergoes **hydrolysis**:
  
  - Urea → ammonium carbonate → ammonium (NH₄⁺) → nitrate (NO₃⁻)
- Microorganisms and urease enzyme speed up this conversion.
- Excess surface-applied urea, especially on alkaline soil, can lose N as **ammonia gas (NH₃)**.

**Role in app:**
- Suggested when **soil nitrogen is low** or crop has **high N requirement** (e.g. rice, sugarcane).
- App mentions:
  - Split application
  - Incorporation into soil / irrigation after application
  - Avoiding overuse to prevent environmental losses.

---

### 2.2 Ammonium sulphate – (NH₄)₂SO₄

- Contains ~**21% N** and **24% S**.
- N present as ammonium (NH₄⁺).
- **Acid-forming fertilizer**:
  - Long-term use can lower soil pH.
- Useful for:
  - **Sulphur-deficient soils**
  - Some neutral to alkaline soils (with management).

**Role in app:**
- Suggested as an option when N is low, especially where:
  - Extra sulphur is helpful.
  - Slight acidification is acceptable along with liming/organics.

---

## 3. Phosphatic fertilizers (P fertilizers)

Plants take up P mainly as **H₂PO₄⁻** or **HPO₄²⁻** ions.  
P is crucial for:
- Root growth
- Energy transfer (ATP, ADP)
- Early crop establishment

### 3.1 DAP – Diammonium phosphate (NH₄)₂HPO₄

- Contains around **18% N** and **46% P₂O₅**.
- Supplies both N and P.
- Slightly alkaline reaction near granule → can affect very acid soils.

**Role in app:**
- Recommended when **P is low**.
- Especially for:
  - Basal dose
  - Starter fertilizer for cereals, pulses, etc.
- App comments on:
  - Placement near root zone
  - Avoiding unnecessary extra P if soil already high in P.

---

### 3.2 SSP – Single superphosphate Ca(H₂PO₄)₂ + CaSO₄ + gypsum mix

- ~**16% P₂O₅**
- Also provides **calcium** and **sulphur**.
- Has a slightly **acidic effect**, suited for many **acid soils**.

**Role in app:**
- Recommended in:
  - Acid soils with low P
  - Situations where additional S and Ca are useful
- App highlights slow-release / balanced nature vs highly concentrated P sources.

---

## 4. Potassic fertilizers (K fertilizers)

Plants absorb potassium as **K⁺** ions.

K is important for:
- Osmotic regulation
- Stomatal opening & closing
- Drought and disease resistance
- Grain filling and quality

### 4.1 MOP – Muriate of potash (KCl)

- Contains about **60% K₂O**.
- Economical, widely used K source.
- Contains chloride (Cl⁻), which in excess may affect some sensitive crops/soils.

**Role in app:**
- Suggested when **available K is low**.
- Especially key for:
  - Sugarcane
  - Many vegetables
  - High-yield cereal systems

---

## 5. NPK complex fertilizers

Example: **NPK 17-17-17**, **NPK 20-20-0**, etc.

- Each granule contains **all three major nutrients** in fixed ratio.
- Easy for farmers to apply balanced dose.
- However, less flexible than applying N, P, K separately.

**Role in app:**
- Suggested mainly for:
  - **Vegetables** and other **nutrient-intensive crops**
  - Situations where **balanced NPK** is needed quickly
- App uses complex fertilizers for:
  - Easy “all-in-one” nutrient supply
  - Early growth stages where balanced nutrition is critical.

---

## 6. Organic manures

### 6.1 FYM – Farmyard manure

- Low nutrient % (e.g. ~0.5% N, 0.2% P, 0.5% K), but:
  - Improves **soil structure**
  - Increases **organic carbon**
  - Enhances **CEC (cation exchange capacity)**
  - Supports **microbial life**

### 6.2 Vermicompost

- Produced by earthworms.
- Slightly higher nutrients (~1–1.5% N etc.).
- Very good for:
  - Root health
  - Biological activity
  - Seedling / nursery stages

**Role in app:**
- Recommended when **organic carbon is low** or **soil health index is poor**.
- Often added alongside mineral fertilizers to:
  - Buffer pH changes
  - Improve long-term soil fertility
- For high-input crops (vegetables), vermicompost is highlighted as a **quality booster**.

---

## 7. Biofertilizers

Biofertilizers use **beneficial microorganisms** to improve nutrient availability.

Examples:
- **Rhizobium** for legumes → fixes atmospheric N
- **Azotobacter / Azospirillum** → free-living N fixers
- **PSB (Phosphate solubilising bacteria)** → make fixed P available

**Role in app:**
- Recommended especially for **pulses** and **legumes**:
  - Reduces need for heavy N fertilization
  - Improves sustainability
- App mentions their role in:
  - Seed treatment
  - Soil inoculation

---

## 8. Soil chemistry & pH effect

Soil **pH** affects:
- Solubility and availability of nutrients
- Activity of soil microorganisms
- Fixation or leaching of certain ions

General trends:
- **Acidic soils (low pH):**
  - P may get fixed by Fe/Al compounds
  - Some micronutrients (Fe, Mn, Al) may become toxic in excess
  - Liming is often recommended
- **Alkaline soils (high pH):**
  - P can get fixed with Ca (calcium phosphates)
  - Micronutrients like Fe, Zn become less available
  - Acid-forming fertilizers + organics help

**In the app:**
- pH is used to:
  - Choose between SSP vs DAP
  - Decide when to caution about nutrient fixation or imbalance
  - Generate **soil health index** messages and recommendations.

---

## 9. Soil Health Index (used in the app)

The app computes a **Soil Health Index (0–1)** using:
- pH
- Organic carbon
- Available N, P, K
- EC (salinity indicator)

Then categorizes as:
- Excellent
- Good
- Moderate
- Poor

This gives a **qualitative chemistry + fertility summary**:
- Low OC → need for organic matter
- High EC → salinity problem
- Low N/P/K → need for specific fertilizers

---

## 10. How the app connects all this chemistry

1. User inputs:
   - pH, OC, N, P, K, EC
   - Soil type, rainfall, temperature
   - Crop

2. Backend:
   - Calculates **Soil Health Index**
   - Classifies **N, P, K** as low / adequate / high
   - Uses **pH band** (acidic / neutral / alkaline)
   - Applies **rule-based agronomy logic**:
     - low N + rice → urea suggested
     - low P + pulses → DAP + biofertilizer emphasis
     - high P → warns about overuse
   - Optionally uses **ML model** (Random Forest) trained on historical data to pick the most likely fertilizer label.

3. App explanation:
   - Shows **final recommended fertilizer**
   - Explains **why**, in terms of:
     - NPK status
     - Soil pH
     - Crop type
     - Chemistry of selected fertilizer
   - Gives warnings/notes about:
     - Over-fertilization
     - Environmental impact
     - Need for local soil testing

---

## 11. Educational / experiential angle

Students can:
- Change only **pH** and watch how recommended P fertilizers change.
- Change **N value** and observe how urea recommendation increases or decreases.
- Switch between **Rice vs Pulses vs Vegetables** and see:
  - Different NPK + biofertilizer strategies
  - Different explanations based on crop demand.

This turns abstract concepts like:
- “NPK balance”
- “pH effect”
- “Organic vs inorganic sources”

into **live, interactive feedback**, making the **chemistry of fertilizers** much easier to understand and remember.
