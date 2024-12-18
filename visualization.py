import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

def create_interactive_chart(df, trades, structures):
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                       vertical_spacing=0.03, 
                       row_heights=[0.7, 0.3])

    # Candlestick base
    fig.add_trace(go.Candlestick(
        x=df['timestamp'],
        open=df['open'],
        high=df['high'],
        low=df['low'],
        close=df['close'],
        name='Price'
    ), row=1, col=1)

    # Entradas LONG
    long_entries = trades[trades['direction'] == 'LONG']
    fig.add_trace(go.Scatter(
        x=long_entries['entry_time'],
        y=long_entries['entry_price'],
        mode='markers',
        marker=dict(symbol='triangle-up', size=10, color='green'),
        name='Long Entry'
    ), row=1, col=1)

    # Salidas LONG
    fig.add_trace(go.Scatter(
        x=long_entries['exit_time'],
        y=long_entries['exit_price'],
        mode='markers',
        marker=dict(symbol='triangle-down', size=10, color='red'),
        name='Long Exit'
    ), row=1, col=1)

    # Entradas SHORT
    short_entries = trades[trades['direction'] == 'SHORT']
    fig.add_trace(go.Scatter(
        x=short_entries['entry_time'],
        y=short_entries['entry_price'],
        mode='markers',
        marker=dict(symbol='triangle-down', size=10, color='red'),
        name='Short Entry'
    ), row=1, col=1)

    # Salidas SHORT
    fig.add_trace(go.Scatter(
        x=short_entries['exit_time'],
        y=short_entries['exit_price'],
        mode='markers',
        marker=dict(symbol='triangle-up', size=10, color='green'),
        name='Short Exit'
    ), row=1, col=1)

    # Estructuras de mercado
    for _, structure in structures.iterrows():
        color = 'green' if structure['direction'] == 'LONG' else 'red'
        fig.add_trace(go.Scatter(
            x=[structure['time_start'], structure['time_end']],
            y=[structure['price_start'], structure['price_end']],
            mode='lines',
            line=dict(color=color, width=2),
            name=f"{structure['direction']} Structure"
        ), row=1, col=1)

    # PnL acumulado
    trades['cumulative_pnl'] = trades['pnl_usd'].cumsum()
    fig.add_trace(go.Scatter(
        x=trades['exit_time'],
        y=trades['cumulative_pnl'],
        mode='lines',
        name='Cumulative PnL',
        line=dict(color='blue')
    ), row=2, col=1)

    # Configuración del layout
    fig.update_layout(
        title='Trading Analysis with Market Structures',
        xaxis_title='Time',
        yaxis_title='Price',
        xaxis2_title='Time',
        yaxis2_title='Cumulative PnL ($)',
        height=800
    )

    fig.show()

def show_trade_statistics(trades):
    statistics_text = f"""
📊 ESTADÍSTICAS DETALLADAS DE TRADING
==================================================

🎯 Resumen General:
➤ Total de operaciones: {len(trades)}
➤ Operaciones ganadoras: {len(trades[trades['pnl_usd'] > 0])}
➤ Operaciones perdedoras: {len(trades[trades['pnl_usd'] <= 0])}
➤ Win rate: {len(trades[trades['pnl_usd'] > 0]) / len(trades) * 100:.2f}%

💰 Análisis de Ganancias/Pérdidas:
➤ PnL total: ${trades['pnl_usd'].sum():.2f}
➤ Ganancia promedio: ${trades[trades['pnl_usd'] > 0]['pnl_usd'].mean():.2f}
➤ Pérdida promedio: ${trades[trades['pnl_usd'] <= 0]['pnl_usd'].mean():.2f}
➤ Mayor ganancia: ${trades['pnl_usd'].max():.2f}
➤ Mayor pérdida: ${trades['pnl_usd'].min():.2f}

🎯 Análisis por Tipo de Salida:
➤ Trailing Stop: {len(trades[trades['exit_reason'] == 'Trailing Stop'])} trades
  Promedio PnL: ${trades[trades['exit_reason'] == 'Trailing Stop']['pnl_usd'].mean():.2f}
➤ Stop Loss: {len(trades[trades['exit_reason'] == 'Stop Loss'])} trades
  Promedio PnL: ${trades[trades['exit_reason'] == 'Stop Loss']['pnl_usd'].mean():.2f}

🔍 Detalles de cada trade:
"""
    print(statistics_text)
    
    # Mostrar detalles de cada trade
    trade_details = trades[['entry_time', 'exit_time', 'direction', 'entry_price', 
                          'exit_price', 'pnl_usd', 'exit_reason']]
    print(trade_details.to_string())

