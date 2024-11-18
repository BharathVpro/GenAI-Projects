import React from 'react';
import './Dashboard.css'; // Import the associated CSS for styling

const Dashboard = () => {
  return (
    <div className="dashboard-container">
      <button className="close-button">×</button> {/* Close button */}
      <div className="dashboard-content">
        {/* Your dashboard content */}
      </div>
    </div>
  );
}

export default Dashboard;
