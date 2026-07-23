from vcos.agents.root_agent import root_agent


def test_root_agent_has_both_sub_agents():
    sub_agent_names = {sa.name for sa in root_agent.sub_agents}
    assert sub_agent_names == {"calendar_agent", "email_agent"}


def test_root_agent_has_no_direct_tools_of_its_own():
    # Phase 1 root agent purely routes; it shouldn't have its own tools that
    # could bypass the propose-not-execute pattern in the sub-agents
    assert root_agent.tools == []


def test_root_agent_name_and_description():
    assert root_agent.name == "root_agent"
    assert "calendar" in root_agent.description.lower()
    assert "email" in root_agent.description.lower()