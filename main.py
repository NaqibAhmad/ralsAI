from src.componentns.agents.ralsAgent import RalsAgent

def main():
    agent = RalsAgent()
    while True:
        query = input("User: ")
        response = agent.respond(query)
        print(f"Agent: {response}")

if __name__ == "__main__":
    main()
