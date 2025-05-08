import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import random
import time



import tempfile


# Streamlit Interface Initialization Section 2
st.title("Misinformation Dynamic Network Simulation")
st.sidebar.header("Simulation Parameters")
N = st.sidebar.slider("Number of Agents", min_value=50, max_value=500, value=100, step=10)
misinformation_spread_prob = st.sidebar.slider("Misinformation Spread Probability", min_value=0.0, max_value=1.0, value=0.3, step=0.05)
fact_check_prob = st.sidebar.slider("Fact-Checking Probability", min_value=0.0, max_value=1.0, value=0.1, step=0.05)
skeptic_conversion_prob = st.sidebar.slider("Skeptic Conversion Probability", min_value=0.0, max_value=1.0, value=0.05, step=0.01)  # New parameter
epsilon = st.sidebar.slider("Epsilon (E-Greedy Believers)", min_value=0.0, max_value=1.0, value=0.1, step=0.05)
steps = st.sidebar.slider("Simulation Steps", min_value=50, max_value=500, value=200, step=10)
believer_algorithm = st.sidebar.selectbox("Believer Strategy", ["E-Greedy", "Thompson Sampling", "UCB", "Random"])
skeptic_algorithm = st.sidebar.selectbox("Skeptic Strategy", ["UCB", "Thompson Sampling", "Random"])

# Network Initialization Section 3
G = nx.barabasi_albert_graph(N, 3)
network_pos = nx.spring_layout(G)  # Fixed layout for consistent visualization

# Agent Initialization Section 4
belief_states = ["Believer", "Skeptic", "Neutral", "Influencer"]
node_colors = {}
node_sizes = {}
skep_strategies = {}  # Store selected skeptic strategy
agent_types = {"Believer": set(), "Skeptic": set(), "Neutral": set(), "Influencer": set()}
rewards = {"Skeptic": [0], "Believer": [0]}  # Track cumulative rewards over time
for node in G.nodes():
    belief = random.choices(belief_states, weights=[0.4, 0.4, 0.1, 0.1])[0]
    if belief == "Skeptic":
        skep_strategies[node] = skeptic_algorithm  # Assign selected skeptic algorithm
    elif belief == "Believer":
        skep_strategies[node] = believer_algorithm  # Assign selected believer algorithm
    agent_types[belief].add(node)
    node_colors[node] = {"Believer": "red", "Skeptic": "blue", "Neutral": "gray", "Influencer": "green"}[belief]
    node_sizes[node] = {"Believer": 100, "Skeptic": 100, "Neutral": 80, "Influencer": 300}[belief]


belief_counts = {"Believers": [len(agent_types["Believer"])],
                 "Skeptics": [len(agent_types["Skeptic"])],
                 "Neutrals": [len(agent_types["Neutral"])],
                 "Influencers": [len(agent_types["Influencer"])],
                 "Rewards_Skeptic": [0],
                 "Rewards_Believer": [0]}

# Simulation UI and Trigger Section 5
st.sidebar.write("Click the button below to start the simulation.")
if st.sidebar.button("Start Simulation"):
    progress_bar = st.progress(0)
    status_text = st.empty()
    network_plot = st.empty()
    graph_plot = st.empty()

