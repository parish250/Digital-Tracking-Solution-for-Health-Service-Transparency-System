import React, { useState, useRef } from 'react';
import axios from 'axios';

// Configure axios with base URL
const api = axios.create({
  baseURL: 'http://localhost:8000', // Adjust this to your backend URL
});

function Scanner({ onScanComplete }) {
  const [scanning, setScanning] = useState(false);
  const [scanResult, setScanResult] = useState(null);
  const [error, setError] = useState('');
  const videoRef = useRef(null);
  const canvasRef = useRef(null);

  // Mock function to simulate QR code scanning
  // In a real application, you would use a library like jsQR or QuaggaJS
  const startScanning = () => {
    setScanning(true);
    setError('');
    
    // Simulate scanning process
    setTimeout(() => {
      // Generate a mock shipment ID
      const mockShipmentId = Math.floor(Math.random() * 10000) + 1000;
      const mockScanData = {
        shipmentId: `SHP-${mockShipmentId}`,
        location: 'Distribution Center',
        timestamp: new Date().toISOString(),
        status: 'arrived'
      };
      
      setScanResult(mockScanData);
      setScanning(false);
      
      // Notify parent component
      if (onScanComplete) {
        onScanComplete(mockScanData);
      }
    }, 2000);
  };

  // Handle scan submission to backend
  const submitScan = async () => {
    if (!scanResult) return;
    
    try {
      const response = await api.post(`/shipments/${scanResult.shipmentId}/scan`, {
        location: scanResult.location,
        status: scanResult.status,
        scanned_at: scanResult.timestamp
      });
      
      console.log('Scan submitted successfully:', response.data);
      setError('Scan submitted successfully!');
    } catch (err) {
      console.error('Error submitting scan:', err);
      setError('Error submitting scan. Please try again.');
    }
  };

  return (
    <div className="scanner">
      <h3>QR Code Scanner</h3>
      
      <div className="scanner-view">
        {scanning ? (
          <div className="scanner-active">
            <p>Scanning... Please point your camera at the QR code</p>
            <div className="scanner-animation"></div>
          </div>
        ) : scanResult ? (
          <div className="scan-result">
            <h4>Scan Result</h4>
            <p><strong>Shipment ID:</strong> {scanResult.shipmentId}</p>
            <p><strong>Location:</strong> {scanResult.location}</p>
            <p><strong>Status:</strong> {scanResult.status}</p>
            <p><strong>Timestamp:</strong> {new Date(scanResult.timestamp).toLocaleString()}</p>
          </div>
        ) : (
          <div className="scanner-inactive">
            <p>Click "Start Scanning" to scan a QR code</p>
          </div>
        )}
      </div>
      
      <div className="scanner-controls">
        {!scanning && !scanResult && (
          <button onClick={startScanning} className="scan-button">
            Start Scanning
          </button>
        )}
        
        {scanResult && (
          <div className="scan-actions">
            <button onClick={submitScan} className="submit-button">
              Submit Scan
            </button>
            <button onClick={() => setScanResult(null)} className="reset-button">
              Scan Another
            </button>
          </div>
        )}
      </div>
      
      {error && (
        <div className={`message ${error.includes('Error') ? 'error' : 'success'}`}>
          {error}
        </div>
      )}
      
      {/* Hidden video and canvas elements for actual QR scanning */}
      <video ref={videoRef} style={{ display: 'none' }} />
      <canvas ref={canvasRef} style={{ display: 'none' }} />
    </div>
  );
}

export default Scanner;