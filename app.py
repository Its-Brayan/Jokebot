from pydantic import BaseModel
from typing import Annotated, List, Literal
from operator import add
from pyjokes import get_joke
from langgraph.graph import StateGraph,END
from langgraph.graph.state import CompiledStateGraph
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os
from config_loader import load_write_config, load_config
load_dotenv()
#Define the state
config1 = load_config("config.yaml")
write_critic_config = load_write_config("joker_write.yaml")
llm = ChatGroq(
            model=config1['llm'],
            api_key=os.getenv('GROQ_API_KEY'),
            temperature=0.0,
        )
class Joke(BaseModel):
    text: str
    category: str
    language: str

class JokeState(BaseModel):
    jokes: Annotated[List[Joke], add] = []
    jokes_choice : Literal["n","c", "l", "r", "q"] = "n"
    category : str = "neutral"
    language : str = "en"
    quit : bool = False
    latest_joke: str = ""
    approved: bool = False
    retry_count: int = 0

def make_writer_node():
    def writer_node(state:JokeState) -> dict:
        config = write_critic_config['joke_writer_cfg']
        prompt = f"{config}"
        prompt += f"the category is {state.category}"
        response = llm.invoke(prompt)
        return {"latest_joke":response.content}
    return writer_node

def make_critic_node():
    def critic_node(state:JokeState) -> dict:
        config = write_critic_config['joke_critic_cfg']
        prompt = f"{config}"
        prompt += f"the joke is {state.latest_joke}"
        decision = llm.invoke(prompt).content.strip().lower()
        approved = "yes" in decision
        return{"approved":approved,"retry_count":state.retry_count+1}
    return critic_node

def show_final_joke(state:JokeState) -> dict:
    joke = Joke(text=state.latest_joke,category=state.category,language=state.language)
    print(joke)
    return {"jokes":[joke],"retry_count":0,"approved":False,"latest_joke":""}

def write_critic_router(state:JokeState) -> str:
    if state.approved or state.retry_count > 5:
        return "show_final_joke"

def update_categories(state:JokeState) -> dict:
    categories = ["dad developer", "chuck norris developer", "general"]
    emoji_map = {
         "knock-knock": "🚪",
        "dad developer": "👨‍💻",
        "chuck norris developer": "🥋",
        "general": "🎯",
    }
    print("📂" + "=" * 58 + "📂")
    print("    CATEGORY SELECTION")
    print("=" * 60)
    for i, cat in enumerate(categories):
        emoji = emoji_map.get(cat, "📂")
        print(f"    {i}. {emoji} {cat.upper()}")
    
    print("=" * 60)
    try:
        selection = int(input("Enter category number").strip())
        if 0 <= selection < len(categories):
            selected_category = categories[selection]
            print(f"    ✅ Category changed to: {selected_category.upper()}")
            return {"category": selected_category}
        else:
              print("    ❌ Invalid choice. Keeping current category.")
              return {}
    except ValueError:
        print("    ❌ Invalid input. Please enter a number.")
        return {}


def show_menu(state: JokeState) -> dict:
    user_input = input("[n] Next  [c] Category  [l] Language [r] Reset [q] Quit\n> ").strip().lower()
    return {"jokes_choice":user_input}

def exit_bot(state:JokeState) -> dict:
    return {'quit':True}

def route_choice(state:JokeState) -> dict:
    if state.jokes_choice == "n":
        return "fetch_joke"
    elif state.jokes_choice == "c":
        return "update_category"
    elif state.jokes_choice == "l":
        return "update_language"
    elif state.jokes_choice == "r":
        return "reset_jokes"
    elif state.jokes_choice == "q":
        return "exit_bot"
    return "exit_bot"

def build_joke_graph() -> CompiledStateGraph:
    workflow = StateGraph(JokeState)
    workflow.add_node("show_menu",show_menu)
    workflow.add_node("writer",make_writer_node())
    workflow.add_node("critic",make_critic_node())
    workflow.add_node("update_category",update_categories)
    workflow.add_node("show_final_joke",show_final_joke)
    workflow.add_node("exit_bot",exit_bot)

    workflow.set_entry_point("show_menu")
    workflow.add_conditional_edges(
        "show_menu",
        route_choice,
        {
            "fetch_joke":"writer",
            "update_category":"update_category",
            "exit_bot":"exit_bot"
        }
    )
    workflow.add_edge("writer","critic")
    workflow.add_edge("update_category","show_menu")
    workflow.add_conditional_edges(
        "critic",
        write_critic_router,
        {
            "writer":"writer","show_final_joke":"show_final_joke"
        }
    )
    workflow.add_edge("show_final_joke","show_menu")
    workflow.add_edge("exit_bot",END)
    return workflow.compile()

def main():
    graph = build_joke_graph()
    final_state = graph.invoke(JokeState(category='dad developer'),config={'recursion_limit':200})
    print("\n✅ Done. Final Joke Count:", len(final_state["jokes"]))
    

if __name__ == "__main__":
    main()


# def fetch_joke(state:JokeState) -> dict:
#     joke_text = get_joke(language=state.language,category=state.category)
#     new_joke = Joke(text=joke_text, category=state.category, language=state.language)
#     print("\n😂 Joke:")
#     print(joke_text, "\n")

#     return {"jokes": [new_joke]}


# def update_category(state:JokeState) -> dict:
#     categories = ["neutral","chuck","all"]
#     selection = int(input("select category [0=neutral, 1=chuck,2=all]:").strip())
    
#     return{"category":categories[selection]}

# def update_language(state:JokeState) -> dict:
#     languages = ["en","es","de"]
#     selection = int(input("select language [0=en, 1=es, 2=de]:").strip())
#     return{"language":languages[selection]}

# def reset_jokes(state:JokeState) -> dict:
#     print("Resetting jokes history...")
#     return {"jokes": []}


# def build_joke_graph() -> CompiledStateGraph:
#     workflow = StateGraph(JokeState)
#     workflow.add_node("show_menu",show_menu)
#     workflow.add_node("fetch_joke",fetch_joke)
#     workflow.add_node("update_category",update_category)
#     workflow.add_node("update_language",update_language)
#     workflow.add_node("reset_jokes",reset_jokes)
#     workflow.add_node("exit_bot",exit_bot)

#     workflow.set_entry_point("show_menu")

#     workflow.add_conditional_edges(
#         "show_menu",
#         route_choice,
#         {
#             "fetch_joke":"fetch_joke",
#             "update_category":"update_category",
#             "update_language":"update_language",
#             "reset_jokes":"reset_jokes",
#             "exit_bot":"exit_bot"
#         }
#     )
#     workflow.add_edge("fetch_joke","show_menu")
#     workflow.add_edge("update_category","show_menu")
#     workflow.add_edge("update_language","show_menu")
#     workflow.add_edge("reset_jokes","show_menu")
#     workflow.add_edge("exit_bot",END)

#     return workflow.compile()

# def main():
#     graph = build_joke_graph()
#     final_state = graph.invoke(JokeState(),config={"recursion_limit":100})
#     return final_state

# if __name__ == "__main__":
#     main()