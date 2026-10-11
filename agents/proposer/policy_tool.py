from langchain_core.tools import tool
from agents.retrieval.retrieve import retrieve


@tool
def search_policies(question: str) -> str:
    """Searches freight policy documents (fuel surcharge formula, accessorial
    fees like liftgate or residential delivery, claims rules, service levels).
    Returns the most relevant policy excerpts with their source file and
    relevance scores. Use this for policy questions, not for carrier rates."""
    results = retrieve(question)

    sections = []
    for chunk_text, source_file, semantic_score, keyword_score in results:
        sections.append(
            f"[source: {source_file} | semantic={semantic_score:.3f} | keyword={keyword_score:.3f}]\n"
            f"{chunk_text}"
        )
    return "\n\n---\n\n".join(sections)


if __name__ == "__main__":
    print("Tool name:", search_policies.name)
    print("Description:", search_policies.description)
    print("Args:", search_policies.args)
    print()
    print(search_policies.invoke({"question": "what is the liftgate fee"}))
