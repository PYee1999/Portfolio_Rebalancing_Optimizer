from calculation import total_trading_cost
import numpy as np
from scipy.optimize import minimize, Bounds

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
