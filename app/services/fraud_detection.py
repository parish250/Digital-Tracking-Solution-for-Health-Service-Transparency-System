import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import pandas as pd
from typing import List, Tuple, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.food_aid import Shipment, ScanLog
from app.models.fraud_detection import FraudDetection


class FraudDetectionService:
    def __init__(self):
        # Initialize the isolation forest model for anomaly detection
        self.model = IsolationForest(
            contamination=0.1,  # Expected proportion of outliers
            random_state=42,
            n_estimators=100
        )
        self.scaler = StandardScaler()
        self.is_trained = False
        
    def extract_features(self, shipment: Shipment, db: Session) -> np.ndarray:
        """
        Extract features from shipment data for fraud detection
        """
        # Get scan logs for this shipment
        scan_logs = db.query(ScanLog).filter(ScanLog.shipment_id == shipment.id).all()
        
        # Feature extraction
        features = []
        
        # Number of scan logs
        features.append(len(scan_logs))
        
        # Time between scans (if multiple scans)
        if len(scan_logs) > 1:
            scan_times = [scan.scanned_at for scan in scan_logs]
            scan_times.sort()
            time_differences = [
                (scan_times[i+1] - scan_times[i]).total_seconds() 
                for i in range(len(scan_times)-1)
            ]
            avg_time_between_scans = np.mean(time_differences) if time_differences else 0
            features.append(avg_time_between_scans)
        else:
            features.append(0)
            
        # Geographic anomalies (distance between scan locations)
        if len(scan_logs) > 1:
            distances = []
            for i in range(len(scan_logs)-1):
                lat1, lon1 = scan_logs[i].latitude or 0, scan_logs[i].longitude or 0
                lat2, lon2 = scan_logs[i+1].latitude or 0, scan_logs[i+1].longitude or 0
                # Simple distance calculation (in practice, use haversine formula)
                distance = np.sqrt((lat2-lat1)**2 + (lon2-lon1)**2)
                distances.append(distance)
            avg_distance = np.mean(distances) if distances else 0
            features.append(avg_distance)
        else:
            features.append(0)
            
        # Shipment age (time since creation)
        if shipment.timestamp:
            age = (datetime.utcnow() - shipment.timestamp).total_seconds()
            features.append(age)
        else:
            features.append(0)
            
        # Status changes
        status_changes = len(set([scan.status for scan in scan_logs])) if scan_logs else 0
        features.append(status_changes)
        
        return np.array(features).reshape(1, -1)
    
    def train_model(self, shipments: List[Shipment], db: Session):
        """
        Train the fraud detection model on historical data
        """
        if not shipments:
            return
            
        # Extract features for all shipments
        features_list = []
        for shipment in shipments:
            features = self.extract_features(shipment, db)
            features_list.append(features.flatten())
            
        # Convert to numpy array
        X = np.array(features_list)
        
        # Handle case where we have insufficient data
        if len(X) < 2:
            return
            
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Train the model
        self.model.fit(X_scaled)
        self.is_trained = True
    
    def predict_fraud(self, shipment: Shipment, db: Session) -> Tuple[float, bool, str]:
        """
        Predict if a shipment is fraudulent
        Returns: (score, is_fraud, reason)
        """
        if not self.is_trained:
            # If not trained, use simple heuristics
            return self._simple_fraud_check(shipment, db)
            
        # Extract features
        features = self.extract_features(shipment, db)
        
        # Scale features
        features_scaled = self.scaler.transform(features)
        
        # Predict
        prediction = self.model.predict(features_scaled)[0]
        score = self.model.decision_function(features_scaled)[0]
        
        # Convert to probability (0-1)
        fraud_probability = (score * -1 + 0.5)  # Invert and shift
        fraud_probability = max(0, min(1, fraud_probability))  # Clamp to 0-1
        
        is_fraud = prediction == -1  # -1 indicates anomaly
        
        # Generate reason
        reason = self._generate_fraud_reason(shipment, db, fraud_probability)
        
        return (fraud_probability, is_fraud, reason)
    
    def _simple_fraud_check(self, shipment: Shipment, db: Session) -> Tuple[float, bool, str]:
        """
        Simple heuristic-based fraud detection for when model is not trained
        """
        score = 0.0
        reasons = []
        
        # Check for delayed shipments
        if shipment.timestamp:
            age = (datetime.utcnow() - shipment.timestamp).total_seconds()
            if age > 30 * 24 * 3600:  # More than 30 days old
                score += 0.3
                reasons.append("Shipment very old")
                
        # Check for unusual status
        if shipment.status and shipment.status.lower() in ['delayed', 'missing', 'issue']:
            score += 0.4
            reasons.append("Unusual status")
            
        # Check scan logs
        scan_logs = db.query(ScanLog).filter(ScanLog.shipment_id == shipment.id).all()
        if len(scan_logs) == 0:
            score += 0.2
            reasons.append("No scan logs")
        elif len(scan_logs) > 10:  # Too many scans
            score += 0.3
            reasons.append("Too many scan logs")
            
        is_fraud = score > 0.5
        reason = ", ".join(reasons) if reasons else "No anomalies detected"
        
        return (score, is_fraud, reason)
    
    def _generate_fraud_reason(self, shipment: Shipment, db: Session, score: float) -> str:
        """
        Generate a reason for fraud detection based on score and shipment data
        """
        if score > 0.8:
            return "High anomaly score - potential fraud detected"
        elif score > 0.5:
            return "Moderate anomaly score - requires review"
        else:
            return "Low anomaly score - likely legitimate"


# Global instance
fraud_detection_service = FraudDetectionService()