const translations = {
  en: {
    sending: "Sending...",
    sent: "Message sent — thank you!",
    unable: "Unable to send message.",
    failed: "Send failed. Please try again later.",
  },
  fr: {
    sending: "Envoi...",
    sent: "Message envoyé — merci !",
    unable: "Impossible d'envoyer le message.",
    failed: "L'envoi a échoué. Veuillez réessayer plus tard.",
  },
};

const form = document.getElementById("contact-form");
const status = document.getElementById("contact-form-status");
const lang = document.documentElement.lang?.slice(0, 2).toLowerCase() || "en";
const texts = translations[lang] || translations.en;

window.addEventListener("load", async () => {
  try {
    await fetch("/api/visit", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        path: window.location.pathname,
        lang,
        title: document.title,
        referrer: document.referrer || undefined,
      }),
    });
  } catch {
    // visit logging is non-blocking
  }
});

form?.addEventListener("submit", async (event) => {
  event.preventDefault();

  const submitButton = form.querySelector('button[type="submit"]');
  if (submitButton) {
    submitButton.disabled = true;
  }

  status.textContent = texts.sending;
  status.className = "contact-form-status";

  const data = {
    name: form.name.value.trim(),
    email: form.email.value.trim(),
    subject: form.subject.value.trim(),
    message: form.message.value.trim(),
  };

  try {
    const response = await fetch("/api/contact", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    });

    const body = await response.json();

    if (!response.ok)
      throw new Error(body.detail || body.message || texts.unable);

    status.textContent = texts.sent;
    status.classList.add("success");

    form.reset();
  } catch (error) {
    status.textContent = error.message || texts.failed;
    status.classList.add("error");
  } finally {
    if (submitButton) {
      submitButton.disabled = false;
    }
  }
});
