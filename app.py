from pydantic import BaseModel
from typing import Annotated, List, Literal
from operator import add
from pyjokes import get_joke
from langgraph.graph import StateGraph,END
from langgraph.graph.state import CompiledStateGraph


#Define the state
class Joke(BaseModel):
    text: str
    category: str

class JokeState(BaseModel):
    jokes: Annotated[List[Joke], add] = []
    jokes_choice : Literal["n","c","q"] = "n"
    category : str = "neutral"
    language : str = "en"
    quit : bool = False

def show_menu(state: JokeState) -> dict:
    user_input = input("[n] Next  [c] Category  [q] Quit\n> ").strip().lower()
    return {"jokes_choice":user_input}

def fetch_joke(state:JokeState) -> dict:
    joke_text = get_joke(language=state.language,category=state.category)
    new_joke = Joke(text=joke_text, category=state.category)
    print("\n😂 Joke:")
    print(joke_text, "\n")

    return {"jokes": [new_joke]}


def update_category(state:JokeState) -> dict:
    categories = ["neutral","chuck","all"]
    selection = int(input("select category [0=neutral, 1=chuck,2=all]:").strip())
    return{"category":categories[selection]}


def exit_bot(state:JokeState) -> dict:
    return {'quit':True}

def route_choice(state:JokeState) -> dict:
    if state.jokes_choice == "n":
        return "fetch_joke"
    elif state.jokes_choice == "c":
        return "update_category"
    elif state.jokes_choice == "q":
        return "exit_bot"
    return "exit_bot"


def build_joke_graph() -> CompiledStateGraph:
    workflow = StateGraph(JokeState)
    workflow.add_node("show_menu",show_menu)
    workflow.add_node("fetch_joke",fetch_joke)
    workflow.add_node("update_category",update_category)
    workflow.add_node("exit_bot",exit_bot)

    workflow.set_entry_point("show_menu")

    workflow.add_conditional_edges(
        "show_menu",
        route_choice,
        {
            "fetch_joke":"fetch_joke",
            "update_category":"update_category",
            "exit_bot":"exit_bot"
        }
    )
    workflow.add_edge("fetch_joke","show_menu")
    workflow.add_edge("update_category","show_menu")
    workflow.add_edge("exit_bot",END)

    return workflow.compile()

def main():
    graph = build_joke_graph()
    final_state = graph.invoke(JokeState(),config={"recursion_limit":100})
    return final_state

if __name__ == "__main__":
    main()