import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';

const BatteryDashboard = () => {
  const [batteryStatus, setBatteryStatus] = useState(null);
  const [batteryHistory, setBatteryHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const statusResponse = await axios.get('/api/battery/B1234/status');
        setBatteryStatus(statusResponse.data);

        const historyResponse = await axios.get('/api/battery/B1234/history');
        setBatteryHistory(historyResponse.data);
        setLoading(false);
      } catch (error) {
        console.error(error);
        setError('Failed to fetch battery data');
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div>
      <h1>Battery Dashboard</h1>
      {batteryStatus && (
        <div>
          <h2>Battery Status</h2>
          <p>Voltage: {batteryStatus.voltage}</p>
          <p>Current: {batteryStatus.current}</p>
          <p>Temperature: {batteryStatus.temperature}</p>
          <p>Capacity: {batteryStatus.capacity}</p>
          <p>Timestamp: {batteryStatus.timestamp}</p>
        </div>
      )}
      {batteryHistory.length > 0 && (
        <div>
          <h2>Battery History</h2>
          <LineChart width={500} height={300} data={batteryHistory}>
            <Line type="monotone" dataKey="voltage" stroke="#8884d8" activeDot={{ r: 8, fill: '#8884d8', stroke: '#fff', strokeWidth: 3 }} />
            <Line type="monotone" dataKey="current" stroke="#82ca9d" activeDot={{ r: 8, fill: '#82ca9d', stroke: '#fff', strokeWidth: 3 }} />
            <Line type="monotone" dataKey="temperature" stroke="#ffbb33" activeDot={{ r: 8, fill: '#ffbb33', stroke: '#fff', strokeWidth: 3 }} />
            <Line type="monotone" dataKey="capacity" stroke="#ff9900" activeDot={{ r: 8, fill: '#ff9900', stroke: '#fff', strokeWidth: 3 }} />
            <XAxis dataKey="timestamp" />
            <YAxis />
            <CartesianGrid strokeDasharray="3 3" />
            <Tooltip />
            <Legend />
          </LineChart>
        </div>
      )}
    </div>
  );
};

export default BatteryDashboard;