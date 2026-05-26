from app.rag.vector_store import search_knowledge_base
from app.services.langchain_service import run_langchain_agent

def document_assistant_agent(message):

    results = search_knowledge_base(message.query)

    if not results:
        context = "No relevant retail knowledge found."
    else:
        context = "\n".join(
            [item["content"] for item in results]
        )

    response = run_langchain_agent(
        system_role="Document Assistant Agent",
        user_query=message.query,
        context=context
    )

    return response