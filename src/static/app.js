document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");

  // Function to fetch activities from API
  async function fetchActivities() {
    try {
      const response = await fetch("/activities");
      const activities = await response.json();

      // Clear loading message
      activitiesList.innerHTML = "";

      // Populate activities list
      Object.entries(activities).forEach(([name, details]) => {
        const activityCard = document.createElement("div");
        activityCard.className = "activity-card";

        const spotsLeft = details.max_participants - details.participants.length;

        activityCard.innerHTML = `
          <h4>${name}</h4>
          <p>${details.description}</p>
          <p><strong>Schedule:</strong> ${details.schedule}</p>
          <p><strong>Availability:</strong> ${spotsLeft} spots left</p>
          <div class="participants-section">
            <strong>Participants:</strong>
            <ul class="participants-list" data-activity="${name}">
            </ul>
          </div>
        `;

        activitiesList.appendChild(activityCard);

        // Populate participants list
        const participantsList = activityCard.querySelector(".participants-list");
        if (details.participants.length > 0) {
          details.participants.forEach((participant) => {
            const li = document.createElement("li");
            li.className = "participant-item";
            li.innerHTML = `
              <span class="participant-name">${participant}</span>
              <button class="delete-btn" data-email="${participant}" data-activity="${name}" aria-label="Remove ${participant}">
                <span class="delete-icon">✕</span>
              </button>
            `;
            participantsList.appendChild(li);
          });
        } else {
          const li = document.createElement("li");
          li.innerHTML = "<em>No participants yet</em>";
          participantsList.appendChild(li);
        }

        // Add option to select dropdown
        const option = document.createElement("option");
        option.value = name;
        option.textContent = name;
        activitySelect.appendChild(option);
      });
    } catch (error) {
      activitiesList.innerHTML = "<p>Failed to load activities. Please try again later.</p>";
      console.error("Error fetching activities:", error);
    } 
  }

  // Handle participant deletion
  activitiesList.addEventListener("click", async (event) => {
    if (!event.target.closest(".delete-btn")) return;

    const deleteBtn = event.target.closest(".delete-btn");
    const participantItem = deleteBtn.closest(".participant-item");
    const participantsList = deleteBtn.closest(".participants-list");

    // Remove the participant from the list
    participantItem.remove();

    // If no more participants, show "No participants yet"
    if (participantsList.children.length === 0) {
      const li = document.createElement("li");
      li.innerHTML = "<em>No participants yet</em>";
      participantsList.appendChild(li);
    }
  });

  // Handle form submission
  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const activity = document.getElementById("activity").value;

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/signup?email=${encodeURIComponent(email)}`,
        {
          method: "POST",
        }
      );

      const result = await response.json();

      if (response.ok) {
        messageDiv.textContent = result.message;
        messageDiv.className = "success";
        signupForm.reset();
        // Refresh activities to show the new participant
        fetchActivities();
      } else {
        messageDiv.textContent = result.detail || "An error occurred";
        messageDiv.className = "error";
      }

      messageDiv.classList.remove("hidden");

      // Hide message after 5 seconds
      setTimeout(() => {
        messageDiv.classList.add("hidden");
      }, 5000);
    } catch (error) {
      messageDiv.textContent = "Failed to sign up. Please try again.";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      console.error("Error signing up:", error);
    }
  });

  // Initialize app
  fetchActivities();
});
