// export const isAuthenticated = () => {
//   const token = localStorage.getItem("access");
//   return !!token;
// };

export const isAuthenticated = async () => {
  try {
    const res = await fetch("http://127.0.0.1:8000/api/auth/user/me/", {
        method: "GET",
        credentials: "include", // send cookies
      });

      if (res.status === 401) return false;
      return res.ok;

    } catch (error) {
      console.error("Auth error:", error);
      return false;
  }
};