(function($) {
	"use strict";

    // sticky menu
    var header = $('.menu-sticky');
    var win = $(window);

    win.on('scroll', function() {
       var scroll = win.scrollTop();
       if (scroll < 1) {
           header.removeClass("sticky");
       } else {
           header.addClass("sticky");
       }

        $("section").each(function() {
        var elementTop = $(this).offset().top - $('#rs-header').outerHeight();
            if(scroll >= elementTop) {
                $(this).addClass('loaded');
            }
        });

    });

    //window load
    $(window).on( 'load', function() {
        $("#loading").delay(1500).fadeOut(500);
        $("#loading-center").on( 'click', function() {
        $("#loading").fadeOut(500);
        })
    })
    
    //canvas menu
    var navexpander = $('#nav-expander');
    if(navexpander.length){
        $('#nav-expander').on('click',function(e){
            e.preventDefault();
            $('body').toggleClass('nav-expanded');
        });
    }
    var navclose = $('#nav-close');
    if(navclose.length){
        $('#nav-close').on('click',function(e){
            e.preventDefault();
            $('body').removeClass('nav-expanded');
        });
    }

    // AI-like trending suggestions
    const trending = [
      "Women Saree",
      "Men Sneakers",
      "Kids T-Shirts",
      "Designer Handbags",
      "Gold Jewelry",
      "Casual Shirts"
    ];
    const searchInput = document.getElementById("searchInput");
    const suggestionsBox = document.getElementById("suggestions");

    searchInput.addEventListener("input", () => {
      const query = searchInput.value.toLowerCase();
      suggestionsBox.innerHTML = "";
      if (query) {
        const filtered = trending.filter(item => item.toLowerCase().includes(query));
        filtered.forEach(s => {
          const div = document.createElement("div");
          div.textContent = s;
          div.onclick = () => {
            searchInput.value = s;
            suggestionsBox.style.display = "none";
          };
          suggestionsBox.appendChild(div);
        });
        suggestionsBox.style.display = "flex";
      } else {
        suggestionsBox.style.display = "none";
      }
    });

    // Voice search (basic demo using Web Speech API)
    document.querySelector(".mic").addEventListener("click", () => {
      if ('webkitSpeechRecognition' in window) {
        const recognition = new webkitSpeechRecognition();
        recognition.lang = "en-IN";
        recognition.onresult = (event) => {
          searchInput.value = event.results[0][0].transcript;
        };
        recognition.start();
      } else {
        alert("Voice search not supported in this browser");
      }
    });

    // popular categories
    const categories = document.getElementById('categories');
    const nextBtn = document.getElementById('nextBtn');
    const prevBtn = document.getElementById('prevBtn');

    nextBtn.addEventListener('click', () => {
      categories.scrollBy({left: 450, behavior: 'smooth'});
    });

    prevBtn.addEventListener('click', () =>{
      categories.scrollBy({left: -450, behavior: 'smooth'});
    });  

    // feature-collection
    const carousels = document.querySelectorAll('.carousel-container');

    carousels.forEach(container => {
      const carousel = container.querySelector('.carousel');
      const left = container.querySelector('.left');
      const right = container.querySelector('.right');

      right.addEventListener('click', () => {
        carousel.scrollBy({ left: 250, behavior: 'smooth' });
      });

      left.addEventListener('click', () => {
        carousel.scrollBy({ left: -250, behavior: 'smooth' });
      });
    });

      // Optional interactivity — example for favorite icon
      // document.querySelectorAll('.fa-heart').forEach(icon => {
      // icon.addEventListener('click', () => {
      // icon.classList.toggle('active');
      // icon.style.color = icon.classList.contains('active') ? 'red' : 'inherit';
      //   });
      // });


    // trending-now-carousel
    const track = document.querySelector('.carousel-track');
    const items = Array.from(track.children);
    items.forEach(trending_item => {
      const clone = trending_item.cloneNode(true);
      track.appendChild(clone);
    });

    // shop-by-mood--style-board
    const moodCards = document.querySelectorAll('.mood-card');
    const aiSection = document.getElementById('ai-suggestion');
    const aiMessage = document.getElementById('ai-message');
    const productList = document.getElementById('product-list');

    // Simulated AI product database
    const aiRecommendations = {
      casual: {
        message: "You seem relaxed today! Here are some comfy, casual picks you’ll love",
        products: ["Denim Jacket", "Basic Tee", "Casual Sneakers", "Cotton Shorts", "Printed Hoodie"]
      },
      party: {
        message: "Ready to party? AI suggests bold and shiny styles",
        products: ["Sequin Dress", "Velvet Blazer", "High Heels", "Silver Clutch", "Statement Earrings"]
      },
      ethnic: {
        message: "Celebrate culture with our top ethnic picks",
        products: ["Kurta Set", "Saree", "Embroidered Dupatta", "Jhumka Earrings", "Kolhapuri Sandals"]
      },
      street: {
        message: "Your vibe is street-smart! Try these edgy outfits",
        products: ["Graphic Tee", "Cargo Pants", "Denim Jacket", "Sneakers", "Bucket Hat"]
      },
      formal: {
        message: "Power mode ON. Here’s what our AI recommends for work",
        products: ["Blazer", "Formal Shirt", "Pencil Skirt", "Leather Shoes", "Watch"]
      }
    };

    // AI click handler
    moodCards.forEach(card => {
      card.addEventListener('click', () => {
        const mood = card.dataset.mood;
        const aiData = aiRecommendations[mood];

        // Show AI section
        aiSection.classList.remove('hidden');
        aiMessage.textContent = aiData.message;

        // Generate product cards dynamically
        productList.innerHTML = "";
        aiData.products.forEach(product => {
          const item = document.createElement('div');
          item.classList.add('product-item');
          item.innerHTML = `
            <img src="file:///D:/project-2025-26/e-commerce/index.html=${encodeURIComponent(product)}" alt="${product}">
            <span>${product}</span>
          `;
          productList.appendChild(item);
        });

        // Smooth scroll to AI section
        aiSection.scrollIntoView({ behavior: 'smooth' });
      });
    });

})(jQuery);

// Optional JS for animation or interaction for banner section
document.querySelectorAll(".promo-card").forEach(card => {
  card.addEventListener("mouseenter", () => {
    card.style.transform = "scale(1.02)";
    card.style.transition = "0.3s";
  });

  card.addEventListener("mouseleave", () => {
    card.style.transform = "scale(1)";
  });
});

// deal-banner countdown timer
const targetDate = new Date("2025-12-31 23:59:59").getTime();

setInterval(() => {
  const now = new Date().getTime();
  const diff = targetDate - now;

  const days = Math.floor(diff / (1000 * 60 * 60 * 24));
  const hours = Math.floor((diff / (1000 * 60 * 60)) % 24);
  const minutes = Math.floor((diff / (1000 * 60)) % 60);
  const seconds = Math.floor((diff / 1000) % 60);

  document.getElementById("days").innerText = days;
  document.getElementById("hours").innerText = hours;
  document.getElementById("minutes").innerText = minutes;
  document.getElementById("seconds").innerText = seconds;
}, 1000);

// winter-banner
function shopNow() {
  alert("Redirecting to Winter Boots Collection...");
  // window.location.href = "/winter-boots";
}

// user-login
function handleLogin(e) {
  e.preventDefault();
  alert("Login submitted!");
}



