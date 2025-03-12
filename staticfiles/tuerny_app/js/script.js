document.addEventListener("DOMContentLoaded", () => {
  initHeroSlider();
  initBlogCardSlider();
});

const initHeroSlider = () => {

  $(".feature-box-gallery1").slick({
    slidesToShow: 3,
    slidesToScroll: 1,
    infinite: true,
    asNavFor: "#hero-slider-bottom",
    focusOnSelect: true,
    arrows: false,
    centerMode: true,
    centerPadding: "0px",
    responsive: [
      {
        breakpoint: 1024,
        settings: {
          slidesToShow: 2,
          slidesToScroll: 1,
        },
      },
      {
        breakpoint: 580,
        settings: {
          slidesToShow: 1,
          slidesToScroll: 1,
          centerPadding: "50px",
        },
      },
    ],
  });

  $(".slide-products").slick({
    dots: true,
    infinite: true,
    speed: 300,
    slidesToShow: 1,
    centerMode: true,
    variableWidth: true,
    responsive: [
      {
        breakpoint: 1024,
        settings: {
          slidesToShow: 2,
          slidesToScroll: 1,
        },
      },
      {
        breakpoint: 580,
        settings: {
          slidesToShow: 1,
          slidesToScroll: 1,
        },
      },
    ],
  });

  $("#hero-slider-top").slick({
    slidesToShow: 3,
    slidesToScroll: 1,
    // infinite: true,
    asNavFor: "#hero-slider-bottom",
    focusOnSelect: true,
    arrows: false,
    centerMode: true,
    centerPadding: "0px",
    // variableWidth: true,
    // fade: true,
    responsive: [
      {
        breakpoint: 768,
        settings: {
          slidesToShow: 1,
          slidesToScroll: 1,
        },
      },
      {
        breakpoint: 581,
        settings: {
          slidesToShow: 1,
          slidesToScroll: 1,
          // centerPadding: "50px",
        },
      },
    ],
  });

  $("#hero-slider-bottom").slick({
    slidesToShow: 1,
    slidesToScroll: 1,
    // infinite: true,
    asNavFor: "#hero-slider-top",
    // focusOnSelect: true,
    arrows: true,
    dots: true,
    // centerMode: true,
    // centerPadding: "0px",
    
  });
};

const initBlogCardSlider = () => {
  $(".blog-card-slider").slick({
    slidesToShow: 4,
    slidesToScroll: 1,
    infinite: true,
    focusOnSelect: true,
    arrows: false,
    dots: false,
    centerMode: false,
    responsive: [
      {
        breakpoint: 1200,
        settings: {
          slidesToShow: 3,
          slidesToScroll: 1,
          dots: true,
        },
      },
      {
        breakpoint: 768,
        settings: {
          slidesToShow: 2,
          slidesToScroll: 1,
          arrows: true,
          dots: true,
        },
      },
    ],
  });
  $(".blog-card-slider-3").slick({
    slidesToShow: 3,
    slidesToScroll: 1,
    infinite: true,
    focusOnSelect: true,
    arrows: false,
    dots: false,
    centerMode: false,
    responsive: [
      {
        breakpoint: 1200,
        settings: {
          slidesToShow: 3,
          slidesToScroll: 1,
          dots: true,
        },
      },
      {
        breakpoint: 768,
        settings: {
          slidesToShow: 2,
          slidesToScroll: 1,
          dots: true,
        },
      },
    ],
  });
  $(".blog-card-slider-2").slick({
    slidesToShow: 6,
    slidesToScroll: 1,
    infinite: true,
    focusOnSelect: true,
    arrows: true,
    dots: false,
    centerMode: false,
    nextArrow: $(".blog-card-slider-2-container .slider-next"),
    prevArrow: $(".blog-card-slider-2-container .slider-prev"),
    responsive: [
      {
        breakpoint: 1200,
        settings: {
          slidesToShow: 4,
        },
      },
      {
        breakpoint: 900,
        settings: {
          slidesToShow: 3,
        },
      },
      {
        breakpoint: 600,
        settings: {
          slidesToShow: 2,
        },
      },
      {
        breakpoint: 480,
        settings: {
          slidesToShow: 1,
          centerMode: true,
        },
      },
    ],
  });
  $(".image-slider").slick({
    slidesToShow: 6,
    slidesToScroll: 1,
    infinite: true,
    focusOnSelect: true,
    arrows: true,
    dots: false,
    centerMode: false,
    responsive: [
      {
        breakpoint: 1200,
        settings: {
          slidesToShow: 4,
        },
      },
      {
        breakpoint: 900,
        settings: {
          slidesToShow: 3,
        },
      },
      {
        breakpoint: 600,
        settings: {
          slidesToShow: 2,
        },
      },
      {
        breakpoint: 480,
        settings: {
          slidesToShow: 1,
          centerMode: true,
        },
      },
    ],
  });
};