# Simulation Loop Section 6
    for t in range(steps):
        reward_skeptic = rewards["Skeptic"][-1]
        reward_believer = rewards["Believer"][-1]
        for node in list(G.nodes()):
            neighbors = list(G.neighbors(node))
            if not neighbors:
                continue
            target = random.choice(neighbors)
            if node in agent_types["Believer"]:  # Believers applying selected strategy
                if believer_algorithm == "E-Greedy" and random.random() < epsilon:
                    target = random.choice(neighbors)  # Explore new target
                if believer_algorithm == "UCB":
                    if random.random() < misinformation_spread_prob:
                        target = max(neighbors, key=lambda n: len(list(G.neighbors(n))), default=target)
                if random.random() < misinformation_spread_prob and target in agent_types["Neutral"]:
                    agent_types["Believer"].add(target)
                    agent_types["Neutral"].remove(target)
                    node_colors[target] = "red"
                    reward_believer += 1
                elif target in agent_types["Influencer"]:
                    agent_types["Believer"].add(target)
                    node_colors[target] = "red"
                    reward_believer += 2
            elif node in agent_types["Skeptic"]:  # Skeptics applying selected strategy
                strategy = skep_strategies.get(node, "UCB")

                if strategy == "UCB":
                    if random.random() < fact_check_prob:
                        if target in agent_types["Believer"]:
                            agent_types["Skeptic"].add(target)
                            agent_types["Believer"].remove(target)
                            node_colors[target] = "blue"
                            reward_skeptic += 1
                        elif target in agent_types["Influencer"]:
                            agent_types["Skeptic"].add(target)
                            agent_types["Influencer"].remove(target)
                            node_colors[target] = "blue"
                            reward_skeptic += 3  # bonus reward for converting an Influencer
                        elif target in agent_types["Neutral"]:
                            agent_types["Skeptic"].add(target)
                            agent_types["Neutral"].remove(target)
                            node_colors[target] = "blue"
                            reward_skeptic += 0.5

                elif strategy == "Thompson Sampling":
                    if random.betavariate(2, 5) > 0.5:
                        if target in agent_types["Believer"]:
                            agent_types["Skeptic"].add(target)
                            agent_types["Believer"].remove(target)
                            node_colors[target] = "blue"
                            reward_skeptic += 1
                        elif target in agent_types["Influencer"]:
                            agent_types["Skeptic"].add(target)
                            agent_types["Influencer"].remove(target)
                            node_colors[target] = "blue"
                            reward_skeptic += 3
                        elif target in agent_types["Neutral"]:
                            agent_types["Skeptic"].add(target)
                            agent_types["Neutral"].remove(target)
                            node_colors[target] = "blue"
                            reward_skeptic += 0.5

                elif strategy == "Random":
                    if random.random() < 0.5:
                        if target in agent_types["Believer"]:
                            agent_types["Skeptic"].add(target)
                            agent_types["Believer"].remove(target)
                            node_colors[target] = "blue"
                            reward_skeptic += 1
                        elif target in agent_types["Influencer"]:
                            agent_types["Skeptic"].add(target)
                            agent_types["Influencer"].remove(target)
                            node_colors[target] = "blue"
                            reward_skeptic += 3
                        elif target in agent_types["Neutral"]:
                            agent_types["Skeptic"].add(target)
                            agent_types["Neutral"].remove(target)
                            node_colors[target] = "blue"
                            reward_skeptic += 0.5

                # Skeptic conversion back to Neutral
                if random.random() < skeptic_conversion_prob:
                    agent_types["Skeptic"].remove(node)
                    agent_types["Neutral"].add(node)
                    node_colors[node] = "gray"

