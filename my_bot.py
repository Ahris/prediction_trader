import random
import other_bots
import traders
import run_experiments
import plot_simulation

class MyBot(traders.Trader):
    name = 'lurker'

    def simulation_params(self, timesteps,
                          possible_jump_locations,
                          single_jump_probability):
        """Receive information about the simulation."""
        # Number of trading opportunities
        self.timesteps = timesteps
        # A list of timesteps when there could be a jump
        self.possible_jump_locations = possible_jump_locations
        # For each of the possible jump locations, the probability of
        # actually jumping at that point. Jumps are normally
        # distributed with mean 0 and standard deviation 0.2.
        self.single_jump_probability = single_jump_probability
        # A place to store the information we get

        self.alpha = .9
        self.belief = 50.0
        self.information = []
        self.time = 0
        self.trades = []
    
    def new_information(self, info, time):
        """Get information about the underlying market value.
        
        info: 1 with probability equal to the current
          underlying market value, and 0 otherwise.
        time: The current timestep for the experiment. It
          matches up with possible_jump_locations. It will
          be between 0 and self.timesteps - 1."""
        self.information.append(info)
        self.belief = (self.belief * self.alpha
                       + info * 100 * (1 - self.alpha))

    def trades_history(self, trades, time):
        """A list of everyone's trades, in the following format:
        [(execution_price, 'buy' or 'sell', quantity,
          previous_market_belief), ...]
        Note that this isn't just new trades; it's all of them."""
        self.trades = trades
        self.time = time

    def trading_opportunity(self, cash_callback, shares_callback,
                            check_callback, execute_callback,
                            market_belief):
        """Called when the bot has an opportunity to trade.
        
        cash_callback(): How much cash the bot has right now.
        shares_callback(): How many shares the bot owns.
        check_callback(buysell, quantity): Returns the per-share
          price of buying or selling the given quantity.
        execute_callback(buysell, quantity): Buy or sell the given
          quantity of shares.
        market_belief: The market maker's current belief.

        Note that a bot can always buy and sell: the bot will borrow
        shares or cash automatically.
        """
        lurk_threshold = 0.2
        time_passed = self.time / float(self.timesteps)

        current_belief = (self.belief + market_belief*2) / 3.0
        # current_belief = (self.belief + (5/2)* market_belief) / (1 + (5/2))
        current_belief = max(min(current_belief, 99.0), 1.0)

        if len(self.trades) < 1 or time_passed < lurk_threshold:
            return
        else:
            bought_once = False
            sold_once = False
            block_size = 20 + 30 * time_passed
            while True:
                if (not sold_once
                    and (check_callback('buy', block_size)
                         < current_belief)):
                    execute_callback('buy', block_size)
                    bought_once = True
                elif (not bought_once
                      and (check_callback('sell', block_size)
                           > current_belief)):
                    execute_callback('sell', block_size)
                    sold_once = True
                else:
                    if block_size == 2:
                        break
                    block_size = block_size // 2
                    if block_size < 2:
                        block_size = 2

        

def main():
    bots = [MyBot()]
    bots.extend(other_bots.get_bots(5,2))
    # Plot a single run. Useful for debugging and visualizing your
    # bot's performance. Also prints the bot's final profit, but this
    # will be very noisy.
    #plot_simulation.run(bots, lmsr_b=250)
    
    # Calculate statistics over many runs. Provides the mean and
    # standard deviation of your bot's profit.
    run_experiments.run(bots, simulations=1000, lmsr_b=250)

# Extra parameters to plot_simulation.run:
#   timesteps=100, lmsr_b=150

# Extra parameters to run_experiments.run:
#   timesteps=100, num_processes=2, simulations=2000, lmsr_b=150

# Descriptions of extra parameters:
# timesteps: The number of trading rounds in each simulation.
# lmsr_b: LMSR's B parameter. Higher means prices change less,
#           and the market maker can lose more money.
# num_processes: In general, set this to the number of cores on your
#                  machine to get maximum performance.
# simulations: The number of simulations to run.

if __name__ == '__main__': # If this file is run directly
    main()