// $(".menu-loader").hover(function () {
//   var id = $(this).attr("data-id");
//   $.ajax({
//     type: "POST",
//     url: "/Controller/ajax/ajax.php?process=menu-load&id=" + id + "",
//     success: function (response) {
//       $(".menu-load-div").html(response);
//     },
//   });
// });

// $(".logoutbtn").click(function () {
//   $.ajax({
//     type: "POST",
//     url: "/Controller/ajax/ajax.php?process=logout",
//     success: function (response) {
//       $(".general-response").html(response);
//     },
//   });
// });

$(".addsurver_check").click(function () {
  if (!$(this).is(":checked")) {
    $(".survey-select").removeClass("vRequired");
    $(".survey-select").val("");
  } else {
    $(".survey-select").addClass("vRequired");
  }
});
$(".blog-comment-checkbox-label").click(function () {
  if (!$(this).is(":checked")) {
    $(".opacity-check").style.opacity = 1;
    
  } else {
    $(".opacity-check").style.opacity = 0.3;
  }
});

$(".survey-btn").click(function () {
  var id = $(this).attr("data-id");
  var radioValue = $('input[name="survey_radio_"' + id + "]:checked").val();
  alert(radioValue);
});

// $(".morebtn").click(function () {
//   var start = $(this).attr("data-start");
//   var category = $(this).attr("data-category");
//   $(this).attr("data-start", parseInt(start) + 5);
//   $.ajax({
//     type: "POST",
//     url:
//       "/Controller/ajax/ajax.php?process=moreask&start=" +
//       start +
//       "&category=" +
//       category +
//       "",
//     success: function (response) {
//       $(".quest-listdiv").append(response);
//     },
//   });
// });

$(".share-btn").on("click", function (e) {
  e.preventDefault();
  $(this).siblings(".social-menu").toggle();
});

// Sosyal medya paylaşımı
$(".social-btn").on("click", function (e) {
  e.preventDefault();
  const url = $(this).data("url");
  const fullUrl = window.location.origin + url;

  if ($(this).hasClass("facebook")) {
    window.open(
      `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(
        fullUrl
      )}`,
      "_blank"
    );
  } else if ($(this).hasClass("twitter")) {
    window.open(
      `https://x.com/intent/tweet?url=${encodeURIComponent(fullUrl)}`,
      "_blank"
    );
  } else if ($(this).hasClass("linkedin")) {
    window.open(
      `https://www.linkedin.com/shareArticle?mini=true&url=${encodeURIComponent(
        fullUrl
      )}`,
      "_blank"
    );
  }
});

$(document).on("click", function (e) {
  if (!$(e.target).closest(".share-container").length) {
    $(".social-menu").hide();
  }
});


$(document).ready(function ($) {
  $(".telefoninput").mask("(999) 999 99 99", {
    placeholder: "(___) ___ __ __",
  });
  $(".ibanno").mask("TR 9999 9999 9999 9999 9999 9999", {
    placeholder: "TR ____ ____ ____ ____ ____ ____",
  });
});

$(document).ready(function () {
  // ASK LETTER LIMITS
  $("#counter-input").keyup(function () {
    $("#title-counter").text(this.value.replace(/ /g, "").length + "/90");
  });
 
  $("#survey-counter-input").keyup(function () {
    $("#survey-title-counter").text(this.value.replace(/ /g, "").length + "/90");
  });

  $("#counter-textarea").keyup(function () {
    $("#content-counter").text(this.value.replace(/ /g, "").length + "/360");
  });
});

function updateRateLine(id) {
  const likeCount = parseInt($(`.heart-result-${id}`).text()) || 0;
  const dislikeCount = parseInt($(`.heart-crack-result-${id}`).text()) || 0;
  const totalVotes = likeCount + dislikeCount;

  if (totalVotes > 0) {
    const likePercentage = (likeCount / totalVotes) * 100;
    const dislikePercentage = (dislikeCount / totalVotes) * 100;

    $(`#rate-like-${id}`).css("width", `${likePercentage}%`);
    $(`#rate-dislike-${id}`).css("width", `${dislikePercentage}%`);
  } else {
    $(`#rate-like-${id}`).css("width", "0%");
    $(`#rate-dislike-${id}`).css("width", "0%");
  }
}

// $(".like-button").on("click", function () {
//   const id = $(this).data("id");
//   const likeSpan = $(`.heart-result-${id}`);
//   const currentLikes = parseInt(likeSpan.text());

//   $.post("/like", { id: id }, function (response) {
//     if (response.success) {
//       likeSpan.text(currentLikes + 1);
//       updateRateLine(id);
//     } else {
//       console.error("Beğenme işlemi başarısız oldu.");
//     }
//   });
// });

// $(".dislike-button").on("click", function () {
//   const id = $(this).data("id");
//   const dislikeSpan = $(`.heart-crack-result-${id}`);
//   const currentDislikes = parseInt(dislikeSpan.text());

