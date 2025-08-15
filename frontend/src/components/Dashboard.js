import React, { useState, useEffect } from 'react';
import axios from 'axios';

// Configure axios with base URL
const api = axios.create({
  baseURL: 'http://localhost:8000', // Adjust this to your backend URL
});

function Dashboard() {
  const [shipments, setShipments] = useState([]);
  const [feedbacks, setFeedbacks] = useState([]);
  const [fraudAlerts, setFraudAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  // Fetch data from backend
  useEffect(() => {
    const fetchData = async () => {
      try {
        // Fetch shipments
        const shipmentResponse = await api.get('/shipments/');
        setShipments(shipmentResponse.data);
        
        // Fetch feedbacks
        const feedbackResponse = await api.get('/feedbacks/');
        setFeedbacks(feedbackResponse.data);
        
        // In a real app, you would fetch fraud alerts from a dedicated endpoint
        // For now, we'll generate mock fraud alerts
        const mockFraudAlerts = shipmentResponse.data
          .filter(shipment => shipment.status === 'delayed')
          .map(shipment => ({
            id: `fraud-${shipment.id}`,
            shipmentId: shipment.id,
            message: `Shipment ${shipment.id} is delayed`,
            severity: 'warning'
          }));
        setFraudAlerts(mockFraudAlerts);
        
        setLoading(false);
      } catch (err) {
        console.error('Error fetching data:', err);
        setError('Error fetching data. Please try again.');
        setLoading(false);
      }
    };

    fetchData();
    
    // Set up polling for real-time updates
    const interval = setInterval(fetchData, 30000); // Refresh every 30 seconds
    
    return () => clearInterval(interval);
  }, []);

  // Calculate KPIs
  const totalShipments = shipments.length;
  const deliveredShipments = shipments.filter(s => s.status === 'delivered').length;
  const delayedShipments = shipments.filter(s => s.status === 'delayed').length;
  const issuesReported = feedbacks.filter(f => f.feedback_type !== 'received').length;
  
  const deliveryRate = totalShipments > 0 
    ? Math.round((deliveredShipments / totalShipments) * 100) 
    : 0;

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <h2>Food Aid Tracking Dashboard</h2>
        <p>Real-time monitoring of food aid distribution</p>
      </header>

      {loading && <div className="loading">Loading dashboard data...</div>}
      {error && <div className="error-message">{error}</div>}

      {!loading && !error && (
        <>
          {/* KPI Cards */}
          <div className="kpi-cards">
            <div className="kpi-card">
              <h3>{totalShipments}</h3>
              <p>Total Shipments</p>
            </div>
            <div className="kpi-card">
              <h3>{deliveryRate}%</h3>
              <p>Delivery Rate</p>
            </div>
            <div className="kpi-card">
              <h3>{delayedShipments}</h3>
              <p>Delayed Shipments</p>
            </div>
            <div className="kpi-card">
              <h3>{issuesReported}</h3>
              <p>Issues Reported</p>
            </div>
          </div>

          {/* Main Dashboard Content */}
          <div className="dashboard-content">
            <div className="dashboard-section">
              <h3>Recent Shipments</h3>
              <div className="shipments-table">
                <table>
                  <thead>
                    <tr>
                      <th>ID</th>
                      <th>Status</th>
                      <th>Origin</th>
                      <th>Destination</th>
                      <th>Items</th>
                    </tr>
                  </thead>
                  <tbody>
                    {shipments.slice(0, 10).map(shipment => (
                      <tr key={shipment.id}>
                        <td>{shipment.id}</td>
                        <td>
                          <span className={`status-badge status-${shipment.status}`}>
                            {shipment.status}
                          </span>
                        </td>
                        <td>{shipment.origin_id || 'N/A'}</td>
                        <td>{shipment.destination_id || 'N/A'}</td>
                        <td>{shipment.aid_item_id || 'N/A'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            <div className="dashboard-section">
              <h3>Fraud Alerts</h3>
              <div className="alerts-list">
                {fraudAlerts.length > 0 ? (
                  fraudAlerts.map(alert => (
                    <div key={alert.id} className={`alert alert-${alert.severity}`}>
                      <strong>{alert.shipmentId}:</strong> {alert.message}
                    </div>
                  ))
                ) : (
                  <p>No fraud alerts at this time</p>
                )}
              </div>
            </div>

            <div className="dashboard-section">
              <h3>Recent Feedback</h3>
              <div className="feedback-list">
                {feedbacks.slice(0, 5).map(feedback => (
                  <div key={feedback.id} className="feedback-item">
                    <p><strong>Type:</strong> {feedback.feedback_type}</p>
                    <p>{feedback.comment}</p>
                    <small>
                      Anonymous: {feedback.anonymous ? 'Yes' : 'No'} | 
                      Submitted: {new Date(feedback.submitted_at).toLocaleString()}
                    </small>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
}

export default Dashboard;