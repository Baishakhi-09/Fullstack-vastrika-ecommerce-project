import { useMemo } from "react";
import zxcvbn from "zxcvbn";

export default function PasswordStrength({ password, email = "", name = "" }) {
    const result = useMemo(() => {
        return zxcvbn(password || "", [email, name]);
    }, [password, email, name]);

    const score = result.score; // 0 to 4

    const labels = ["Very weak", "Weak", "Fair", "Good", "Strong"];

    const widths = ["20%", "40%", "60%", "80%", "100%"];

    const colors = ["#dc2626", "#f97316", "#eab308", "#22c55e", "#15803d"];

    const tips = [];

    if ((password || "").length < 12) {
        tips.push("Use at least 12 characters");
    }

    if (result.feedback?.warning) {
        tips.push(result.feedback.warning);
    }

    if (result.feedback?.suggestions?.length) {
        tips.push(...result.feedback.suggestions);
    }

    return (
        <div style={{ marginTop: "10px" }}>
            <div
                style={{
                    width: "100%",
                    height: "8px",
                    background: "#f1f1f1",
                    borderRadius: "999px",
                    overflow: "hidden",
                }}
            >
                <div
                    style={{
                        width: password ? widths[score] : "0%",
                        height: "100%",
                        background: password ? colors[score] : "#f1f1f1",
                        transition: "all 0.3s ease",
                        borderRadius: "999px",
                    }}
                />
            </div>

            {password && (
                <>
                    <p
                        style={{
                            marginTop: "8px",
                            fontSize: "13px",
                            fontWeight: "600",
                            color: colors[score],
                        }}
                    >
                        Password strength: {labels[score]}
                    </p>

                    {tips.length > 0 && (
                        <ul style={{ marginTop: "6px", paddingLeft: "18px", fontSize: "12px", color: "#666" }}>
                            {tips.slice(0, 2).map((tip, index) => (
                                <li key={index}>{tip}</li>
                            ))}
                        </ul>
                    )}
                </>
            )}
        </div>
    );
}