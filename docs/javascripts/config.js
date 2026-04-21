document.addEventListener("DOMContentLoaded", function() {
  var script = document.createElement("script");
  script.src = "https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js";
  script.onload = function() {
    mermaid.initialize({
      startOnLoad: true,
      securityLevel: "loose",
      theme: "neutral",
      flowchart: {
        useMaxWidth: true,
        htmlLabels: true
      }
    });
  };
  document.head.appendChild(script);
});