const form = document.querySelector("#researchForm");
const submitButton = document.querySelector("#submitButton");
const welcome = document.querySelector("#welcome");
const loading = document.querySelector("#loadingState");
const error = document.querySelector("#errorState");
const reportSection = document.querySelector("#reportSection");
const historyList = document.querySelector("#historyList");
let currentResult = null;
function showError(message) { document.querySelector("#errorMessage").textContent = message; error.hidden = false; }
function hostName(value) { try { return new URL(value).hostname.replace(/^www\./, ""); } catch { return value; } }
function updateHistoryCount() { document.querySelector("#historyCount").textContent = historyList.querySelectorAll(".history-item").length || ""; }
function addHistoryItem(item) {
  const empty = historyList.querySelector(".empty-history"); if (empty) empty.remove();
  const button = document.createElement("button"); button.className = "history-item"; button.dataset.runId = item.run_id; button.title = item.query;
  const dot = document.createElement("span"); dot.className = "history-dot";
  const query = document.createElement("span"); query.className = "history-query"; query.textContent = item.query;
  button.append(dot, query); historyList.prepend(button); updateHistoryCount();
}
function renderReport(result) {
  currentResult = result;
  document.querySelector("#reportTitle").textContent = result.query;
  document.querySelector("#runId").textContent = `· ${result.run_id.slice(0, 8)}`;
  document.querySelector("#reportMeta").textContent = `Saved ${new Date(result.created_at).toLocaleString()} · ${result.sources.length} sources`;
  const body = document.querySelector("#reportBody"); body.replaceChildren();
  for (const part of result.report.split(/(\[S\d+\])/g)) {
    const match = part.match(/^\[S(\d+)\]$/);
    if (match) { const link = document.createElement("a"); link.href = `#source-S${match[1]}`; link.textContent = part; link.setAttribute("aria-label", `Jump to source ${match[1]}`); body.append(link); }
    else body.append(document.createTextNode(part));
  }
  document.querySelector("#sourceCount").textContent = `${result.sources.length} SOURCES`;
  const sourceList = document.querySelector("#sourceList"); sourceList.replaceChildren();
  result.sources.forEach((source) => {
    const card = document.createElement("article"); card.className = "source-card"; card.id = `source-${source.id}`;
    const top = document.createElement("div"); top.className = "source-card-top";
    const id = document.createElement("span"); id.className = "source-id"; id.textContent = `[${source.id}]`; top.append(id);
    if (typeof source.score === "number") { const score = document.createElement("span"); score.className = "source-score"; score.textContent = `${Math.round(source.score * 100)}% match`; top.append(score); }
    const title = document.createElement("a"); title.className = "source-title"; title.href = source.url; title.target = "_blank"; title.rel = "noopener noreferrer"; title.textContent = source.title;
    const domain = document.createElement("div"); domain.className = "source-domain"; domain.textContent = hostName(source.url);
    const excerpt = document.createElement("p"); excerpt.className = "source-excerpt"; excerpt.textContent = source.content;
    card.append(top, title, domain, excerpt); sourceList.append(card);
  });
  reportSection.hidden = false; reportSection.scrollIntoView({ behavior: "smooth", block: "start" });
}
form.addEventListener("submit", async (event) => {
  event.preventDefault(); error.hidden = true; reportSection.hidden = true; loading.hidden = false; submitButton.disabled = true;
  submitButton.querySelector("span:first-child").textContent = "Researching…";
  const steps = [...document.querySelectorAll(".loading-steps .step")]; let active = 0;
  const timer = setInterval(() => { active = Math.min(active + 1, steps.length - 1); steps.forEach((step,index)=>step.classList.toggle("active",index<=active)); document.querySelector("#loadingMessage").textContent = ["Searching trusted sources and mapping the key ideas…","Comparing evidence across the source set…","Writing a grounded report with traceable citations…"][active]; },4500);
  try {
    const response = await fetch("/research", { method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify({query:form.query.value.trim(),depth:form.depth.value,max_results:Number(form.max_results.value)}) });
    const payload = await response.json(); if (!response.ok) throw new Error(payload.detail || "The research request failed.");
    renderReport(payload); addHistoryItem(payload);
  } catch (requestError) { showError(requestError.message || "Check your connection and try again."); }
  finally { clearInterval(timer); loading.hidden = true; submitButton.disabled = false; submitButton.querySelector("span:first-child").textContent = "Build my brief"; }
});
document.querySelectorAll(".prompt-chip").forEach((button)=>button.addEventListener("click",()=>{form.query.value=button.textContent;form.query.focus();}));
document.querySelector("#newResearch").addEventListener("click",()=>{welcome.scrollIntoView({behavior:"smooth"});form.query.focus();});
document.querySelector("#dismissError").addEventListener("click",()=>{error.hidden=true;});
document.querySelector("#downloadButton").addEventListener("click",()=>{
  if(!currentResult)return;
  const sources=currentResult.sources.map(source=>`- [${source.id}] [${source.title}](${source.url})`).join("\n");
  const blob=new Blob([`# ${currentResult.query}\n\n${currentResult.report}\n\n## Sources\n\n${sources}\n`],{type:"text/markdown;charset=utf-8"});
  const url=URL.createObjectURL(blob);const link=document.createElement("a");link.href=url;link.download=`research-brief-${currentResult.run_id.slice(0,8)}.md`;link.click();URL.revokeObjectURL(url);
});
historyList.addEventListener("click",async(event)=>{
  const button=event.target.closest("[data-run-id]");if(!button)return;error.hidden=true;loading.hidden=false;
  try { const response=await fetch(`/research/${encodeURIComponent(button.dataset.runId)}`);const payload=await response.json();if(!response.ok)throw new Error(payload.detail||"Could not load this brief.");renderReport(payload); }
  catch(requestError){showError(requestError.message);}finally{loading.hidden=true;}
});
updateHistoryCount();
