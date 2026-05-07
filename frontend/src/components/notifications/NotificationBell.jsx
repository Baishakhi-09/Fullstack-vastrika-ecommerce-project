import { useEffect, useRef, useState } from "react";

const API_BASE =
  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000/api";

const WS_BASE =
  import.meta.env.VITE_WS_BASE_URL || "ws://127.0.0.1:8000";

export default function NotificationBell() {
  const [open, setOpen] = useState(false);
  const [activeTab, setActiveTab] = useState("orders");
  const [unreadCount, setUnreadCount] = useState(0);
  const [notifications, setNotifications] = useState([]);
  const [pulse, setPulse] = useState(false);
  const [socketStatus, setSocketStatus] = useState("connecting");

  const socketRef = useRef(null);
  const reconnectTimerRef = useRef(null);
  const pollingTimerRef = useRef(null);
  const reconnectAttemptsRef = useRef(0);
  const audioRef = useRef(null);

  const fetchNotifications = async () => {
        try {
        const res = await fetch(`${API_BASE}/admin/notifications/`, {
            credentials: "include",
        });

        if (!res.ok) return;

        const data = await res.json();
        setUnreadCount(data.unread_count || 0);
        setNotifications(data.notifications || []);
        } catch {
        // silent fallback
        }
    };

    const startPollingFallback = () => {
        if (pollingTimerRef.current) return;
        pollingTimerRef.current = setInterval(fetchNotifications, 15000);
    };

    const stopPollingFallback = () => {
        if (pollingTimerRef.current) {
        clearInterval(pollingTimerRef.current);
        pollingTimerRef.current = null;
        }
    };

    const connectWebSocket = () => {
        const socket = new WebSocket(`${WS_BASE}/ws/admin/notifications/`);
        socketRef.current = socket;

        socket.onopen = () => {
        setSocketStatus("connected");
        reconnectAttemptsRef.current = 0;
        stopPollingFallback();
        };

        socket.onmessage = (event) => {
            const payload = JSON.parse(event.data);

            if (payload.event !== "new_notification") return;

            const newItem = payload.notification;

            setNotifications((prev) => [newItem, ...prev]);
            setUnreadCount((prev) => prev + 1);

            setPulse(true);
            setTimeout(() => setPulse(false), 900);

            audioRef.current?.play().catch(() => {});
        };

        socket.onerror = () => {
            setSocketStatus("error");
        };

        socket.onclose = () => {
            setSocketStatus("disconnected");
            startPollingFallback();

            reconnectAttemptsRef.current += 1;

            const delay = Math.min(
                1000 * 2 ** reconnectAttemptsRef.current,
                30000
            );

            reconnectTimerRef.current = setTimeout(() => {
                connectWebSocket();
            }, delay);
        };
    };

    useEffect(() => {
        fetchNotifications();

        audioRef.current = new Audio("/sounds/notification.mp3");

        connectWebSocket();

        return () => {
            socketRef.current?.close();

            if (reconnectTimerRef.current) {
                clearTimeout(reconnectTimerRef.current);
            }

            stopPollingFallback();
        };
    }, []);

    const markAllRead = async () => {
        await fetch(`${API_BASE}/admin/notifications/read-all/`, {
            method: "POST",
            credentials: "include",
        });

        setUnreadCount(0);
        setNotifications((prev) =>
            prev.map((item) => ({ ...item, is_read: true }))
        );
    };

    const filteredNotifications = notifications.filter((item) => {
        if (activeTab === "orders") return item.notification_type === "order";
        if (activeTab === "returns") return item.title.toLowerCase().includes("return");
        if (activeTab === "payments") return item.title.toLowerCase().includes("payment");
        return true;
    });

    return (
        <div className="notification-wrapper">
            <button
                className={`notification-btn ${pulse ? "pulse" : ""}`}
                onClick={() => setOpen(!open)}>
                    
                <span className="bell-icon">Bell</span>

                {unreadCount > 0 && (
                    <span className="notification-count">{unreadCount}</span>
                )}
            </button>

            {open && (
                <div className="notification-dropdown">
                    <div className="notification-header">
                        <div>
                            <strong>Notifications</strong>
                            <span className={`socket-status ${socketStatus}`}>
                                {socketStatus}
                            </span>
                        </div>

                        <button onClick={markAllRead}>Mark all read</button>
                    </div>

                    <div className="notification-tabs">
                        <button
                            className={activeTab === "orders" ? "active" : ""}
                            onClick={() => setActiveTab("orders")}>
                            
                            Orders
                        </button>

                        <button
                            className={activeTab === "returns" ? "active" : ""}
                            onClick={() => setActiveTab("returns")}>
                            
                            Returns
                        </button>

                        <button
                            className={activeTab === "payments" ? "active" : ""}
                            onClick={() => setActiveTab("payments")}>
                            
                            Payments
                        </button>
                    </div>

                    <div className="notification-list">
                        {filteredNotifications.length === 0 ? (
                            <p className="empty-notification">No notifications</p>
                        ) : (
                            filteredNotifications.map((item) => (
                                <a key={item.id} href={item.url || "#"} className={`notification-item ${
                                    item.is_read ? "" : "unread"}`}>
                                    
                                    <strong>{item.title}</strong>
                                    <p>{item.message}</p>
                                    <small>{new Date(item.created_at).toLocaleString()}</small>
                                </a>
                            ))
                        )}
                    </div>
                </div>
            )}
        </div>
    );
}