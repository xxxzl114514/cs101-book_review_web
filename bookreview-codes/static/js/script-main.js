let slideIndex = 0; // 当前幻灯片索引，初始值为0
let timer; // 保存计时器的变量
showSlides(); // 显示幻灯片
// 显示幻灯片的函数
function showSlides() {
  let i;
  let slides = document.getElementsByClassName("mySlides"); // 获取所有类名为mySlides的元素，即所有幻灯片
  let dots = document.getElementsByClassName("dot"); // 获取所有类名为dot的元素，即所有导航点
  // 隐藏所有幻灯片
  for (i = 0; i < slides.length; i++) {
    slides[i].style.display = "none"; // 将每个幻灯片的display属性设为none，隐藏
  }
  // 重置所有点的状态
  for (i = 0; i < dots.length; i++) {
    dots[i].className = dots[i].className.replace(" active", ""); // 移除所有点的active类，取消激活状态
  }
  // 循环显示幻灯片
  slideIndex++; // 当前幻灯片索引加1
  if (slideIndex > slides.length) {
    // 如果索引超过幻灯片数量
    slideIndex = 1; // 索引重置为1，即第一张幻灯片
  }
  if (slideIndex < 1) {
    // 如果索引小于1
    slideIndex = slides.length; // 索引设为幻灯片总数，即最后一张幻灯片
  }
  // 显示当前幻灯片，并设置激活点
  slides[slideIndex - 1].style.display = "block"; // 将当前索引对应的幻灯片display设为block，显示
  dots[slideIndex - 1].className += " active"; // 将当前索引对应的点添加active类，激活
  // 清除旧的计时器，防止速度加快
  clearTimeout(timer);
  // 每 5 秒切换幻灯片
  timer = setTimeout(showSlides, 5000);
}

// 手动切换功能
function plusSlides(n) {
  // 清除旧的计时器，防止速度加快
  clearTimeout(timer);
  // 更新索引并立即切换
  slideIndex += n - 1; // 减去1确保当前索引一致
  showSlides();
}
// 设置当前幻灯片
function currentSlide(n) {
  // 清除旧的计时器，防止速度加快
  clearTimeout(timer);
  // 设置为索引并立即切换
  slideIndex = n - 1;
  showSlides();
}

// 搜索书籍功能
function searchBooks(event) {
  event.preventDefault(); // 阻止表单的默认提交行为
  const keyword = $("#keyword").val();
  $.ajax({
    url: "/search_books",
    method: "GET",
    data: { keyword: keyword },
    success: function (response) {
      updateBooksContainer(response);
      toggleRefreshSection(keyword, response);
    },
    error: function () {
      alert("搜索失败，请稍后重试。");
    },
  });
}

//刷新随机书籍功能
function refreshBooks() {
  $.ajax({
    url: "/refresh_books",
    method: "GET",
    success: function (response) {
      updateBooksContainer(response);
    },
    error: function () {
      alert("获取新书籍数据失败，请稍后重试。");
    },
  });
}

function updateBooksContainer(books) {
  $(".book-container").empty(); // 清空原有内容
  if (books.length > 0) {
    books.forEach(function (book) {
      const bookElement = `
              <a href="/book/${book.id}">
                  <div class="book-item">
                      <img src="/static/covers/${book.coverpath}" alt="书籍封面">
                      <h3>书名：${book.title}</h3>
                      <p>作者：${book.author}</p>
                      <p>ISBN: ${book.isbn}</p>
                  </div>
              </a>
          `;
      $(".book-container").append(bookElement);
    });
  } else {
    const emptyElement = `
            <h3>还没有书籍喔...</h3>
        `;
    $(".book-container").append(emptyElement);
  }
}

// 当搜索栏内有内容时，隐藏刷新区域
function toggleRefreshSection(keyword, response) {
  if (keyword || !response) {
    $(".refresh-section").hide(); // 隐藏刷新区域
  } else {
    $(".refresh-section").show(); // 显示刷新区域
  }
}

$(document).ready(function () {
  $("#BookSearchForm").on("submit", searchBooks);
});
