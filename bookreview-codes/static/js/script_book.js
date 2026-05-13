// 从后端获取动态评分
var averageRatingElement = document.getElementById("averageRatingElement");
var rating = parseFloat(averageRatingElement.getAttribute("rating"));
console.log(rating);
//const rating = 4;
const minRating = 1;
const maxRating = 5;
function displayRating(rating) {
  const starsContainer = document.getElementById("stars");
  const ratingText = document.getElementById("ratingText");
  // 检查评分是否在合法范围内
  if (rating < minRating || rating > maxRating) {
    for (let i = 1; i <= maxRating; i++) {
      starsContainer.innerHTML += '<span class="star">☆</span>'; // 空心星星
    }
    ratingText.innerText = `${rating.toFixed(1)}/${maxRating}`;
  } else {
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
}
// 调用函数显示评分
displayRating(rating);