//   $.post("/dislike", { id: id }, function (response) {
//     if (response.success) {
//       dislikeSpan.text(currentDislikes + 1);
//       updateRateLine(id);
//     } else {
//       console.error("Beğenmeme işlemi başarısız oldu.");
//     }
//   });
// });



//profile tabs



$(".header-link-container.open-header-link").hover(function() {
  $(".header-menu").addClass("show-before");
  let scrollBarWidth = window.innerWidth - document.documentElement.clientWidth;
  $("body").css({
    "overflow": "hidden",
    "padding-right": scrollBarWidth + "px"
  });
}, function() {
  $(".header-menu").removeClass("show-before")
  $("body").css({
    "overflow": "auto",
    "padding-right": "0"
  });
});

// $('.menu-loader').on('click', function (e) {
//   const selectedCategory = $(this).data('category');

//   if (selectedCategory) {
//     e.preventDefault(); 
//     $('.blog-item').hide();
//     $(`.blog-item[data-category="${selectedCategory}"]`).fadeIn();

//     setTimeout(() => {
//       window.location.href = $(this).attr('href');
//     }, 1000);
//   }
// });

$(document).ready(function() {
  // Belirtilen kategoriye ait blog öğelerini filtreleyen fonksiyon
  function filterBlogs(category) {
    $(".menu-load-div .col-md-2")
      .hide() // Tüm blogları gizle
      .filter(function() {
        return $(this).data("category") == category;
      })
      .show(); // Seçilen kategoriye ait blogları göster
  }

  // Sayfa yüklendiğinde, global olarak ilk bulunan menü-loader'ın kategorisine göre blogları göster
  let firstCategory = $(".menu-loader").first().data("category");
  filterBlogs(firstCategory);

  // Menü içindeki kategori öğesi üzerine gelindiğinde ilgili blogları göster
  $(".menu-loader").on("mouseenter", function() {
    let selectedCategory = $(this).data("category");
    filterBlogs(selectedCategory);
  });

  // Her ana dropdown (header-link-container) üzerine gelindiğinde, o menüye ait default (ilk) kategori aktif hale gelsin
  $(".header-link-container").on("mouseenter", function() {
    let defaultCategory = $(this).find(".menu-loader").first().data("category");
    filterBlogs(defaultCategory);
  });




  // Hover olayı için
  $(".menu-loader").hover(
    function () {
      const selectedCategory = $(this).data("category"); // Menüdeki kategori
      
      // Blog kategorilerini kontrol et ve göster/gizle
      $(".menu-load-div .col-md-2").each(function () {
        const blogCategory = $(this).data("category"); // Blogun kategori verisi

        if (blogCategory === selectedCategory) {
          $(this).show(); // Kategori eşleşiyorsa göster
        } else {
          $(this).hide(); // Eşleşmiyorsa gizle
        }
      });
      
    },
    
  );
});

document.addEventListener("scroll", function() {
  let scrollY = window.scrollY || window.pageYOffset; // Kullanıcının kaydırdığı piksel miktarı
  let offcanvasDiv = document.getElementById("offcanvasScrolling");

  if (scrollY < 40) {
      offcanvasDiv.style.marginTop = `${111 - scrollY}px`; // Her kaydırmada azalt
  } else {
      offcanvasDiv.style.marginTop = "71px"; // 40px veya daha fazla kaydırıldığında sabit
  }
});


function toggleDropdown() {
  let dropdown = document.getElementById("dropdownMenu");
  dropdown.style.display = dropdown.style.display === "block" ? "none" : "block";
}


document.getElementById("sidebarToggle").addEventListener("click", function () {
  let icon = document.getElementById("toggleIcon");
  let sidebar = document.getElementById("offcanvasScrolling");

  // Offcanvas açık mı kapalı mı kontrol et
  if (sidebar.classList.contains("show")) {
      // Eğer açık ise, ikon tekrar hamburger menüye dönsün
      icon.outerHTML = `<i id="toggleIcon" class="fa-solid fa-bars fs-5"></i>`;
  } else {
      // Eğer kapalı ise, ikon "çarpı" SVG'si olsun
      icon.outerHTML = `
          <svg id="toggleIcon" width="21" height="21" viewBox="0 0 21 21" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M2 19.3242L19.3241 2.0001" stroke="black" stroke-width="3"/>
              <path d="M2 2.32422L19.3241 19.6483" stroke="black" stroke-width="3"/>
          </svg>
      `;
  }
});

// Offcanvas kapanınca ikon tekrar hamburger menüye dönsün
document.getElementById("offcanvasScrolling").addEventListener("hidden.bs.offcanvas", function () {
  document.getElementById("toggleIcon").outerHTML = `<i id="toggleIcon" class="fa-solid fa-bars fs-5"></i>`;
});