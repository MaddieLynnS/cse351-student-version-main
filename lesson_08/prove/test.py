import matplotlib.pyplot as plt
import matplotlib.animation as animation

def ask_standards():
    response = input("Do you have standards? (Yes/No): ").strip().lower()

    if response == "yes":
        realistic = input("Are they realistic? (Yes/No): ").strip().lower()

        if realistic == "yes":
            realistic_standards = input("Would you be willing to lower them? (Yes/No): ").strip().lower()

            if realistic_standards == "yes":
                print("\nWhat do you like doing for fun? What are your hobbies or interests?")
                possible = []
                print("List your hobbies and interests. When done, type 'done' duh\n")

                while True:
                    hobby = input("→ ").strip()
                    if hobby.lower() == "done":
                        break
                    elif hobby == "":
                        print("You didn’t type anything. Are you really that boring?")
                        continue
                    possible.append(hobby)
                    print(f"Added: {hobby}")
                    print(f"Current list: {possible}\n")

                print("\nHere's everything you listed:")
                for h in possible:
                    print("-", h)

                # Fun reaction
                if len(possible) == 0:
                    print("\nYou didn’t list anything... You should find a hobby.")
                elif len(possible) < 3:
                    print("\nShort and sweet list!")
                else:
                    print("\nThose are pretty cool, except for the second one...")

                # Ask on date
                date_question = input("\nWould you like to go on a date centered around one of these? (Yes/No): ").strip().lower()

                if date_question == "yes":
                    if len(possible) > 0:
                        print("Awesome! Which one should we base it on?")
                        for i, hobby in enumerate(possible, start=1):
                            print(f"{i}. {hobby}")
                        choice = input("Pick a number: ").strip()

                        if choice.isdigit() and 1 <= int(choice) <= len(possible):
                            print(f"Perfect — a {possible[int(choice) - 1]}-themed date it is!")
                        else:
                            print("That’s not a valid choice, but I like the enthusiasm!")
                    else:
                        print("Wait... you didn’t list any hobbies. So... maybe a surprise date?")
                elif date_question == "no":
                    print("Womp womp")

                    # Animated "hopes and dreams" decline
                    fig, ax = plt.subplots(figsize=(6,4))
                    ax.set_xlim(0, 10)
                    ax.set_ylim(0, 100)
                    ax.set_title("My Hopes and Dreams Over Time 💔")
                    ax.set_xlabel("Time")
                    ax.set_ylabel("My Hopes and Dreams")
                    line, = ax.plot([], [], 'r-', linewidth=3)

                    x_data, y_data = [], []

                    def animate(i):
                        x_data.append(i)
                        # Simulate exponential decline
                        y_data.append(100 * (0.9 ** i))
                        line.set_data(x_data, y_data)
                        return line,

                    ani = animation.FuncAnimation(fig, animate, frames=30, interval=200, blit=True, repeat=False)
                    plt.show()

                else:
                    print("That wasn’t a Yes or No, so I’ll take that as a 'Maybe'")

            elif realistic_standards == "no":
                welp = input("What if I promise not to take you to Kiwi Loco? (I'm in / I'm ok): ").strip().lower()
                if welp in ["i'm in", "im in"]:
                    print("50% of the time — frozen yogurt diplomacy works every time.")
                elif welp in ["i'm ok", "im ok"]:
                    print("Fair enough. Dignity first.")
                else:
                    print("That’s... not one of the options, but okay")

            else:
                print("Quit trying to break the code, ya dingus!")

        elif realistic == "no":
            print("It’s time for a reality check!")
        else:
            print("Please answer Yes or No.")

    elif response == "no":
        print("At least you're honest.")

    else:
        print("Please answer with either a Yes or a No.")
        ask_standards()  # restart if invalid input


# Ask if they want to retry without having to restart the code
while True:
    ask_standards()
    retry = input("\nWould you like to try again? (Yes/No): ").strip().lower()
    if retry != "yes":
        print("Fair enough")
        break
