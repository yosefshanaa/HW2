from debate_simulator.skills.argument_builder.skill import ArgumentBuilderSkill
from debate_simulator.skills.fact_check.skill import FactCheckSkill
from debate_simulator.skills.rag_retrieve.skill import RagRetrieveSkill
from debate_simulator.skills.rag_store.skill import RagStoreSkill
from debate_simulator.skills.rebuttal_builder.skill import RebuttalBuilderSkill
from debate_simulator.skills.rebuttal_check.skill import RebuttalCheckSkill
from debate_simulator.skills.respect_check.skill import RespectCheckSkill
from debate_simulator.skills.stance_check.skill import StanceCheckSkill
from debate_simulator.skills.web_search.skill import WebSearchSkill


class FakeSearch:
    """Search test double."""

    def search(self, query: str):
        """Return one result."""
        return [{"title": query}]


class FakeLlm:
    """LLM test double."""

    def complete(self, prompt: str) -> str:
        """Echo a deterministic response."""
        return f"llm:{prompt[:6]}"


class FakeStore:
    """Vector store test double."""

    def __init__(self) -> None:
        """Create empty storage."""
        self.documents: list[str] = []

    def add(self, documents, embeddings, metadatas):
        """Store documents."""
        self.documents.extend(documents)

    def query(self, embeddings, top_k: int):
        """Return stored documents."""
        return self.documents[:top_k]


class FakeEmbedder:
    """Embedder test double."""

    def embed(self, texts: list[str]):
        """Return deterministic embeddings."""
        return [[float(len(text))] for text in texts]


def test_web_search_skill_executes_search() -> None:
    """WebSearchSkill returns search results."""
    result = WebSearchSkill(searcher=FakeSearch()).execute({"query": "topic"})

    assert result.data == {"results": [{"title": "topic"}]}


def test_rag_store_skill_chunks_embeds_and_stores() -> None:
    """RagStoreSkill stores chunked documents."""
    store = FakeStore()
    skill = RagStoreSkill(store=store, embedder=FakeEmbedder(), chunk_size=2, chunk_overlap=1)

    result = skill.execute({"text": "alpha beta gamma", "source": "unit"})

    assert result.data == {"stored": 2} and store.documents == ["alpha beta", "beta gamma"]


def test_rag_retrieve_skill_queries_store() -> None:
    """RagRetrieveSkill embeds the query and retrieves documents."""
    store = FakeStore()
    store.documents = ["alpha", "beta"]

    result = RagRetrieveSkill(store=store, embedder=FakeEmbedder()).execute(
        {"query": "alpha", "top_k": 1}
    )

    assert result.data == {"documents": ["alpha"]}


def test_fact_check_skill_uses_llm() -> None:
    """FactCheckSkill delegates verification to the LLM client."""
    result = FactCheckSkill(llm_client=FakeLlm()).execute({"claim": "Earth is round"})

    assert result.data == {"verdict": "llm:Verify"}


def test_stance_check_skill_detects_contradiction() -> None:
    """StanceCheckSkill flags simple stance contradiction."""
    result = StanceCheckSkill().execute({"stance": "pro", "text": "I argue against this policy"})

    assert result.data == {"contradiction": True}


def test_respect_check_skill_detects_disallowed_terms() -> None:
    """RespectCheckSkill flags configured disrespect terms."""
    result = RespectCheckSkill(disallowed_terms=["insult"]).execute({"text": "that is an insult"})

    assert result.data == {"respectful": False, "matches": ["insult"]}


def test_rebuttal_check_skill_detects_missing_overlap() -> None:
    """RebuttalCheckSkill flags responses that ignore the previous argument."""
    result = RebuttalCheckSkill().execute({"previous": "tax policy", "response": "sports culture"})

    assert result.data == {"addressed": False}


def test_argument_builder_skill_uses_llm() -> None:
    """ArgumentBuilderSkill builds arguments through the LLM client."""
    result = ArgumentBuilderSkill(llm_client=FakeLlm()).execute({"topic": "AI", "stance": "pro"})

    assert result.data == {"argument": "llm:Build "}


def test_rebuttal_builder_skill_uses_llm() -> None:
    """RebuttalBuilderSkill builds rebuttals through the LLM client."""
    result = RebuttalBuilderSkill(llm_client=FakeLlm()).execute(
        {"opponent_argument": "AI is risky"}
    )

    assert result.data == {"rebuttal": "llm:Rebut "}


def test_argument_builder_completes_prompt_passthrough() -> None:
    """A supplied prompt is completed directly, bypassing internal composition."""
    result = ArgumentBuilderSkill(llm_client=FakeLlm()).execute({"prompt": "PROMPT"})

    assert result.data == {"argument": "llm:PROMPT"}


def test_rebuttal_builder_completes_prompt_passthrough() -> None:
    """A supplied prompt is completed directly, bypassing internal composition."""
    result = RebuttalBuilderSkill(llm_client=FakeLlm()).execute({"prompt": "PROMPT"})

    assert result.data == {"rebuttal": "llm:PROMPT"}
