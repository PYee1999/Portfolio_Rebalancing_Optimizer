# Portfolio_Rebalancing_Optimizer
Given a stock portfolio that shows number of shares owned and bought at specific price and target weights to adjust to, optimize portfolio by moving number of shares to meet those weights without going over the transaction fee.

**Programming Assignment – Portfolio Rebalancing**

1. Goal
A single portfolio optimization that rebalances the portfolio back to the model (minimize the deviations
between portfolio holding and model target weights) while keeping the total trading cost (sum of each
holding trading cost) below a certain dollar amount.
Assumptions &amp; Conditions:
- The problem can handle any number of securities
- Stocks can be traded at any fractional unit
- Shorting is not allowed
- The trading cost of a holding is 3% of its traded amount
- The total trading cost cannot exceed $7,500
- Deviations between portfolio and model weights should be measured as the square of the
difference in weights

2. Mathematical Formulation

Write out the mathematical equations defining the objective function and constraints.

3. Python Program
Develop a working program (Python) using any opensource optimizer of your choice. The
program should be generalized so as it can easily be run with various inputs (e.g. trading cost
constraints). Make sure to clearly describe any variables and comment your code appropriately.

4. Example Portfolio
Use your program to solve (and print) the optimal holding weights for the following portfolio.

<img width="407" alt="Screenshot 2023-09-10 at 4 17 25 PM" src="https://github.com/PYee1999/Portfolio_Rebalancing_Optimizer/assets/41497459/ce68a598-f571-4225-b176-051e3de3a82b">
