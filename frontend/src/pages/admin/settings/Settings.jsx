import React, { useEffect, useMemo, useState } from "react";

const API_BASE =
  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000/api";

export default function Settings() {
  const [groups, setGroups] = useState([]);
  const [activeGroupSlug, setActiveGroupSlug] = useState("");
  const [formData, setFormData] = useState({});
  const [search, setSearch] = useState("");

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  // ---------------- FETCH SETTINGS ---------------- //
  const fetchSettings = async () => {
    try {
      setLoading(true);
      setError("");

      const res = await fetch(`${API_BASE}/settings/`, {
        method: "GET",
        credentials: "include",
      });

      const data = await res.json();

      if (!res.ok || !data.success) {
        throw new Error(data.message || "Failed to load settings");
      }

      const settingGroups = data.data || [];
      setGroups(settingGroups);

      if (settingGroups.length > 0 && !activeGroupSlug) {
        setActiveGroupSlug(settingGroups[0].slug);
      }

      const initialValues = {};

      settingGroups.forEach((group) => {
        group.fields.forEach((field) => {
          initialValues[field.key] =
            field.current_value ?? field.default_value ?? "";
        });
      });

      setFormData(initialValues);
    } catch (err) {
      setError(err.message || "Something went wrong");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSettings();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // ---------------- ACTIVE GROUP ---------------- //
  const activeGroup = useMemo(() => {
    return groups.find((group) => group.slug === activeGroupSlug);
  }, [groups, activeGroupSlug]);

  // ---------------- FILTERED FIELDS ---------------- //
  const filteredFields = useMemo(() => {
    if (!activeGroup?.fields) return [];

    const keyword = search.trim().toLowerCase();

    if (!keyword) return activeGroup.fields;

    return activeGroup.fields.filter((field) => {
      return (
        field.label.toLowerCase().includes(keyword) ||
        field.key.toLowerCase().includes(keyword) ||
        field.help_text?.toLowerCase().includes(keyword)
      );
    });
  }, [activeGroup, search]);

  // ---------------- HANDLE CHANGE ---------------- //
  const handleChange = (key, value) => {
    setFormData((prev) => ({
      ...prev,
      [key]: value,
    }));
  };

  // ---------------- SAVE GROUP SETTINGS ---------------- //
  const handleSave = async () => {
    if (!activeGroup) return;

    try {
      setSaving(true);
      setMessage("");
      setError("");

      const settingsPayload = {};

      activeGroup.fields.forEach((field) => {
        if (field.field_type !== "file") {
          settingsPayload[field.key] = formData[field.key] ?? "";
        }
      });

      const res = await fetch(`${API_BASE}/settings/update/`, {
        method: "POST",
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          settings: settingsPayload,
        }),
      });

      const data = await res.json();

      if (!res.ok || !data.success) {
        throw new Error(data.message || "Failed to update settings");
      }

      setMessage(data.message || "Settings updated successfully.");
      fetchSettings();
    } catch (err) {
      setError(err.message || "Something went wrong while saving.");
    } finally {
      setSaving(false);
    }
  };

  // ---------------- FILE UPLOAD ---------------- //
  const handleFileUpload = async (fieldKey, file) => {
    if (!file) return;

    try {
      setSaving(true);
      setMessage("");
      setError("");

      const payload = new FormData();
      payload.append("key", fieldKey);
      payload.append("file", file);

      const res = await fetch(`${API_BASE}/settings/upload-file/`, {
        method: "POST",
        credentials: "include",
        body: payload,
      });

      const data = await res.json();

      if (!res.ok || !data.success) {
        throw new Error(data.message || "File upload failed");
      }

      setMessage(data.message || "File uploaded successfully.");
      fetchSettings();
    } catch (err) {
      setError(err.message || "Something went wrong while uploading file.");
    } finally {
      setSaving(false);
    }
  };

  // ---------------- FIELD RENDERER ---------------- //
  const renderField = (field) => {
    const value = formData[field.key] ?? "";

    switch (field.field_type) {
      case "textarea":
        return (
          <textarea
            className="form-control settings-input"
            rows="4"
            placeholder={field.placeholder || ""}
            required={field.is_required}
            value={value}
            onChange={(e) => handleChange(field.key, e.target.value)}
          />
        );

      case "select":
        return (
          <select
            className="form-select settings-input"
            required={field.is_required}
            value={value}
            onChange={(e) => handleChange(field.key, e.target.value)}
          >
            <option value="">Select {field.label}</option>

            {(field.options || []).map((option, index) => (
              <option key={index} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        );

      case "toggle":
        return (
          <div className="form-check form-switch settings-switch">
            <input
              className="form-check-input"
              type="checkbox"
              role="switch"
              checked={
                value === true ||
                value === "true" ||
                value === "1" ||
                value === "yes"
              }
              onChange={(e) =>
                handleChange(field.key, e.target.checked ? "true" : "false")
              }
            />
            <label className="form-check-label">
              {value === "true" || value === true ? "Enabled" : "Disabled"}
            </label>
          </div>
        );

      case "file":
        return (
          <>
            <input
              type="file"
              className="form-control settings-input"
              onChange={(e) =>
                handleFileUpload(field.key, e.target.files?.[0])
              }
            />

            {field.uploaded_file?.file_url && (
              <div className="settings-file-preview mt-2">
                <a
                  href={field.uploaded_file.file_url}
                  target="_blank"
                  rel="noreferrer"
                >
                  View uploaded file
                </a>
              </div>
            )}
          </>
        );

      case "color":
        return (
          <div className="settings-color-row">
            <input
              type="color"
              className="form-control form-control-color"
              value={value || "#000000"}
              onChange={(e) => handleChange(field.key, e.target.value)}
            />

            <input
              type="text"
              className="form-control settings-input"
              value={value}
              placeholder="#000000"
              onChange={(e) => handleChange(field.key, e.target.value)}
            />
          </div>
        );

      case "password":
        return (
          <input
            type="password"
            className="form-control settings-input"
            placeholder={field.placeholder || ""}
            required={field.is_required}
            value={value}
            onChange={(e) => handleChange(field.key, e.target.value)}
          />
        );

      case "email":
      case "number":
      case "text":
      default:
        return (
          <input
            type={field.field_type || "text"}
            className="form-control settings-input"
            placeholder={field.placeholder || ""}
            required={field.is_required}
            value={value}
            onChange={(e) => handleChange(field.key, e.target.value)}
          />
        );
    }
  };

  // ---------------- LOADING UI ---------------- //
  if (loading) {
    return (
      <div className="settings-page">
        <div className="settings-loader-card">
          <div className="spinner-border" role="status" />
          <p>Loading settings...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="settings-page">
      <div className="settings-header">
        <div>
          <h2>Settings</h2>
          <p>Manage your store configuration, security, appearance and system preferences.</p>
        </div>

        <button
          className="btn btn-primary settings-save-btn"
          onClick={handleSave}
          disabled={saving || !activeGroup}
        >
          {saving ? "Saving..." : "Save Changes"}
        </button>
      </div>

      {message && <div className="alert alert-success">{message}</div>}
      {error && <div className="alert alert-danger">{error}</div>}

      <div className="settings-layout">
        <aside className="settings-sidebar">
          <div className="settings-sidebar-title">Configuration</div>

          {groups.map((group) => (
            <button
              key={group.id}
              className={`settings-tab ${
                activeGroupSlug === group.slug ? "active" : ""
              }`}
              onClick={() => {
                setActiveGroupSlug(group.slug);
                setSearch("");
              }}
            >
              <span className="settings-tab-icon">
                {group.icon ? <i className={group.icon}></i> : "⚙️"}
              </span>

              <span>{group.name}</span>
            </button>
          ))}
        </aside>

        <main className="settings-content">
          {activeGroup ? (
            <>
              <div className="settings-content-header">
                <div>
                  <h4>{activeGroup.name}</h4>
                  <p>{activeGroup.description || "Update related settings below."}</p>
                </div>

                <input
                  type="text"
                  className="form-control settings-search"
                  placeholder="Search settings..."
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                />
              </div>

              <div className="settings-card">
                {filteredFields.length > 0 ? (
                  filteredFields.map((field) => (
                    <div className="settings-field-row" key={field.id}>
                      <div className="settings-field-info">
                        <label>
                          {field.label}
                          {field.is_required && <span className="required">*</span>}
                        </label>

                        {field.help_text && <small>{field.help_text}</small>}

                        <code>{field.key}</code>
                      </div>

                      <div className="settings-field-control">
                        {renderField(field)}
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="settings-empty">
                    No settings found for this search.
                  </div>
                )}
              </div>

              <div className="settings-footer">
                <button
                  className="btn btn-outline-secondary"
                  onClick={fetchSettings}
                  disabled={saving}
                >
                  Reset
                </button>

                <button
                  className="btn btn-primary"
                  onClick={handleSave}
                  disabled={saving}
                >
                  {saving ? "Saving..." : "Save Changes"}
                </button>
              </div>
            </>
          ) : (
            <div className="settings-empty">No active settings group found.</div>
          )}
        </main>
      </div>
    </div>
  );
}