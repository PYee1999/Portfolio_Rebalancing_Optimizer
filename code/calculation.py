import numpy as np

def weight_dev(port_weights, target_weights):
    '''
    Function to calculate total deviation between portfolio holding weights and model target weights
    (This function is minimized in optimization function)
        port_weights: current weights in portfolio
        target_weights: weights we want to adjust port_weights to
    '''
    return np.sum(np.square(np.subtract(port_weights, target_weights)))

def total_trading_cost(curr_weights, adj_weights, prices, total_holdings, trading_rate): 
    '''
    Function to calculate total trading cost for adjusted weights
        curr_weights: original weights of portfolio
        adj_weights: adjusted weights of portfolio that would approach goal
        prices: list of prices for stocks
        total_holdings: total holdings in portfolio
        trading_rate: rate/fee for stock transaction
    '''
    # Get difference between current weight and target weight
    weight_diff_list = np.subtract(adj_weights, curr_weights)
    
    # Multiply weight differences by total number of shares to buy/sell in portfolio
    units_exchange_list = weight_diff_list * total_holdings

    # Convert exchange units to prices/amounts
    amt_exchange_list = np.multiply(units_exchange_list, prices)

    # Calculate trading costs/fees for each transaction
    trading_fees = np.absolute(amt_exchange_list * trading_rate) # Calculate fee for every transaction
    total_fee = np.sum(trading_fees) # Get total of all transaction fees

    return total_fee
