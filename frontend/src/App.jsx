import { useEffect, useState } from "react";
import "./App.css";
import Header from "./components/Header";

function App() {
  const [backendConnected, setBackendConnected] = useState(false);
  const [selectedTask, setSelectedTask] = useState("basic_delivery");

  const [observation, setObservation] = useState(null);
  const [stateData, setStateData] = useState(null);
  const [gradeData, setGradeData] = useState(null);

  const [selectedTruck, setSelectedTruck] = useState("T1");
  const [selectedOrder, setSelectedOrder] = useState("");

  const [stepResult, setStepResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const API_BASE = import.meta.env.VITE_API_BASE || "http://127.0.0.1:8000";

  useEffect(() => {
    checkBackend();
  }, []);

  const checkBackend = async () => {
    try {
      const res = await fetch(`${API_BASE}/health`);
      setBackendConnected(res.ok);
    } catch {
      setBackendConnected(false);
    }
  };

  const handleReset = async () => {
    try {
      setLoading(true);
      setStepResult(null);
      setGradeData(null);

      const res = await fetch(`${API_BASE}/reset?task_id=${selectedTask}`, {
        method: "POST",
      });

      const data = await res.json();
      setObservation(data);
      setStateData(null);

      if (data.available_orders?.length > 0) {
        setSelectedOrder(data.available_orders[0].id);
      } else {
        setSelectedOrder("");
      }
    } catch (err) {
      console.error(err);
      alert("Failed to reset environment.");
    } finally {
      setLoading(false);
    }
  };

  const handleStep = async () => {
    if (!selectedOrder) {
      alert("Select an order first.");
      return;
    }

    try {
      setLoading(true);

      const res = await fetch(`${API_BASE}/step`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          truck_id: selectedTruck,
          target_order_id: selectedOrder,
        }),
      });

      const data = await res.json();
      setStepResult(data);
      setObservation(data.observation);

      if (data.observation?.available_orders?.length > 0) {
        setSelectedOrder(data.observation.available_orders[0].id);
      } else {
        setSelectedOrder("");
      }
    } catch (err) {
      console.error(err);
      alert("Failed to execute step.");
    } finally {
      setLoading(false);
    }
  };

  const handleState = async () => {
    try {
      setLoading(true);
      const res = await fetch(`${API_BASE}/state`);
      const data = await res.json();
      setStateData(data);
    } catch (err) {
      console.error(err);
      alert("Failed to fetch state.");
    } finally {
      setLoading(false);
    }
  };

  const handleGrade = async () => {
    try {
      setLoading(true);
      const res = await fetch(`${API_BASE}/grade?task_id=${selectedTask}`);
      const data = await res.json();
      setGradeData(data);
    } catch (err) {
      console.error(err);
      alert("Failed to fetch grade.");
    } finally {
      setLoading(false);
    }
  };

  const trucks = observation?.trucks || [];
  const orders = observation?.available_orders || [];

  return (
    <div className="page">
      <div className="container">
        <Header backendConnected={backendConnected} />

        {/* TASKS */}
        <div className="panel">
          <h2>🎯 Benchmark Tasks</h2>
          <p className="panel-subtext">
            Choose one of the OpenEnv benchmark scenarios and reset the environment to start a new episode.
          </p>
          <div className="task-buttons">
            <button
              className={selectedTask === "basic_delivery" ? "active" : ""}
              onClick={() => setSelectedTask("basic_delivery")}
            >
              Basic Delivery
            </button>
            <button
              className={selectedTask === "fleet_balancing" ? "active" : ""}
              onClick={() => setSelectedTask("fleet_balancing")}
            >
              Fleet Balancing
            </button>
            <button
              className={selectedTask === "carbon_challenge" ? "active" : ""}
              onClick={() => setSelectedTask("carbon_challenge")}
            >
              Carbon Challenge
            </button>
          </div>
        </div>

        {/* CONTROLS */}
        <div className="panel">
          <h2>🕹 Environment Controls</h2>
          <p className="panel-subtext">
            Control the benchmark loop manually using reset, state, step, and grade interactions.
          </p>
          <div className="control-buttons">
            <button onClick={handleReset} disabled={loading}>Reset Task</button>
            <button onClick={handleState} disabled={loading}>Get State</button>
            <button onClick={handleGrade} disabled={loading}>Get Grade</button>
          </div>
        </div>

        {/* LIVE STATE */}
        <div className="grid-two">
          <div className="panel">
            <h2>🚚 Truck State</h2>
            {trucks.length === 0 ? (
              <p>No observation loaded yet. Click <strong>Reset Task</strong>.</p>
            ) : (
              trucks.map((truck) => (
                <div key={truck.id} className="card">
                  <h3>{truck.id} — {truck.truck_type.toUpperCase()}</h3>
                  <p><strong>Capacity:</strong> {truck.capacity}</p>
                  <p><strong>Energy:</strong> {truck.energy_level.toFixed(2)}%</p>
                  <p><strong>CO₂ Emitted:</strong> {truck.co2_emitted.toFixed(2)}</p>
                  <p><strong>Location:</strong> [{truck.current_location.join(", ")}]</p>
                </div>
              ))
            )}
          </div>

          <div className="panel">
            <h2>📦 Available Orders</h2>
            {orders.length === 0 ? (
              <p>No pending orders available.</p>
            ) : (
              orders.map((order) => (
                <div key={order.id} className="card">
                  <h3>{order.id}</h3>
                  <p><strong>Weight:</strong> {order.weight}</p>
                  <p><strong>Deadline:</strong> {order.deadline}</p>
                  <p><strong>Location:</strong> [{order.location.join(", ")}]</p>
                  <p><strong>Status:</strong> {order.is_delivered ? "Delivered" : "Pending"}</p>
                </div>
              ))
            )}
          </div>
        </div>

        {/* STEP PANEL */}
        <div className="panel">
          <h2>⚙ Execute Agent Action</h2>
          <p className="panel-subtext">
            Choose a truck and assign it to one pending order. This triggers one environment step.
          </p>

          <div className="action-row">
            <select value={selectedTruck} onChange={(e) => setSelectedTruck(e.target.value)}>
              <option value="T1">T1 — Electric</option>
              <option value="T2">T2 — Diesel</option>
            </select>

            <select value={selectedOrder} onChange={(e) => setSelectedOrder(e.target.value)}>
              <option value="">Select Order</option>
              {orders.map((order) => (
                <option key={order.id} value={order.id}>
                  {order.id}
                </option>
              ))}
            </select>

            <button onClick={handleStep} disabled={loading || !selectedOrder}>
              Run Step
            </button>
          </div>
        </div>

        {/* STEP RESULT */}
        {stepResult && (
          <div className="panel">
            <h2>📈 Step Feedback</h2>
            <div className="grid-three">
              <div className="metric-card">
                <h3>Reward</h3>
                <p>{stepResult.reward}</p>
              </div>
              <div className="metric-card">
                <h3>Done</h3>
                <p>{stepResult.done ? "Yes" : "No"}</p>
              </div>
              <div className="metric-card">
                <h3>Info</h3>
                <p>{stepResult.info?.error || stepResult.info?.reason || "None"}</p>
              </div>
            </div>
          </div>
        )}

        {/* GRADE RESULT */}
        {gradeData && (
          <div className="panel">
            <h2>🏁 Grade Summary</h2>
            <div className="grid-three">
              <div className="metric-card">
                <h3>Score</h3>
                <p>{gradeData.score}</p>
              </div>
              <div className="metric-card">
                <h3>Delivered</h3>
                <p>{gradeData.state_summary.delivered} / {gradeData.state_summary.total_orders}</p>
              </div>
              <div className="metric-card">
                <h3>Total CO₂</h3>
                <p>{gradeData.state_summary.total_co2}</p>
              </div>
            </div>
          </div>
        )}

        {/* RAW STATE */}
        {stateData && (
          <div className="panel">
            <h2>🧾 Full Environment State</h2>
            <pre className="json-box">{JSON.stringify(stateData, null, 2)}</pre>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;