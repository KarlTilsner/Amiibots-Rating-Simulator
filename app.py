import trueskill
import json
import random
import matplotlib.pyplot as plt

# Set global variables
mu_initial = 25
sigma_initial = mu_initial / 3 # 25/3
beta_initial = mu_initial / 6 # 25/6
tau_initial = mu_initial / 300 # 25/300
draw_initial = 0

trueskill.setup(mu=mu_initial, sigma=sigma_initial, beta=beta_initial, tau=tau_initial, draw_probability=draw_initial)

# max_points_on_screen = 1000
simulated_runs = 150
simulated_rounds = 50 # int(max_points_on_screen / simulated_runs)

artificial_wr_boost = 1 # 1 = no boost
simulated_character = 'da8fefbf-43a2-47f5-a5bf-d7dadb4fabdc'
simulated_character_name = '???'





# Load snapshot of Amiibo
with open('amiibots_vanilla.json', encoding='utf-8') as f:
    response = json.load(f)

trainers = list(set(index['user']['id'] for index in response['data']))

def get_amiibo(rating_mu, response, trainers):
    trainer_ids = set(trainers)
    data = {}
    for amiibo in response['data']:
        if (amiibo['rating_mu'] <= rating_mu + 5 and amiibo['rating_mu'] >= rating_mu - 5 and amiibo['user']['id'] in trainer_ids): #amiibo['match_selection_status'] != "INACTIVE" and
            temp = data.get(amiibo['user']['id'], {
                'trainer_id': amiibo['user']['id'],
                'trainer_name': amiibo['user']['twitch_user_name'],
                'amiibo': [],
            })
            temp['amiibo'].append(amiibo)
            data[amiibo['user']['id']] = temp
    return list(data.values())





# Load winrates
with open('AmiibotsMatchupData.json', encoding='utf-8') as f:
    winrate = json.load(f)

sim_winrates = {}
for index in winrate:
    if index['id'] == simulated_character:
        simulated_character_name = index['name']
        for character in index['data']:
            sim_winrates[character['id']] = character['wins'] / (character['wins'] + character['losses'])





sim_runs = []
first_round_result = []
for x in range(simulated_runs):
    print(x + 1)
    rounds = [0]
    ratings = [0]
    
    # Set up initial simulation amiibo
    sim_amiibo = trueskill.Rating(mu_initial, sigma_initial)

    for i in range(simulated_rounds):
        # Matchmaking selection
        all_amiibo = get_amiibo(sim_amiibo.mu, response, trainers) # Call get_amiibo to filter suitable opponents
        random_trainer = random.choice(all_amiibo)

        # Find the best quality opponent
        best_quality = -1
        best_amiibo = None
        for amiibo in random_trainer['amiibo']:
            amiibo_quality = trueskill.quality_1vs1(sim_amiibo, trueskill.Rating(amiibo['rating_mu'], amiibo['rating_sigma']))
            if amiibo_quality > best_quality:
                best_quality = amiibo_quality
                best_amiibo = amiibo
        
        random_amiibo = best_amiibo
        sim_opponent = trueskill.Rating(random_amiibo['rating_mu'], random_amiibo['rating_sigma'])

        # Determine the winner
        if random.random() < (sim_winrates[random_amiibo['playable_character_id']] * artificial_wr_boost):
            sim_amiibo, sim_opponent = trueskill.rate_1vs1(sim_amiibo, sim_opponent)
            # Store first match result
            if i == 0: first_round_result.append(1)
        else:
            sim_opponent, sim_amiibo = trueskill.rate_1vs1(sim_opponent, sim_amiibo)
            if i == 0: first_round_result.append(2)

        # Collect rating data for this round
        rounds.append(i + 1)
        ratings.append(trueskill.expose(sim_amiibo))

    sim_runs.append(ratings)





# Set figure size and background color
plt.figure(figsize=(10, 6), facecolor='#1e1e1e')  # Dark background color

# Graph the rating
for i, plot_rating in enumerate(sim_runs):
    cyan = (0, 1, 1)
    pink = (1, 0.4, 0.6)
    color = (1, 0, 0) # Set to red incase something breaks
    if first_round_result[i] == 1: color = cyan
    if first_round_result[i] == 2: color = pink
    plt.plot(rounds, plot_rating, label=f"Simulation {i+1}", color=color)

# Plot style settings
plt.xlabel('Rounds', fontsize=14, fontweight='bold', color='white')  # Set label color to white
plt.ylabel('Rating', fontsize=14, fontweight='bold', color='white')  # Set label color to white
plt.title(f'{simulated_character_name} Simulation Results', fontsize=16, fontweight='bold', color='white')  # Set title color to white
plt.grid(True, linestyle='--', alpha=0.7, color='#555555')  # Darker grid color
plt.tick_params(axis='x', colors='white')  # Set tick color to white
plt.tick_params(axis='y', colors='white')  # Set tick color to white
plt.gca().spines['bottom'].set_color('white')  # Set bottom spine color to white
plt.gca().spines['left'].set_color('white')  # Set left spine color to white
plt.gca().set_facecolor('#222222')  # Dark plot area background color
plt.tight_layout()
plt.show()