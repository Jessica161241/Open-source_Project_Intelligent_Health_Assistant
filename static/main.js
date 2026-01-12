function analyzeRepo() {
  const repo_name = document.getElementById('repo_name').value;
  fetch('/analyze', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: `repo_name=${encodeURIComponent(repo_name)}`
  }).then(res => res.json()).then(data => {
    if(data.error) { alert(data.error); return; }
    updateRadar(data.scores);

    const suggestionsDiv = document.getElementById('suggestions');
    suggestionsDiv.innerHTML = '<h3>改进建议</h3>';
    data.suggestions.forEach(s => {
      let cls = s.priority==='高'?'priority-high':s.priority==='中'?'priority-medium':'priority-low';
      suggestionsDiv.innerHTML += `<div class="suggestion ${cls}">[${s.priority}] ${s.text}</div>`;
    });
  });
}
