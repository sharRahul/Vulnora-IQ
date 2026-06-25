from webui import agent_lab


def test_project_id_accepts_real_names():
    assert agent_lab.normalise_project_id("realagent") == "realagent"
