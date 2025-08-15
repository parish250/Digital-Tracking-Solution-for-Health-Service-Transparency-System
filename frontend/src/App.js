import React, { useState } from 'react';
import axios from 'axios';
import Scanner from './components/Scanner';
import Dashboard from './components/Dashboard';
import './App.css';

// Configure axios with base URL
const api = axios.create({
  baseURL: 'http://localhost:8000', // Adjust this to your backend URL
});

function App() {
  const [activeTab, setActiveTab] = useState('feedback');
  const [userRole, setUserRole] = useState('citizen'); // 'citizen', 'distributor', 'official'
  const [feedback, setFeedback] = useState({
    shipmentId: '',
    feedbackType: 'received',
    comment: '',
    anonymous: true
  });
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  // Handle feedback submission
  const handleFeedbackSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage('');
    
    try {
      const response = await api.post('/feedbacks/', {
        shipment_id: feedback.shipmentId,
        feedback_type: feedback.feedbackType,
        comment: feedback.comment,
        anonymous: feedback.anonymous
      });
      
      setMessage('Feedback submitted successfully!');
      setFeedback({
        shipmentId: '',
        feedbackType: 'received',
        comment: '',
        anonymous: true
      });
    } catch (error) {
      setMessage('Error submitting feedback: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  // Handle SMS feedback submission
  const handleSmsFeedback = async () => {
    // This would send an SMS to the backend webhook
    setMessage('SMS feedback would be sent to the system');
  };

  // Handle scan completion from Scanner component
  const handleScanComplete = (scanData) => {
    setMessage(`Shipment ${scanData.shipmentId} scanned successfully!`);
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Digital Aid Tracker</h1>
        <p>Transparent Food Aid Distribution</p>
        
        {/* Role selector for demo purposes */}
        <div className="role-selector">
          <label htmlFor="role">Select Role: </label>
          <select
            id="role"
            value={userRole}
            onChange={(e) => setUserRole(e.target.value)}
          >
            <option value="citizen">Citizen</option>
            <option value="distributor">Distributor</option>
            <option value="official">Official</option>
          </select>
        </div>
      </header>

      {userRole === 'official' ? (
        // Official Dashboard View
        <Dashboard />
      ) : (
        // Citizen and Distributor Views
        <>
          <nav className="App-nav">
            <button
              className={activeTab === 'feedback' ? 'active' : ''}
              onClick={() => setActiveTab('feedback')}
            >
              Submit Feedback
            </button>
            {userRole === 'distributor' && (
              <button
                className={activeTab === 'scan' ? 'active' : ''}
                onClick={() => setActiveTab('scan')}
              >
                Scan Shipment
              </button>
            )}
            <button
              className={activeTab === 'sms' ? 'active' : ''}
              onClick={() => setActiveTab('sms')}
            >
              SMS Feedback
            </button>
          </nav>

          <main className="App-main">
            {activeTab === 'feedback' && (
              <div className="feedback-form">
                <h2>Submit Feedback</h2>
                <form onSubmit={handleFeedbackSubmit}>
                  <div className="form-group">
                    <label htmlFor="shipmentId">Shipment ID:</label>
                    <input
                      type="text"
                      id="shipmentId"
                      value={feedback.shipmentId}
                      onChange={(e) => setFeedback({...feedback, shipmentId: e.target.value})}
                      placeholder="e.g., SHP-1234"
                      required
                    />
                  </div>

                  <div className="form-group">
                    <label htmlFor="feedbackType">Feedback Type:</label>
                    <select
                      id="feedbackType"
                      value={feedback.feedbackType}
                      onChange={(e) => setFeedback({...feedback, feedbackType: e.target.value})}
                    >
                      <option value="received">Received</option>
                      <option value="not received">Not Received</option>
                      <option value="delayed">Delayed</option>
                      <option value="damaged">Damaged</option>
                      <option value="insufficient quantity">Insufficient Quantity</option>
                      <option value="other">Other</option>
                    </select>
                  </div>

                  <div className="form-group">
                    <label htmlFor="comment">Comment:</label>
                    <textarea
                      id="comment"
                      value={feedback.comment}
                      onChange={(e) => setFeedback({...feedback, comment: e.target.value})}
                      placeholder="Please provide details about your experience..."
                      rows="4"
                      required
                    />
                  </div>

                  <div className="form-group">
                    <label>
                      <input
                        type="checkbox"
                        checked={feedback.anonymous}
                        onChange={(e) => setFeedback({...feedback, anonymous: e.target.checked})}
                      />
                      Submit anonymously
                    </label>
                  </div>

                  <button type="submit" disabled={loading}>
                    {loading ? 'Submitting...' : 'Submit Feedback'}
                  </button>
                </form>
              </div>
            )}

            {activeTab === 'scan' && userRole === 'distributor' && (
              <div className="scan-section">
                <h2>Scan Shipment QR Code</h2>
                <p>Use your device's camera to scan the QR code on the shipment</p>
                <Scanner onScanComplete={handleScanComplete} />
              </div>
            )}

            {activeTab === 'sms' && (
              <div className="sms-section">
                <h2>SMS Feedback</h2>
                <p>Send feedback via SMS to our system</p>
                
                <div className="sms-instructions">
                  <p>Send an SMS with the following format:</p>
                  <p><strong>FEEDBACK [Shipment ID] [Status/Issue] [Comment]</strong></p>
                  <p>Example: FEEDBACK SHP-1234 received Food arrived damaged</p>
                </div>
                
                <button onClick={handleSmsFeedback} className="sms-button">
                  Send SMS Feedback
                </button>
              </div>
            )}

            {message && (
              <div className={`message ${message.includes('Error') ? 'error' : 'success'}`}>
                {message}
              </div>
            )}
          </main>
        </>
      )}
    </div>
  );
}

export default App;