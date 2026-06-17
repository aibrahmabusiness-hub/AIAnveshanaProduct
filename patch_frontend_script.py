import re

with open('frontend/script.js', 'r', encoding='utf-8') as f:
    text = f.read()

original_js = """
        data.projects.forEach(project => {
            const card = document.createElement('div');
            card.classList.add('project-card');
            card.innerHTML = `
                <div class="card-header-row" style="display:flex; justify-content:space-between; align-items:center; width:100%;">
                    <div class="agent-title">${project.name}</div>
                </div>
                <div class="agent-desc">
                    <span>${project.description}</span>
                </div>
            `;
            card.addEventListener('click', () => { window.location.href = `/project/${project.id}`; });
            projectsGrid.appendChild(card);
        });
"""

new_js = """
        data.projects.forEach(project => {
            const card = document.createElement('div');
            card.classList.add('project-card');
            card.innerHTML = `
                <div class="card-header-row" style="display:flex; justify-content:space-between; align-items:center; width:100%;">
                    <div class="agent-title">${project.name}</div>
                    <button class="delete-project-btn" data-id="${project.id}" style="background:none; border:none; cursor:pointer; color:#ef4444; padding:4px; border-radius:4px;" title="Delete Project">
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>
                    </button>
                </div>
                <div class="agent-desc">
                    <span>${project.description}</span>
                </div>
            `;
            
            // Handle card click
            card.addEventListener('click', (e) => { 
                // Ignore clicks on the delete button
                if (e.target.closest('.delete-project-btn')) return;
                window.location.href = `/project/${project.id}`; 
            });
            
            // Handle delete button click
            const delBtn = card.querySelector('.delete-project-btn');
            if (delBtn) {
                delBtn.addEventListener('click', async (e) => {
                    e.stopPropagation();
                    if (confirm(`Are you sure you want to delete the project "${project.name}" and ALL of its related agents, workflows, knowledge base documents, and chat history? This action cannot be undone.`)) {
                        try {
                            const delRes = await authFetch(`/api/projects/${project.id}`, { method: 'DELETE' });
                            if (delRes.ok) {
                                card.remove();
                            } else {
                                alert("Failed to delete project.");
                            }
                        } catch (err) {
                            console.error("Error deleting project:", err);
                            alert("An error occurred while deleting the project.");
                        }
                    }
                });
            }
            
            projectsGrid.appendChild(card);
        });
"""

# The exact indentation might differ, so we'll do a regex replacement or find a smaller anchor.
# Let's replace the content.
import textwrap

def normalize_ws(s):
    return re.sub(r'\s+', ' ', s.strip())

# We can search for the start and end anchors and replace the text between them.
start_anchor = "data.projects.forEach(project => {"
end_anchor = "projectsGrid.appendChild(card);"
end_anchor_2 = "});"

start_idx = text.find(start_anchor)
if start_idx != -1:
    end_idx = text.find(end_anchor_2, start_idx + len(start_anchor))
    if end_idx != -1:
        full_end_idx = end_idx + len(end_anchor_2)
        text = text[:start_idx] + new_js.strip() + text[full_end_idx:]
        with open('frontend/script.js', 'w', encoding='utf-8') as f:
            f.write(text)
        print("Patched script.js successfully")
    else:
        print("End anchor not found")
else:
    print("Start anchor not found")
