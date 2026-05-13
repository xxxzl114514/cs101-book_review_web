/*
document.querySelector("form").addEventListener("submit", function (event) {
  event.preventDefault(); // 阻止表单默认提交行为

  // 获取表单数据
  const formData = new FormData(document.querySelector("form"));

  // 发送表单数据到后端
  fetch("/new_review", {
    method: "POST",
    body: formData,
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.success) {
        alert("评论提交成功！");
        // 可以在这里添加重置表单或刷新页面的逻辑
      } else {
        alert("评论提交失败：" + data.message);
      }
    })
    .catch((error) => {
      console.error("Error:", error);
      alert("发生错误，请稍后再试。");
    });
});
*/