import os

file_path = "c:\\Users\\Admin\\Documents\\Agentic AI\\frontend\\project.js"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

broken_str = """                        loadProjectAgentsList();
                    } catch (err) {
                        alert('Error deleting agent');
                    }
            createBtn.setAttribute('data-bound', 'true');
            createBtn.addEventListener('click', async () => {"""

fixed_str = """                        loadProjectAgentsList();
                    } catch (err) {
                        alert('Error deleting agent');
                    }
                }
            });

            document.addEventListener('click', (e) => {
                if (!contextMenu.contains(e.target) && !moreBtn.contains(e.target)) {
                    contextMenu.style.display = 'none';
                }
            });

            card.addEventListener('click', async () => {
                activeAgentId = agent.id;
                const agentRes = await authFetch(`/api/agents/${activeAgentId}`);
                activeAgentData = await agentRes.json();
                
                document.getElementById('configAgentTitle').textContent = `Configuring: ${activeAgentData.name}`;
                document.getElementById('agentNameInput').value = activeAgentData.name;
                document.getElementById('agentDescInput').value = activeAgentData.description;
                document.getElementById('personalityPromptInput').value = activeAgentData.system_prompt || '';
                populateAgentModelDropdown();
                
                document.getElementById('agents-list-screen').style.display = 'none';
                document.getElementById('agent-config-screen').style.display = 'flex';
                document.getElementById('saveAgentBtn').style.display = 'block';
                updateAgentAttachedToolsBox();
                
                Array.from(grid.children).forEach(c => c.classList.remove('active-card'));
                card.classList.add('active-card');
            });

            grid.appendChild(card);
        });
        
        // Add create handler
        const createBtn = document.getElementById('projectCreateNewBtn');
        if (createBtn && !createBtn.hasAttribute('data-bound')) {
            createBtn.setAttribute('data-bound', 'true');
            createBtn.addEventListener('click', async () => {"""

if broken_str in content:
    content = content.replace(broken_str, fixed_str)
    print("Fixed corrupted lines.")
else:
    print("Could not find broken string.")

broken_create_str = """                document.getElementById('configAgentTitle').textContent = `Configuring: ${activeAgentData.name}`;
                document.getElementById('agents-list-screen').style.display = 'none';
                document.getElementById('agent-config-screen').style.display = 'flex';
                updateAgentAttachedToolsBox();
            });
        }
    } catch (e) {"""

fixed_create_str = """                document.getElementById('configAgentTitle').textContent = `Configuring: ${activeAgentData.name}`;
                document.getElementById('agents-list-screen').style.display = 'none';
                document.getElementById('agent-config-screen').style.display = 'flex';
                document.getElementById('saveAgentBtn').style.display = 'block';
                updateAgentAttachedToolsBox();
            });
        }
    } catch (e) {"""

if broken_create_str in content:
    content = content.replace(broken_create_str, fixed_create_str)
    print("Added saveAgentBtn block to create custom agent.")
else:
    print("Could not find broken create string.")

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Done.")
