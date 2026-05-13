// 检查表单元素是否存在
/*
const bookForm = document.getElementById("bookForm");
if (bookForm) {
  bookForm.addEventListener("submit", function (event) {
    event.preventDefault(); // 阻止表单默认提交行为

    // 获取表单数据
    const formData = new FormData(bookForm);

    // 发送表单数据到后端
    fetch("/new_book", {
      method: "POST",
      body: formData,
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.success) {
          document.getElementById("message").textContent = "书籍上传成功！";
          document.getElementById("message").style.color = "green";
        } else {
          document.getElementById("message").textContent =
            "书籍上传失败：" + data.message;
          document.getElementById("message").style.color = "red";
        }
      })
      .catch((error) => {
        console.error("Error:", error);
        document.getElementById("message").textContent =
          "发生错误，请稍后再试。";
        document.getElementById("message").style.color = "red";
      });
  });
} 
else {
  console.error("表单元素未找到");
}
*/
