import pandas as pd
from market_structure_detector import MarketStructureDetector
from trading_strategy import TradingStrategy
from visualization import create_interactive_chart, show_trade_statistics

def main():
    detector = MarketStructureDetector(detection_type='filtered')
    strategy = TradingStrategy()
    
    df = detector.get_historical_data()
    structures = detector.detect_structures(df)
    trades = strategy.execute_backtest(df, structures)
    
    fig = create_interactive_chart(df, trades, structures)
    show_trade_statistics(trades)

if __name__ == "__main__":
    main()


























