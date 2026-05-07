import AdminHeader from "./AdminHeader";

export default function AdminLayout({ children }) {
  return (
    <div>
      <AdminHeader />
      <main>{children}</main>
    </div>
  );
}