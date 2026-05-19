from pathlib import Path

from debate_simulator.skills.router_skill import RouterSkill


def test_router_skill_selects_matching_skill_description(tmp_path: Path) -> None:
    """Router selects a skill by matching context to skill description text."""
    skill_dir = tmp_path / "web_search"
    skill_dir.mkdir()
    (skill_dir / "skill.md").write_text("name: web_search\ndescription: search the web", encoding="utf-8")

    result = RouterSkill(skills_path=tmp_path).execute({"context": "please search the web"})

    assert result.data == {"skill": "web_search"}
