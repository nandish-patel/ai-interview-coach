async function generateQuestions() {
  const role = document.getElementById("role").value;
  const level = document.getElementById("level").value;
  const question_type = document.getElementById("questionType").value;
  const count = document.getElementById("count").value;
  const status = document.getElementById("generateStatus");
  const questionsDiv = document.getElementById("questions");

  status.textContent = "Generating questions...";
  questionsDiv.innerHTML = "";

  try {
    const res = await fetch("/generate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ role, level, question_type, count })
    });

    const data = await res.json();

    if (!res.ok || data.error) {
      throw new Error(data.error || "Something went wrong");
    }

    status.textContent = "Questions generated successfully.";
    renderQuestions(data.questions);
  } catch (err) {
    status.textContent = "";
    questionsDiv.innerHTML = `<p class="error">${err.message}</p>`;
  }
}

let generatedQuestions = [];

function escapeHtml(text) {
  return String(text)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

function renderQuestions(questions) {
  const questionsDiv = document.getElementById("questions");
  generatedQuestions = questions || [];

  if (!generatedQuestions.length) {
    questionsDiv.innerHTML = "No questions were returned. Try generating again.";
    questionsDiv.classList.add("empty");
    return;
  }

  questionsDiv.classList.remove("empty");
  questionsDiv.innerHTML = generatedQuestions.map((q, index) => `
    <div class="question-item" data-question-index="${index}">
      <h3>Question ${index + 1}</h3>
      <p>${escapeHtml(q.question)}</p>
      <p class="points"><strong>Ideal points:</strong> ${escapeHtml((q.ideal_points || []).join(", "))}</p>
      <button type="button" class="answer-this-btn" data-question-index="${index}">Answer This</button>
    </div>
  `).join("");
}

function selectQuestion(question, index) {
  console.log("Answer This button clicked");

  if (!question) {
    console.warn("No question found for index:", index);
    return;
  }

  const selectedQuestionEl = document.getElementById("selectedQuestion");
  const answerEl = document.getElementById("answer");
  const answerSection = document.getElementById("answerSection");
  const evaluateStatus = document.getElementById("evaluateStatus");

  selectedQuestionEl.value = question;
  evaluateStatus.textContent = "";

  document.querySelectorAll(".question-item.selected").forEach((item) => {
    item.classList.remove("selected");
  });

  const selectedItem = document.querySelector(
    `.question-item[data-question-index="${index}"]`
  );
  if (selectedItem) {
    selectedItem.classList.add("selected");
  }

  if (answerSection) {
    answerSection.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  answerEl.focus();
}

function setupAnswerThisDelegation() {
  const questionsDiv = document.getElementById("questions");
  if (!questionsDiv) {
    console.warn("Questions container not found");
    return;
  }

  questionsDiv.addEventListener("click", (event) => {
    const button = event.target.closest(".answer-this-btn");
    if (!button) {
      return;
    }

    const index = Number.parseInt(button.dataset.questionIndex, 10);
    const question = generatedQuestions[index]?.question;
    selectQuestion(question, index);
  });
}

async function evaluateAnswer() {
  const role = document.getElementById("role").value || "Software Engineer";
  const question = document.getElementById("selectedQuestion").value;
  const answer = document.getElementById("answer").value;
  const status = document.getElementById("evaluateStatus");
  const feedbackDiv = document.getElementById("feedback");

  status.textContent = "Evaluating your answer...";
  feedbackDiv.innerHTML = "";

  try {
    const res = await fetch("/evaluate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ role, question, answer })
    });

    const data = await res.json();

    if (!res.ok || data.error) {
      throw new Error(data.error || "Something went wrong");
    }

    status.textContent = "Feedback ready.";
    renderFeedback(data);
  } catch (err) {
    status.textContent = "";
    feedbackDiv.innerHTML = `<p class="error">${err.message}</p>`;
  }
}

function listItems(items) {
  return (items || []).map(item => `<li>${escapeHtml(item)}</li>`).join("");
}

function renderFeedback(data) {
  const feedbackDiv = document.getElementById("feedback");

  feedbackDiv.innerHTML = `
    <div class="score">${escapeHtml(data.score)}/10</div>

    <h3>Strengths</h3>
    <ul>${listItems(data.strengths)}</ul>

    <h3>Improvements</h3>
    <ul>${listItems(data.improvements)}</ul>

    <h3>Better Sample Answer</h3>
    <p>${escapeHtml(data.better_answer)}</p>

    <h3>Confidence Tip</h3>
    <p>${escapeHtml(data.confidence_tip)}</p>
  `;
}

document.addEventListener("DOMContentLoaded", () => {
  setupAnswerThisDelegation();
});
