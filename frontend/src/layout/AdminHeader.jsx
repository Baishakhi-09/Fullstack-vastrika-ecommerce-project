import NotificationBell from "../components/notifications/NotificationBell";

export default function AdminHeader() {
  return (
    <div className="admin-header">
      <h2>Dashboard</h2>

      <div className="header-right">
        <NotificationBell />   {/* 👈 HERE */}
      </div>
    </div>
  );
}