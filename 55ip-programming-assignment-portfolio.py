import pandas as pd
import numpy as np
import sys # sys module to get command-line argument data 
from scipy.optimize import minimize, Bounds # Optimization libraries

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

def optimize_holdings(min_func, port_weights, target_weights, prices, total_holdings, cons_trading_limit, trading_rate, tolerance):
    '''
    Optimizer Function (Ref: https://towardsdatascience.com/portfolio-optimization-with-scipy-aa9c02e6b937)
        min_func: function we want to minimize on (in this case, minimize weight deviation)
        port_weights: input portfolio weights we want to adjust in optimizer
        target_weights: target weights (we want port_weights to adjust to be as close to)
        prices: list of latest (t1) market prices for stocks
        total_holdings: total holdings (units) in portfolio
        cons_trading_limit: total trading limit contraint
        trading_rate: rate/free for every stock transaction; used for constraint function
        tolerance: optimizer tolerance
    '''
    opt_bounds = Bounds(0.0, 1.0) # Set bounds for weights to be between 0 and 1
    save_curr_weights = port_weights # Save port_weights for checking trade limit

    # Contraint function to check trade limit
    def check_trade_limit(port_weights):
        limit = cons_trading_limit - (total_trading_cost(
                    curr_weights=save_curr_weights, 
                    adj_weights=port_weights,
                    prices=prices,
                    total_holdings=total_holdings,
                    trading_rate=trading_rate
                    ))
        # print("check_trade_limit:", limit)
        return limit

    # Set our constraints for the optimization
    opt_constraints = [
        {'type': 'eq', 'fun': lambda port_weights: 1.0 - (np.sum(port_weights))}, # Weights must sum up to 1
        {'type': 'ineq', 'fun': lambda port_weights: check_trade_limit(port_weights)} # Total trading fees must not exceed limit
    ]
    
    # Calculate optimal weights with the constraints
    optimal_weights = minimize(min_func, port_weights, 
                               args=(target_weights),
                               method='SLSQP',
                               bounds=opt_bounds,
                               constraints=opt_constraints,
                               tol=tolerance
                               )
    
    print(optimal_weights)

    # Return optimal weights of portfolio
    return optimal_weights['x']

def validate_port_target_vals(stock_portfolio_data):
    '''
    Checks if portfolio target values do sum up to 1.
    If so, resume program; otherwise, print error and stop program
        stock_portfolio_data: list of stock data; each stock in list is in form of dictionary

    '''
    check_sum = 0.0
    for stock in stock_portfolio_data:
        check_sum += stock["target_weight"]
    if (check_sum != 1.0):
        raise Exception(f"ERROR: target_weights in portfolio do not add up to 1.0\nCurrently sums up to: {check_sum}")

