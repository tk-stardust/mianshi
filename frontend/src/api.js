const BASE = "/api";

export async function fetchQuestions(params = {}) {
  const qs = new URLSearchParams(params).toString();
  const res = await fetch(`${BASE}/questions?${qs}`);
  return res.json();
}

export async function fetchQuestion(id) {
  const res = await fetch(`${BASE}/questions/${id}`);
  return res.json();
}

export async function createQuestion(data) {
  const res = await fetch(`${BASE}/questions`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  return res.json();
}

export async function updateQuestion(id, data) {
  const res = await fetch(`${BASE}/questions/${id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  return res.json();
}

export async function deleteQuestion(id) {
  await fetch(`${BASE}/questions/${id}`, { method: "DELETE" });
}

export async function fetchStudy(params = {}) {
  const qs = new URLSearchParams(params).toString();
  const res = await fetch(`${BASE}/study?${qs}`);
  return res.json();
}

export async function fetchFilters() {
  const res = await fetch(`${BASE}/filters`);
  return res.json();
}

export async function fetchStats() {
  const res = await fetch(`${BASE}/stats`);
  return res.json();
}

export async function toggleFavorite(id, favorite) {
  return updateQuestion(id, { favorite });
}

export async function batchFavorite(ids, favorite) {
  const results = [];
  for (const id of ids) {
    results.push(await updateQuestion(id, { favorite }));
  }
  return results;
}

export async function fetchExport(params = {}) {
  const clean = {};
  for (const [k, v] of Object.entries(params)) {
    if (v !== undefined && v !== null && v !== "") clean[k] = v;
  }
  const qs = new URLSearchParams(clean).toString();
  const res = await fetch(`${BASE}/export?${qs}`);
  return res.json();
}

export async function fetchExportMd(params = {}) {
  const clean = {};
  for (const [k, v] of Object.entries(params)) {
    if (v !== undefined && v !== null && v !== "") clean[k] = v;
  }
  const qs = new URLSearchParams(clean).toString();
  const res = await fetch(`${BASE}/export/md?${qs}`);
  return res.text();
}

export async function importQuestions(data) {
  const res = await fetch(`${BASE}/import`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  return res.json();
}

export async function fetchKnowledge() {
  const res = await fetch(`${BASE}/knowledge`);
  return res.json();
}
