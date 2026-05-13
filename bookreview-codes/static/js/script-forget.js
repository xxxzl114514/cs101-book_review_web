document.getElementById("username").addEventListener("input", function () {
  const username = this.value;

  // 如果用户名为空，清空密保问题提示
  if (!username) {
    document.getElementById("securityQuestion").textContent =
      "输入用户名以获取密保问题";
    return;
  }
  // 从后端获取密保问题
  fetch(`/get_security_question?username=${encodeURIComponent(username)}`)
    .then((response) => {
      if (!response.ok) {
        throw new Error("网络响应不正确");
      }
      return response.json();
    })
    .then((data) => {
      if (data.security_question) {
        document.getElementById("securityQuestion").textContent =
          data.security_question;
      } else {
        document.getElementById("securityQuestion").textContent =
          "获取密保问题失败，请稍后重试";
      }
    })
    .catch((error) => {
      console.error("获取密保问题失败:", error);
      document.getElementById("securityQuestion").textContent =
        "获取密保问题失败，请稍后重试";
    });
});
