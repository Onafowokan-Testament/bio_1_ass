function detectTypeFromText(sequenceText) {
  const seq = sequenceText.toUpperCase().replace(/\s+/g, "");
  if (!seq) return "unknown";

  const dnaAllowed = /^[ACGT]+$/;
  const rnaAllowed = /^[ACGU]+$/;

  if (dnaAllowed.test(seq)) return "DNA";
  if (rnaAllowed.test(seq)) return "RNA";
  return "invalid";
}

function toggleStrandSection() {
  const textArea = document.getElementById("sequence_text");
  const strandSection = document.getElementById("strand-section");

  const detected = detectTypeFromText(textArea.value);
  if (detected === "DNA" || detected === "unknown") {
    strandSection.style.display = "block";
  } else {
    strandSection.style.display = "none";
  }
}

function setupDragAndDrop() {
  const dropZone = document.getElementById("drop-zone");
  const fileInput = document.getElementById("sequence_file");

  ["dragenter", "dragover", "dragleave", "drop"].forEach((eventName) => {
    dropZone.addEventListener(eventName, (e) => {
      e.preventDefault();
      e.stopPropagation();
    });
  });

  ["dragenter", "dragover"].forEach((eventName) => {
    dropZone.addEventListener(eventName, () => {
      dropZone.classList.add("drag-active");
    });
  });

  ["dragleave", "drop"].forEach((eventName) => {
    dropZone.addEventListener(eventName, () => {
      dropZone.classList.remove("drag-active");
    });
  });

  dropZone.addEventListener("drop", (e) => {
    const files = e.dataTransfer.files;
    if (!files || files.length === 0) {
      return;
    }

    const dt = new DataTransfer();
    dt.items.add(files[0]);
    fileInput.files = dt.files;
    dropZone.textContent = `Selected: ${files[0].name}`;
  });
}

document.addEventListener("DOMContentLoaded", () => {
  const textArea = document.getElementById("sequence_text");
  textArea.addEventListener("input", toggleStrandSection);

  setupDragAndDrop();
  toggleStrandSection();
});
