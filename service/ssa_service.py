import pandas as pd
import numpy as np
import json
import joblib
from pathlib import Path
from datetime import datetime, timezone
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.cluster import KMeans
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score, confusion_matrix, classification_report
from backend.models.db import get_conn


class SSAService:
    """
    Space Situational Awareness (SSA) Analysis Service
    This class analyzes the behaviors and purposes of satellites using raw TLE data.
    """

    def __init__(self):
        self.model_path = Path("data/ssa_model.joblib")
        self.data_path = Path("data/ucs_database.csv")
        self.metrics_path = Path("data/ssa_metrics.json")
        self.model = None
        self.kmeans = None
        self.iso_forest = None
        self.label_encoder = LabelEncoder()  # Converts categorical data to numerical data
        self.scaler = StandardScaler()  # Scales data to standard normal distribution (mean 0, std 1)

        """
        Problem: There are thousands of active/passive objects in space. By looking at their raw orbital
        parameters (TLE), our main problem is to predict for what purpose (Communication, Observation, etc.)
        they are used and to detect those that move abnormally (anomalies).
        """

        # Orbit regime labels
        self.REGIME_MAP = {
            0: "LEO - Low Earth Orbit (High Traffic)",
            1: "MEO - Medium Earth Orbit (Navigation)",
            2: "GEO - Geostationary (Communication Belt)",
            3: "HEO - Highly Elliptical (Strategic)",
            4: "VLEO - Very Low Earth Orbit"
        }

    def parse_bstar(self, line1):
        """
        Parses the B* (BSTAR) drag coefficient from TLE Line 1.
        This value shows how much the satellite is affected by atmospheric drag.
        """
        try:
            # Boşlukları temizle ve formatı düzelt (Örn: " 12345-3" -> "0.12345e-3")
            bstar_str = line1[53:61].strip()
            if not bstar_str: return 0.0

            # Eğer sonda işaret varsa (-3, +2 gibi) onu ayır
            sign_pos = -2
            mantissa = bstar_str[:sign_pos].strip()
            exponent = bstar_str[sign_pos:].strip()

            val = f"0.{mantissa}e{exponent}"
            return float(val)
        except:
            return 0.0

    def train_model(self):
        """
        Source: Union of Concerned Scientists (UCS) Satellite Dataset.
        This dataset contains technical (mass, power, launch date), orbital (apogee, perigee, inclination, orbit type),
        and operational (country, operator, purpose) information for about 7,500 active satellites in Earth's orbit,
        making it a comprehensive dataset suitable for analyzing the distribution and usage of space assets.
        https://www.kaggle.com/datasets/mexwell/ucs-satellite-database/data
        """
        if not self.data_path.exists():
            return "Error: Dataset not found."

        try:
            # Preprocessing
            # Cleans numerical errors, punctuation mistakes, and missing values in the raw data.
            df = pd.read_csv(self.data_path, sep=';', on_bad_lines='skip', low_memory=False, encoding='latin-1')
            df.columns = [c.strip() for c in df.columns]

            # Make column names more manageable (Mapping)
            mapping = {
                'Purpose': 'Purpose',
                'Inclination (degrees)': 'Inclination',
                'Eccentricity': 'Eccentricity',
                'Period (minutes)': 'Period_minutes',
                'Perigee (km)': 'Perigee',
                'Apogee (km)': 'Apogee'
            }
            df = df.rename(columns=mapping)

            # Feature Selection, the 5 most explanatory physical parameters
            # The most effective physical parameters for determining satellite purpose are selected:
            # Inclination, Eccentricity, Period, and Altitude values.
            features = ['Inclination', 'Eccentricity', 'Period_minutes', 'Perigee', 'Apogee']


            for col in features:
                # Convert commas to dots and cast to numeric type in the dataset
                df[col] = df[col].astype(str).str.replace(',', '').str.replace('"', '')
                df[col] = pd.to_numeric(df[col], errors='coerce')

            # Clean missing data (NaN) and label the target variable
            df = df[['Purpose'] + features].dropna()

            # For training stability, remove rare classes with only 1 example
            df = df[df.groupby('Purpose')['Purpose'].transform('count') > 1]

            X = df[features]  # Girdi özellikleri
            y = self.label_encoder.fit_transform(df['Purpose'].astype(str))  # Hedef değişken

            # Random Forest algorithm is used - 80% Training, 20% Test
            # In this problem, the relationship between satellite purposes (categorical target) and orbital parameters (numerical inputs)
            # may not be linear. For example, spy satellites and meteorological satellites may be at similar altitudes (LEO)
            # but have different inclinations. Random Forest successfully models these complex decision trees.
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
            self.model = RandomForestClassifier(n_estimators=200, class_weight='balanced', random_state=42)
            self.model.fit(X_train, y_train)

            # Performance Metrics
            y_pred = self.model.predict(X_test)
            y_prob = self.model.predict_proba(X_test)

            try:
                # Multi-class ROC-AUC score
                roc_auc = roc_auc_score(y_test, y_prob, multi_class='ovr', average='weighted')
            except:
                roc_auc = 0.0

            metrics = {
                "accuracy": accuracy_score(y_test, y_pred),  # Overall accuracy rate
                "f1_score": f1_score(y_test, y_pred, average='weighted'),  # Sensitivity metric for imbalanced classes
                "roc_auc": roc_auc,
                "confusion_matrix": confusion_matrix(y_test, y_pred).tolist(),
                "classes": self.label_encoder.classes_.tolist(),
                "feature_importance": dict(zip(features, self.model.feature_importances_.tolist())),  # Which feature is more important?
                "classification_report": classification_report(y_test, y_pred, output_dict=True),  # Detailed report
                "sample_size": len(df),
                "timestamp": datetime.now().isoformat()
            }

            # Save metrics to JSON file
            with open(self.metrics_path, "w") as f:
                json.dump(metrics, f)

            # Clustering (K-Means) and Anomaly Detection (Isolation Forest)
            # Scale the data, group satellites, and catch outliers.
            kmeans = KMeans(n_clusters=5, random_state=42).fit(self.scaler.fit_transform(X))
            iso_forest = IsolationForest(contamination=0.03, random_state=42).fit(self.scaler.transform(X))

            # Save models to disk
            joblib.dump((self.model, self.label_encoder, self.scaler, kmeans, iso_forest), self.model_path)
            return f"Model Trained Successfully. Accuracy: %{metrics['accuracy'] * 100:.1f}"

        except Exception as e:
            return f"Training Error: {str(e)}"

    def analyze_all_satellites(self):
        """
        Analyze live TLE data using trained models.
        """
        if self.model is None or self.kmeans is None or self.iso_forest is None:
            if self.model_path.exists():
                try:
                    loaded_data = joblib.load(self.model_path)
                    self.model, self.label_encoder, self.scaler, self.kmeans, self.iso_forest = loaded_data
                    print(">>> Models successfully loaded from disk.")
                except Exception as e:
                    print(f">>> Error loading models: {e}")
                    return 0
            else:
                print(">>> ERROR: Model file not found! Please run /ssa/train first.")
                return 0

        if self.model is None:
            return 0

        # Create country lookup table
        ucs_df = pd.read_csv(self.data_path, sep=';', on_bad_lines='skip', low_memory=False, encoding='latin-1')
        ucs_df.columns = [c.strip() for c in ucs_df.columns]

        # Make NORAD column numeric and strip spaces
        ucs_df['NORAD Number'] = pd.to_numeric(ucs_df['NORAD Number'], errors='coerce')
        country_lookup = ucs_df.dropna(subset=['NORAD Number']).set_index('NORAD Number')[
            'Country of Operator/Owner'].to_dict()

        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT id, sat_name, line1, line2 FROM raw_tles")
        rows = cur.fetchall()

        count = 0
        for sid, name, line1, line2 in rows:
            try:
                if not line2 or len(line2) < 69:
                    continue
                if not line2.startswith("2 "):
                    continue

                # Physical Parameters
                incl = float(line2[8:16])
                ecc = float("0." + line2[26:33].strip())
                mm = float(line2[52:63])  # Mean Motion: how many times the satellite orbits Earth in a day
                alt = ((398600.44 / ((mm * 2 * np.pi / 86400) ** 2)) ** (1 / 3)) - 6378.137
                bstar = self.parse_bstar(line1)

                # AI Predictions
                input_raw = np.array([[incl, ecc, 1440 / mm, alt, alt]])
                scaled = self.scaler.transform(input_raw)

                cat = self.label_encoder.inverse_transform(self.model.predict(input_raw))[0]
                conf = np.max(self.model.predict_proba(input_raw))
                cluster_id = int(self.kmeans.predict(scaled)[0])
                is_anomaly = 1 if self.iso_forest.predict(scaled)[0] == -1 else 0

                # ORBITAL DECAY RISK
                # Low altitude + High BSTAR = Critical Risk
                decay_risk = "LOW"
                if alt < 350 and bstar > 0.0005:  # Critical altitude threshold
                    decay_risk = "HIGH"
                elif alt < 400:
                    decay_risk = "MEDIUM"

                # COUNTRY INFO (Lookup)
                # Capture NORAD ID from TLE (Line 2: characters 3-7)
                # Convert ID from TLE to int
                norad_id = int(line2[2:7].strip())
                country = country_lookup.get(norad_id, "Unknown")

                cur.execute("""
                    UPDATE satellite_intelligence 
                    SET predicted_category=?, confidence=?, cluster_id=?, is_anomaly=?, 
                        predicted_country=?, decay_risk=?, predicted_at=?
                    WHERE sat_id=?
                """, (cat, float(conf), cluster_id, is_anomaly, country, decay_risk,
                      datetime.now(timezone.utc).isoformat(), sid))

                if cur.rowcount == 0:
                    cur.execute("""
                        INSERT INTO satellite_intelligence 
                        (sat_id, predicted_category, confidence, cluster_id, is_anomaly, predicted_country, decay_risk, predicted_at)
                        VALUES (?,?,?,?,?,?,?,?)
                    """, (sid, cat, float(conf), cluster_id, is_anomaly, country, decay_risk,
                          datetime.now(timezone.utc).isoformat()))

                count += 1
            except Exception as e:
                print(f"[SSA ERROR] {e}")
                continue

        conn.commit()
        conn.close()
        return count

    def get_metrics(self):
        if self.metrics_path.exists():
            with open(self.metrics_path, "r") as f: return json.load(f)
        return None

    def get_regime_heatmap_data(self):
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT line2 FROM raw_tles")
        data = []
        for row in cur.fetchall():
            try:
                line2 = row[0]
                incl = float(line2[8:16])
                mm = float(line2[52:63])
                alt = ((398600.44 / ((mm * 2 * np.pi / 86400) ** 2)) ** (1 / 3)) - 6378.137
                if 200 < alt < 40000:
                    data.append({"x": round(incl, 1), "y": round(alt, -1)})
            except:
                continue
        conn.close()
        return data


ssa_service = SSAService()
