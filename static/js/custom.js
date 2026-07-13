document.addEventListener('DOMContentLoaded', function() {
  var headings = document.querySelectorAll('.resume-biography h2');
  headings.forEach(function(h) { h.style.display = 'none'; });
  var icons = document.querySelectorAll('.resume-biography .about-icon');
  icons.forEach(function(i) { i.style.display = 'none'; });
});
document.addEventListener('DOMContentLoaded', function() {
  document.querySelectorAll('a[href*="resume.pdf"]').forEach(function(link) {
    link.setAttribute('target', '_blank');
    link.setAttribute('rel', 'noopener');
  });
});
