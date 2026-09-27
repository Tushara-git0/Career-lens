// Aetheris Labs - Application Engine
document.addEventListener('DOMContentLoaded', () => {
  // Initialize lucide icons
  if (typeof lucide !== 'undefined') {
    lucide.createIcons();
  }

  // --- CART SYSTEM STATE ---
  let cart = [];

  // DOM Elements - Cart
  const cartDrawer = document.getElementById('cartDrawer');
  const cartOverlay = document.getElementById('cartOverlay');
  const cartOpenBtn = document.getElementById('cartOpenBtn');
  const cartCloseBtn = document.getElementById('cartCloseBtn');
  const cartItemsContainer = document.getElementById('cartItemsContainer');
  const cartBadge = document.getElementById('cartBadge');
  const cartTotal = document.getElementById('cartTotal');
  const checkoutBtn = document.getElementById('checkoutBtn');

  // Toggle Cart Drawer
  function toggleCart() {
    cartDrawer.classList.toggle('open');
    cartOverlay.classList.toggle('open');
  }

  cartOpenBtn.addEventListener('click', toggleCart);
  cartCloseBtn.addEventListener('click', toggleCart);
  cartOverlay.addEventListener('click', toggleCart);

  // Cart Functions
  function saveCart() {
    localStorage.setItem('aetheris_cart', JSON.stringify(cart));
  }

  function loadCart() {
    const stored = localStorage.getItem('aetheris_cart');
    if (stored) {
      cart = JSON.parse(stored);
      renderCart();
    }
  }

  function renderCart() {
    cartItemsContainer.innerHTML = '';
    let total = 0;
    let itemCount = 0;

    if (cart.length === 0) {
      cartItemsContainer.innerHTML = `
        <div class="empty-cart-message">
          <i data-lucide="flask-conical" style="width: 48px; height: 48px; margin-bottom: 15px; stroke-width: 1;"></i>
          <p>No active bio-protocols in your cart.</p>
        </div>
      `;
      if (typeof lucide !== 'undefined') lucide.createIcons();
      checkoutBtn.disabled = true;
    } else {
      cart.forEach(item => {
        itemCount += item.quantity;
        total += item.price * item.quantity;

        const itemEl = document.createElement('div');
        itemEl.classList.add('cart-item');
        itemEl.innerHTML = `
          <img src="${item.img}" alt="${item.title}" class="cart-item-img">
          <div class="cart-item-info">
            <h4 class="cart-item-title">${item.title}</h4>
            <div class="cart-item-price">$${item.price}</div>
            <div class="cart-item-quantity">
              <button class="quantity-btn dec-qty" data-id="${item.id}">-</button>
              <span>${item.quantity}</span>
              <button class="quantity-btn inc-qty" data-id="${item.id}">+</button>
            </div>
          </div>
          <button class="cart-item-remove remove-item" data-id="${item.id}">&times;</button>
        `;
        cartItemsContainer.appendChild(itemEl);
      });
      checkoutBtn.disabled = false;
    }

    cartBadge.textContent = itemCount;
    cartTotal.textContent = `$${total.toFixed(2)}`;

    // Add listeners to new items
    document.querySelectorAll('.dec-qty').forEach(btn => {
      btn.addEventListener('click', () => updateQuantity(btn.dataset.id, -1));
    });
    document.querySelectorAll('.inc-qty').forEach(btn => {
      btn.addEventListener('click', () => updateQuantity(btn.dataset.id, 1));
    });
    document.querySelectorAll('.remove-item').forEach(btn => {
      btn.addEventListener('click', () => removeFromCart(btn.dataset.id));
    });
  }

  function addToCart(id, title, price, img) {
    const existing = cart.find(item => item.id === id);
    if (existing) {
      existing.quantity += 1;
    } else {
      cart.push({ id, title, price: parseFloat(price), img, quantity: 1 });
    }
    saveCart();
    renderCart();
    // Open cart drawer to give direct response feedback
    if (!cartDrawer.classList.contains('open')) {
      toggleCart();
    }
  }

  function removeFromCart(id) {
    cart = cart.filter(item => item.id !== id);
    saveCart();
    renderCart();
  }

  function updateQuantity(id, delta) {
    const item = cart.find(item => item.id === id);
    if (item) {
      item.quantity += delta;
      if (item.quantity <= 0) {
        removeFromCart(id);
      } else {
        saveCart();
        renderCart();
      }
    }
  }

  // Hook up static add-to-cart buttons
  document.querySelectorAll('.add-to-cart-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      const target = e.currentTarget;
      addToCart(
        target.dataset.id,
        target.dataset.title,
        target.dataset.price,
        target.dataset.img
      );
    });
  });

  // Checkout handler
  checkoutBtn.addEventListener('click', () => {
    alert('Aetheris Secure Checkout initialized. Syncing laboratory logs...');
    cart = [];
    saveCart();
    renderCart();
    toggleCart();
  });


  // --- BIO-LONGEVITY ASSESSMENT QUIZ ---
  let currentQuizStep = 1;
  const totalQuizSteps = 3;
  let quizSelections = {};

  const quizOverlay = document.getElementById('quizOverlay');
  const quizProgress = document.getElementById('quizProgress');
  const quizSteps = document.querySelectorAll('.quiz-step');
  const quizCloseBtn = document.getElementById('quizCloseBtn');
  const startQuizBtn = document.getElementById('startQuizBtn');
  const heroQuizBtn = document.getElementById('heroQuizBtn');
  const navQuizBtn = document.getElementById('navQuizBtn');

  // Recommendation products reference
  const productsDatabase = {
    sleep: {
      id: 'somnus',
      title: 'Somnus Circadian Shield',
      price: 349,
      desc: 'Based on your circadian imbalances, the Somnus light therapy system is recommended to realign your melatonin production curves and secure deep REM rest stages.',
      img: 'assets/somnus_shield.webp',
      recTitle: 'Circadian Realignment Protocol'
    },
    physical: {
      id: 'pulse',
      title: 'PEMF Pulse Cell',
      price: 599,
      desc: 'Your high physical workload suggests high cellular energy expenditure. The PEMF Pulse Cell is recommended to restore resting membrane potential and half cellular down-time.',
      img: 'assets/pulse_cell.webp',
      recTitle: 'Cellular Resonance Protocol'
    },
    focus: {
      id: 'neuro',
      title: 'Neuro-Elixir Nootropic',
      price: 129,
      desc: 'To target cognitive bottlenecks and mitigate stress-induced fatigue, we recommend the peptide-infused Neuro-Elixir liposome protocol.',
      img: 'assets/neuro_elixir.webp',
      recTitle: 'Neuro-Cognitive Synergy Protocol'
    }
  };

  // Open Quiz
  function openQuiz() {
    currentQuizStep = 1;
    quizSelections = {};
    updateQuizUI();
    quizOverlay.classList.add('open');
  }

  // Close Quiz
  function closeQuiz() {
    quizOverlay.classList.remove('open');
  }

  startQuizBtn.addEventListener('click', openQuiz);
  heroQuizBtn.addEventListener('click', openQuiz);
  navQuizBtn.addEventListener('click', openQuiz);
  quizCloseBtn.addEventListener('click', closeQuiz);
  document.getElementById('recCloseBtn').addEventListener('click', closeQuiz);

  // Quiz Option Selection
  document.querySelectorAll('.quiz-option').forEach(option => {
    option.addEventListener('click', (e) => {
      const parentStep = option.closest('.quiz-step');
      const stepIdx = parseInt(parentStep.dataset.step);

      // Deselect siblings
      parentStep.querySelectorAll('.quiz-option').forEach(opt => opt.classList.remove('selected'));
      // Select clicked
      option.classList.add('selected');

      // Record selection value
      quizSelections[stepIdx] = option.dataset.value;

      // Enable Next Button
      const nextBtn = parentStep.querySelector('.quiz-next-btn');
      if (nextBtn) {
        nextBtn.removeAttribute('disabled');
      }
    });
  });

  // Next / Previous Navigation
  document.querySelectorAll('.quiz-next-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      if (currentQuizStep < totalQuizSteps) {
        currentQuizStep++;
        updateQuizUI();
      } else if (currentQuizStep === totalQuizSteps) {
        currentQuizStep++; // move to recommendation screen
        generateProtocolRecommendation();
      }
    });
  });

  document.querySelectorAll('.quiz-prev-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      if (currentQuizStep > 1) {
        currentQuizStep--;
        updateQuizUI();
      }
    });
  });

  function updateQuizUI() {
    // Progress Bar
    const progressPercent = (Math.min(currentQuizStep, totalQuizSteps) / totalQuizSteps) * 100;
    quizProgress.style.width = `${progressPercent}%`;

    // Toggle active step display
    quizSteps.forEach(step => {
      const stepIdx = parseInt(step.dataset.step);
      if (stepIdx === currentQuizStep) {
        step.classList.add('active');
      } else {
        step.classList.remove('active');
      }
    });
  }

  // Generate Recommendations
  function generateProtocolRecommendation() {
    // Primary bottleneck decides the product recommendation
    const bottleneck = quizSelections[1]; // 'sleep', 'physical', or 'focus'
    const recommendedProduct = productsDatabase[bottleneck] || productsDatabase.sleep;

    // Fill DOM elements with custom suggestion
    document.getElementById('recTitle').textContent = recommendedProduct.recTitle;
    document.getElementById('recDesc').textContent = recommendedProduct.desc;
    document.getElementById('recImg').src = recommendedProduct.img;
    document.getElementById('recProdName').textContent = recommendedProduct.title;
    document.getElementById('recPrice').textContent = `$${recommendedProduct.price}`;

    // Update buttons in recommendation
    const recAddBtn = document.getElementById('recAddBtn');
    
    // Clear old click listener using replace element cloning technique
    const newRecAddBtn = recAddBtn.cloneNode(true);
    recAddBtn.parentNode.replaceChild(newRecAddBtn, recAddBtn);

    newRecAddBtn.addEventListener('click', () => {
      addToCart(
        recommendedProduct.id,
        recommendedProduct.title,
        recommendedProduct.price,
        recommendedProduct.img
      );
      closeQuiz();
    });

    updateQuizUI();
  }


  // --- SCIENCE TABS SYSTEM ---
  const tabButtons = document.querySelectorAll('.tab-btn');
  const tabContents = document.querySelectorAll('.tab-content');

  tabButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      const targetTab = btn.dataset.tab;

      // Deactivate active ones
      tabButtons.forEach(b => b.classList.remove('active'));
      tabContents.forEach(c => c.classList.remove('active'));

      // Activate selected
      btn.classList.add('active');
      document.getElementById(targetTab).classList.add('active');
    });
  });


  // --- INTERSECTION OBSERVER SCROLL REVEAL ---
  const revealElements = document.querySelectorAll('.scroll-reveal');
  
  const revealObserver = new IntersectionObserver((entries, observer) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('revealed');
        // Unobserve once shown to prevent repeating animation
        observer.unobserve(entry.target);
      }
    });
  }, {
    threshold: 0.15,
    rootMargin: '0px 0px -50px 0px' // triggers slightly before entering viewport
  });

  revealElements.forEach(el => revealObserver.observe(el));

  // Initialize
  loadCart();
});
