(() => {
  const menuButton = document.querySelector(".menu-toggle");
  const navigation = document.getElementById("primary-nav");
  if (menuButton && navigation) {
    const closeNavigation = () => {
      menuButton.setAttribute("aria-expanded", "false");
      navigation.classList.remove("is-open");
    };
    menuButton.addEventListener("click", () => {
      const isOpen = menuButton.getAttribute("aria-expanded") !== "true";
      menuButton.setAttribute("aria-expanded", String(isOpen));
      navigation.classList.toggle("is-open", isOpen);
    });
    navigation.addEventListener("click", (event) => {
      if (event.target.closest("a")) closeNavigation();
    });
    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape") closeNavigation();
    });
  }

  document.querySelectorAll(".sidebar-mobile-toggle").forEach((toggle) => {
    const sidebar = toggle.closest(".marketplace-sidebar");
    const content = sidebar?.querySelector(".sidebar-content");
    if (!sidebar || !content) return;

    const setSidebarOpen = (isOpen) => {
      toggle.setAttribute("aria-expanded", String(isOpen));
      sidebar.classList.toggle("is-open", isOpen);
    };
    toggle.addEventListener("click", () => {
      setSidebarOpen(toggle.getAttribute("aria-expanded") !== "true");
    });
    content.addEventListener("click", (event) => {
      if (event.target.closest("a")) setSidebarOpen(false);
    });
    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape" && toggle.getAttribute("aria-expanded") === "true") {
        setSidebarOpen(false);
        toggle.focus();
      }
    });
  });

  const chat = document.getElementById("chat");
  const chatOpen = document.getElementById("chatOpen");
  const chatClose = document.getElementById("chatClose");
  const chatLog = document.getElementById("chatLog");
  const chatForm = document.getElementById("chatForm");
  const chatText = document.getElementById("chatText");
  const csrfToken = document.querySelector("[name=csrfmiddlewaretoken]")?.value;

  const setChatOpen = (isOpen) => {
    if (!chat || !chatOpen) return;
    chat.classList.toggle("is-open", isOpen);
    chat.setAttribute("aria-hidden", String(!isOpen));
    chatOpen.setAttribute("aria-expanded", String(isOpen));
    if (isOpen) chatText?.focus();
  };
  chatOpen?.addEventListener("click", () => {
    setChatOpen(!chat?.classList.contains("is-open"));
  });
  chatClose?.addEventListener("click", () => setChatOpen(false));
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && chat?.classList.contains("is-open")) {
      setChatOpen(false);
      chatOpen?.focus();
    }
  });

  const appendMessage = (message, className) => {
    if (!chatLog) return;
    const bubble = document.createElement("p");
    bubble.className = `chat-bubble ${className}`;
    bubble.textContent = message;
    chatLog.appendChild(bubble);
    chatLog.scrollTop = chatLog.scrollHeight;
  };

  chatForm?.addEventListener("submit", async (event) => {
    event.preventDefault();
    const message = chatText?.value.trim();
    const submitButton = chatForm.querySelector("button[type=submit]");
    if (!message || !submitButton) return;

    appendMessage(message, "user");
    chatText.value = "";
    submitButton.disabled = true;
    try {
      const response = await fetch("/assistant/message/", {
        method: "POST",
        credentials: "same-origin",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrfToken || "",
        },
        body: JSON.stringify({ message }),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || "The assistant could not process that message.");
      appendMessage(data.reply, "bot");
    } catch (error) {
      console.error("GateXKart assistant request failed:", error);
      appendMessage(error.message || "The assistant is unavailable. Please email info@gatexkart.com.", "bot");
    } finally {
      submitButton.disabled = false;
      chatText?.focus();
    }
  });

  const slider = document.getElementById("heroSlider");
  if (slider) {
    const slides = [...slider.querySelectorAll(".hero-slide")];
    const dots = [...slider.querySelectorAll(".hero-dots button")];
    if (slides.length > 1 && !window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
      let activeIndex = 0;
      let timer;
      const showSlide = (nextIndex) => {
        activeIndex = (nextIndex + slides.length) % slides.length;
        slides.forEach((slide, index) => slide.classList.toggle("active", index === activeIndex));
        dots.forEach((dot, index) => dot.classList.toggle("active", index === activeIndex));
      };
      const startRotation = () => {
        window.clearInterval(timer);
        timer = window.setInterval(() => showSlide(activeIndex + 1), 6000);
      };
      dots.forEach((dot, index) => dot.addEventListener("click", () => {
        showSlide(index);
        startRotation();
      }));
      slider.addEventListener("mouseenter", () => window.clearInterval(timer));
      slider.addEventListener("mouseleave", startRotation);
      startRotation();
    }
  }
})();
