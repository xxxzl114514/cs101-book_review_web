let slideIndex = 0; // 当前幻灯片索引
let timer; // 保存计时器的变量
showSlides(); // 显示幻灯片
// 自动播放功能
function showSlides() {
  let i;
  let slides = document.getElementsByClassName("mySlides");
  let dots = document.getElementsByClassName("dot");
  // 隐藏所有幻灯片
  for (i = 0; i < slides.length; i++) {
    slides[i].style.display = "none";
  }

  // 重置所有点状态
  for (i = 0; i < dots.length; i++) {
    dots[i].className = dots[i].className.replace(" active", "");
  }

  // 循环显示幻灯片
  slideIndex++;
  if (slideIndex > slides.length) {
    slideIndex = 1;
  }
  if (slideIndex < 1) {
    slideIndex = slides.length;
  }

  // 显示当前幻灯片，并设置激活点
  slides[slideIndex - 1].style.display = "block";
  dots[slideIndex - 1].className += " active";
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