#  These updates happen for **every step**
        rewards["Believer"].append(reward_believer)
        rewards["Skeptic"].append(reward_skeptic)
        belief_counts["Believers"].append(len(agent_types["Believer"]))
        belief_counts["Skeptics"].append(len(agent_types["Skeptic"]))
        belief_counts["Neutrals"].append(len(agent_types["Neutral"]))
        belief_counts["Influencers"].append(len(agent_types["Influencer"]))

        progress_bar.progress((t + 1) / steps)
        status_text.text(f"Simulation Step {t + 1}/{steps}")

    #  Only render plots every 10 steps
        if t % 10 == 0:
        # Network Graph
            fig, ax = plt.subplots(figsize=(12, 10))
            nx.draw(
                G, pos=network_pos,
                node_color=[node_colors[n] for n in G.nodes()],
                node_size=[node_sizes[n] for n in G.nodes()],
                edge_color="lightgray", with_labels=False
            )
            network_plot.pyplot(fig)

        # Line Graphs for Beliefs & Rewards
            fig, axs = plt.subplots(1, 3, figsize=(18, 6))
            def compute_ci(data):
                data = np.array(data)
                mean = np.cumsum(data) / (np.arange(len(data)) + 1)
                std_err = [np.std(data[:i+1]) / np.sqrt(i+1) if i > 0 else 0 for i in range(len(data))]
                ci = 1.645 * np.array(std_err)
                return mean, ci

            believers = belief_counts["Believers"]
            skeptics = belief_counts["Skeptics"]
            x = range(len(believers))

            bel_mean, bel_ci = compute_ci(believers)
            skep_mean, skep_ci = compute_ci(skeptics)

            axs[0].plot(x, bel_mean, label="Believers", color="red")
            axs[0].fill_between(x, bel_mean - bel_ci, bel_mean + bel_ci, color="red", alpha=0.3)

            axs[0].plot(x, skep_mean, label="Skeptics", color="blue")
            axs[0].fill_between(x, skep_mean - skep_ci, skep_mean + skep_ci, color="blue", alpha=0.3)
            axs[0].set_title("Believers vs. Skeptics Over Time")
            axs[0].legend()

        # Neutrals over time
            neutrals = belief_counts["Neutrals"]
            neu_mean, neu_ci = compute_ci(neutrals)
            axs[1].plot(x, neu_mean, label="Neutrals", color="gray")
            axs[1].fill_between(x, neu_mean - neu_ci, neu_mean + neu_ci, color="gray", alpha=0.3)

            axs[1].set_title("Neutral Count Over Time")
            axs[1].legend()

        # Cumulative Rewards with 90% CI
            axs[2].set_title("Cumulative Rewards (90% CI)")
            believer_rewards = rewards["Believer"]
            skeptic_rewards = rewards["Skeptic"]
            x = range(len(believer_rewards))

            def compute_ci(data):
                data = np.array(data)
                mean = np.cumsum(data) / (np.arange(len(data)) + 1)
                std_err = [np.std(data[:i+1]) / np.sqrt(i+1) if i > 0 else 0 for i in range(len(data))]
                ci = 1.645 * np.array(std_err)  # 90% confidence interval
                return mean, ci

            believer_mean, believer_ci = compute_ci(believer_rewards)
            skeptic_mean, skeptic_ci = compute_ci(skeptic_rewards)

            axs[2].plot(x, believer_mean, label="Believers", color="red")
            axs[2].fill_between(x, believer_mean - believer_ci, believer_mean + believer_ci, color="red", alpha=0.3)

            axs[2].plot(x, skeptic_mean, label="Skeptics", color="blue")
            axs[2].fill_between(x, skeptic_mean - skeptic_ci, skeptic_mean + skeptic_ci, color="blue", alpha=0.3)

            axs[2].legend()
            axs[2].set_xlabel("Simulation Step")
            axs[2].set_ylabel("Cumulative Reward")

            graph_plot.pyplot(fig)
            # Show the parameters used in the simulation

    st.success("Simulation Complete")
    # --- Generate the final plot image ---
    fig, axs = plt.subplots(1, 3, figsize=(18, 6))

    # Believers vs. Skeptics
    axs[0].plot(x, bel_mean, label="Believers", color="red")
    axs[0].fill_between(x, bel_mean - bel_ci, bel_mean + bel_ci, color="red", alpha=0.3)
    axs[0].plot(x, skep_mean, label="Skeptics", color="blue")
    axs[0].fill_between(x, skep_mean - skep_ci, skep_mean + skep_ci, color="blue", alpha=0.3)
    axs[0].set_title("Believers vs. Skeptics")
    axs[0].legend()

    # Neutrals
    axs[1].plot(x, neu_mean, label="Neutrals", color="gray")
    axs[1].fill_between(x, neu_mean - neu_ci, neu_mean + neu_ci, color="gray", alpha=0.3)
    axs[1].set_title("Neutrals Over Time")
    axs[1].legend()

    # Rewards
    axs[2].plot(x, believer_mean, label="Believers", color="red")
    axs[2].fill_between(x, believer_mean - believer_ci, believer_mean + believer_ci, color="red", alpha=0.3)
    axs[2].plot(x, skeptic_mean, label="Skeptics", color="blue")
    axs[2].fill_between(x, skeptic_mean - skeptic_ci, skeptic_mean + skeptic_ci, color="blue", alpha=0.3)
    axs[2].set_title("Cumulative Rewards (90% CI)")
    axs[2].legend()

    # Save plot to a BytesIO buffer


    # Read the contents back for Streamlit to download


    # Optional: clean up the temp file
    import os
#    os.remove(tmp_pdf_path)
    st.subheader("Simulation Parameters Used")
    params_df = pd.DataFrame({
        "Parameter": [
            "Number of Agents",
            "Misinformation Spread Probability",
            "Fact-Checking Probability",
            "Skeptic Conversion Probability",
            "Epsilon (E-Greedy)",
            "Simulation Steps",
            "Believer Strategy",
            "Skeptic Strategy"
        ],
        "Value": [
            N,
            misinformation_spread_prob,
            fact_check_prob,
            skeptic_conversion_prob,
            epsilon,
            steps,
            believer_algorithm,
            skeptic_algorithm
        ]
    })
    st.table(params_df)
    results_df = pd.DataFrame({
        "Step": list(range(len(belief_counts["Believers"]))),
        "Believers": belief_counts["Believers"],
        "Skeptics": belief_counts["Skeptics"],
        "Neutrals": belief_counts["Neutrals"],
        "Influencers": belief_counts["Influencers"],
        "Reward_Believer": rewards["Believer"],
        "Reward_Skeptic": rewards["Skeptic"]
    })

    csv = results_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Download Simulation Results as CSV",
        data=csv,
        file_name="misinformation_simulation_results.csv",
        mime="text/csv",
        key="csv_download_button"
    )
