# 🩸 Modelo de Clasificación de Severidad de Anemia

Clasificación binaria de prioridad de casos de anemia en la región San Martín (Perú), utilizando modelos de Machine Learning con optimización de hiperparámetros mediante Optuna. El proyecto busca apoyar la toma de decisiones clínicas al identificar automáticamente los casos que requieren atención inmediata, contribuyendo a una gestión más eficiente de los recursos de salud pública en zonas con alta prevalencia de anemia infantil.

---

## 📋 Descripción

Este proyecto tiene como objetivo predecir si un paciente con anemia requiere **atención prioritaria** (anemia moderada o severa) o puede seguir un tratamiento estándar (anemia leve), a partir de variables clínicas, demográficas y geográficas.

La variable objetivo `TARGET_PRIORIDAD` se construye a partir del campo `GRADO_SEVERIDAD`:

| Grado Original | Clase |
|---|---|
| Leve (LEV) | 0 — No prioritario |
| Moderado (MOD) | 1 — Prioritario |
| Severo (SEV) | 1 — Prioritario |

---

## 📂 Estructura del Proyecto

```
├── model_severidad.ipynb   # Notebook principal con todo el pipeline
├── ANEMIA_DA.csv           # Dataset fuente (no incluido en el repo)
├── ANEMIA_diccionario.xlsx
├── deforestacion.ipynb     # Descripción 
└── README.md
```

---

## 🗃️ Dataset

El dataset `ANEMIA_DA.csv` contiene registros de pacientes con diagnóstico de anemia en la región San Martín, Perú. Las variables utilizadas como predictores son:

| Variable | Descripción |
|---|---|
| `EDAD_EN_DIAS` | Edad del paciente convertida a días (calculada desde `EDAD_REGISTRO` y `TIPO_EDAD`) |
| `ETNIA` | Etnia del paciente (agrupada en: Mestizo / Indígena) |
| `DIAGNOSTICO` | Diagnóstico clínico registrado |
| `CANTIDAD` | Hemoglobina u otro valor clínico cuantitativo |
| `ALTITUD_MSNM` | Altitud media de la provincia del paciente (en m.s.n.m.) |

> **Nota:** La altitud fue incorporada como variable de contexto geográfico mediante un maestro de altitudes por provincia.

---

## ⚙️ Pipeline

### 1. Preprocesamiento
- Normalización de texto (mayúsculas, tildes, espacios)
- Agrupación étnica: cualquier etnia distinta a "Mestizo" se clasifica como "Indígena"
- Conversión de edad a días (manejo de registros en años, meses y días)
- Merge con tabla maestra de altitud por provincia
- Codificación de variables categóricas con **One-Hot Encoding** (`ETNIA`, `DIAGNOSTICO`)

### 2. Manejo del Desbalanceo de Clases
Se evaluaron dos estrategias de remuestreo:
- **SMOTE** (Oversampling sintético)
- **RandomUnderSampler** (Submuestreo aleatorio)

### 3. Modelos Evaluados (Baseline)
Con validación cruzada estratificada (5-Fold):

| Modelo | Estrategia |
|---|---|
| Regresión Logística | Oversampling / Undersampling |
| XGBoost | Oversampling / Undersampling |
| LightGBM | Oversampling / Undersampling |

### 4. Optimización de Hiperparámetros con Optuna
Se realizó búsqueda bayesiana con **Optuna** para los dos mejores modelos:
- **LightGBM** — 100 trials, optimizando F1-Score
- **XGBoost** — hasta 30 trials, con penalización por clase (`scale_pos_weight`) ajustada al desbalanceo real del dataset

La métrica principal de optimización fue el **F1-Score** sobre el set de test.

---

## 📊 Métricas Monitoreadas

Durante la optimización se rastrearon las siguientes métricas por trial:
- **F1-Score** (métrica objetivo)
- **Precision**
- **Recall (Sensibilidad)**
- **AUC-ROC**

---

## 🛠️ Tecnologías y Librerías

```python
pandas, numpy, matplotlib, seaborn
scikit-learn
xgboost
lightgbm
imbalanced-learn (SMOTE, RandomUnderSampler)
optuna
```

---

## 🚀 Cómo Reproducir

1. Clona el repositorio:
   ```bash
   git clone https://github.com/tu-usuario/tu-repo.git
   cd tu-repo
   ```

2. Instala las dependencias:
   ```bash
   pip install pandas numpy matplotlib seaborn scikit-learn xgboost lightgbm imbalanced-learn optuna
   ```

3. Coloca el archivo `ANEMIA_DA.csv` en la raíz del proyecto.

4. Abre y ejecuta el notebook:
   ```bash
   jupyter notebook model_severidad.ipynb
   ```

---

## 📌 Notas Adicionales

- El parámetro `scale_pos_weight` en XGBoost fue calculado dinámicamente a partir del ratio real de clases en el set de entrenamiento, y luego explorado por Optuna en un rango de `[1.0, ratio × 1.2]`.
- La altitud media por provincia se incorporó como variable proxy del factor geográfico, conocido por su influencia en los valores normales de hemoglobina.

---