def main():
    '''
    Main Method:
    - Takes in three arguments: 
        - arg1: trading_cost_limit (What is the max allocated trading cost allowed) 
        - arg2: trading_rate (What is the trading rate for every transaction)
        - arg3: tolerance (What is the tolerance for the optimizer)
        - arg4: portfolio_name (csv filename for stock portfolio; formatted as list of dictionaries)
    - Determines if target_weights in stock portfolio are valid (sum of target_weights should add up to 1)
    - Calculate total trading fee to rebalance portfolio back to target_weights and show data collected
    - If total trading fee is at most the limit, then target weights are the holding weights
    - Otherwise, run optimizer to calculate holding weights
    '''
    
    # Collect inputted information from command-line arguments
    trading_cost_limit = float(sys.argv[1]) # Get trading_cost_limit (7500)
    trading_rate = float(sys.argv[2])       # Get rate for trading stocks (0.03)
    tolerance = float(sys.argv[3])          # Get tolerance in optimizer (0.0001, or put 0.0 if no tolerance)
    portfolio_name = str(sys.argv[4])       # Get csv filename to access stock portfolio

    '''
    Get stock data from CSV files
    Stock portfolio is a list of dictionaries; each dictionary is a stock and its data
    Format of porfolio is as follows:
    [
        {
            "stock_name": 'A',          # Stock
            "t0_stock_price": 100.0,    # t0 Price
            "units_held": 5000.0,       # t0 Units Held
            "t1_stock_price": 63.0,     # t1 Price
            "target_weight": 0.4,       # t1 Target Weight
            "holding_weight": -1        # t1 Holding Weight
        },
        ...
    ]
    '''
    stock_portfolio_data = pd.read_csv(portfolio_name).to_dict(orient='records')
    
    # Checks if target weights in portfolio are valid (sum up to 1)
    validate_port_target_vals(stock_portfolio_data)

    total_curr_port_val = 0     # Total current market value of portfolio (using t1 price)
    total_holdings = 0          # Total number of holdings in portfolio
    target_market_val_list = [] # List of target market values for each stock holding
    curr_market_val_list = []   # List of current market values for each stock holding
    curr_stock_prices_list = [] # List of current stock prices

    # Loop through every stock inside of the portfolio
    for stock in stock_portfolio_data:
        
        # Append target_weight of stock to target_market_val_list
        target_market_val_list.append(stock["target_weight"])
        
        # Append t1_stock_price of stock to curr_stock_prices_list
        curr_stock_prices_list.append(stock["t1_stock_price"])

        # Add up total number of units in each stock of portfolio
        total_holdings += stock["units_held"]

        # Calculate current market value of stock holdings
        curr_stock_market_val = stock["t1_stock_price"] * stock["units_held"]

        # Append curr_stock_market_val to curr_market_val_list
        curr_market_val_list.append(curr_stock_market_val)

        # Add curr_stock_market_val to total_curr_port_val to get grand total value of portfolio
        total_curr_port_val += curr_stock_market_val

    # Convert lists to np.array
    target_market_val_list = np.array(target_market_val_list)
    curr_market_val_list = np.array(curr_market_val_list)

    # Divide each holding by the total to get current holding weights for each stock in portfolio
    curr_portfolio_weight_list = curr_market_val_list / total_curr_port_val

    # Get difference between current weight and target weight
    weight_diff_list = np.subtract(target_market_val_list, curr_portfolio_weight_list)

    # Multiply weight differences by total number of shares to buy/sell in portfolio
    units_exchange_list = weight_diff_list * total_holdings

    # Convert exchange units to prices
    amt_exchange_list = np.multiply(units_exchange_list, curr_stock_prices_list)

    # Calculate trading costs/fees for each transaction
    trading_fees = np.absolute(amt_exchange_list * trading_rate) # Calculate fee for every transaction
    total_fee = np.sum(trading_fees) # Get total of all transaction fees

    print("\n----- STOCK PORTFOLIO DATA -----")
    print("Current t1 Weights:", curr_portfolio_weight_list)
    print("Target Weights:    ", target_market_val_list)
    print("Curr Market Vals:  ", curr_market_val_list)
    print("Total Market Val:  ", total_curr_port_val)
    print("Weight Diff:       ", weight_diff_list)
    print("Buy/Sell Units:    ", units_exchange_list)
    print("Buy/Sell $ Amts:   ", amt_exchange_list)
    print("Trading Fees:      ", trading_fees)
    print("Total Trading Fee: ", total_fee)
    print("Trading Fee Limit: ", trading_cost_limit)

    # Check if total_fee is at most the limit
    if (total_fee <= trading_cost_limit):
        # If total_fee is within the limit, holding_weight should be the same as target_weight
        print("\n----- TRADING FEE IS WITHIN LIMIT -----\n")
        for stock in stock_portfolio_data:
            stock["holding_weight"] = stock["target_weight"]
    else:
        # Otherwise, we need to optimize holding weights to be within the limit
        print("\n----- TRADING FEE EXCEEDS LIMIT -----\n")

        # Perform optimization
        print("Running Optimizer...")
        new_holdings = optimize_holdings(
            weight_dev, 
            curr_portfolio_weight_list,
            target_market_val_list, 
            curr_stock_prices_list, 
            total_holdings, 
            trading_cost_limit, 
            trading_rate,
            tolerance)
        
        print("Optimized Holdings: ", new_holdings) # Show optimal holdings
        print("Updated Trading Fee:", 
            total_trading_cost(
                curr_portfolio_weight_list, 
                new_holdings, 
                curr_stock_prices_list, 
                total_holdings, 
                trading_rate), "\n") # Show updated trading fee with optimal holdings

        # Update dictionary "holding_weight" with new_holdings data for each stock
        for index in range(len(stock_portfolio_data)):
            stock_portfolio_data[index]["holding_weight"] = new_holdings[index]

    # Print out holding answer for each stock
    print("----- ANSWER -----\n")
    print("Holding weights for each stock in portfolio should be rebalanced to:")
    for stock in stock_portfolio_data:
        stock_name = stock["stock_name"]
        stock_holding_weight = stock["holding_weight"]
        print(f"Stock {stock_name}: {stock_holding_weight}")
        
if __name__ == '__main__':
    main()