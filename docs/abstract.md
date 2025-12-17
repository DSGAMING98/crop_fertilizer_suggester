# ABSTRACT

Modern agriculture increasingly relies on scientific management of soil and fertilizers to
maintain productivity while reducing environmental impact. However, for many learners,
the connection between **soil chemistry**, **fertilizer composition** and **crop response**
remains abstract and theoretical. This project, titled **“Crop-Fertilizer Suggestion System:
Smart Agriculture & Chemistry of Fertilizers”**, aims to convert these concepts into an
interactive, experiential learning tool.

The system is implemented using **Python** and **Streamlit**. Users input basic soil test
parameters such as **pH, organic carbon, available nitrogen (N), phosphorus (P),
potassium (K), electrical conductivity (EC)**, along with **soil type, rainfall, temperature
and target crop**. In the backend, the application first computes a **Soil Health Index**
by scoring pH, organic matter and NPK levels, and classifying the soil into categories such
as *Excellent, Good, Moderate* or *Poor*.

A **rule-based agronomy and chemistry engine** then interprets the NPK status and pH band
to suggest suitable fertilizers, such as **urea, DAP, SSP, MOP, NPK complexes, farmyard
manure, vermicompost and biofertilizers**, along with detailed explanations. These
explanations emphasize the underlying chemistry, including the roles of **ammonium, nitrate,
phosphate, potassium ions, organic matter** and the influence of soil pH on nutrient
availability. In addition, an optional **machine learning model** (Random Forest classifier),
trained on a labeled dataset, predicts the most likely fertilizer recommendation based on
past patterns. The final decision combines **rule-based logic and ML output**, and clearly
indicates the source (rules-only, ML-only, or ML + rules agreement).

The system therefore acts both as a **decision-support prototype** and as a **pedagogical
tool**. Students can vary soil parameters and crop type to immediately see how soil health,
fertilizer choice and explanatory chemistry change in response. This creates an effective
platform for **experiential learning in chemistry of fertilizers, soil science and smart
agriculture**, while also demonstrating the integration of **data science and web
technologies** in real-world agricultural problem solving.
