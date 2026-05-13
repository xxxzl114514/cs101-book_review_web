// 假设这是从后端获取的动态评分
const rating = 4.3; // 这里替换为从后端获取的评分
const maxRating = 5;
function displayRating(rating) {
  const starsContainer = document.getElementById("stars");
  const ratingText = document.getElementById("ratingText");
  // 计算星星数量
  for (let i = 1; i <= maxRating; i++) {
    if (i <= rating) {
      starsContainer.innerHTML += '<span class="star">★</span>'; // 完整星星
    } else {
      starsContainer.innerHTML += '<span class="star">☆</span>'; // 空心星星
    }
  }
  // 显示评分文本，保留一位小数
  ratingText.innerText = `${rating.toFixed(1)}/${maxRating}`;
}
// 调用函数显示评分
displayRating(rating);
