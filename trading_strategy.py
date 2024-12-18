import pandas as pd

class TradingStrategy:
    def __init__(self):
        self.stop_loss_pct = 0.01  # 1%
        self.breakeven_pct = 0.006  # 0.6%
        self.trailing_activation_pct = 0.01  # 1%
        self.trailing_offset_high_vol = 0.005  # 0.5%
        self.trailing_offset_low_vol = 0.003   # 0.3%
        self.leverage = 10
        self.initial_capital = 1000

    def calculate_volatility(self, df, current_index):
        if current_index < 2:
            return False
        last_3_candles = df.iloc[current_index-2:current_index+1]
        ranges = (last_3_candles['high'] - last_3_candles['low']) / last_3_candles['low'] * 100
        avg_range = ranges.mean()
        return avg_range > 0.2

    def execute_backtest(self, df, structures):
        trades = []
        active_trades = []
        print("\n=== INICIO DE BACKTEST ===\n")
        
        for i in range(len(df)):
            current_price = df['close'].iloc[i]
            current_high = df['high'].iloc[i]
            current_low = df['low'].iloc[i]
            current_time = df['timestamp'].iloc[i]
            
            # Revisar señales de entrada
            for _, structure in structures.iterrows():
                if structure['time_end'] == current_time and i + 1 < len(df):
                    print(f"\n🔍 ESTRUCTURA DETECTADA:")
                    print(f"Tiempo: {structure['time_end']}")
                    print(f"Dirección: {structure['direction']}")
                    print(f"Precio estructura: {structure['price_end']}")
                    
                    entry_price = df['close'].iloc[i + 1]
                    
                    if structure['direction'] == 'LONG':
                        stop_loss = entry_price * (1 - self.stop_loss_pct)
                        print(f"\n🚀 ENTRADA LONG:")
                        print(f"Precio entrada: {entry_price}")
                        print(f"Stop loss inicial: {stop_loss}")
                        print(f"Tiempo entrada: {df['timestamp'].iloc[i + 1]}")
                        
                        active_trades.append({
                            'entry_price': entry_price,
                            'stop_loss': stop_loss,
                            'direction': 'LONG',
                            'entry_time': df['timestamp'].iloc[i + 1],
                            'breakeven_active': False,
                            'trailing_active': False,
                            'highest_price': entry_price,
                            'initial_stop': stop_loss
                        })
                    
                    elif structure['direction'] == 'SHORT':
                        stop_loss = entry_price * (1 + self.stop_loss_pct)
                        print(f"\n🔻 ENTRADA SHORT:")
                        print(f"Precio entrada: {entry_price}")
                        print(f"Stop loss inicial: {stop_loss}")
                        print(f"Tiempo entrada: {df['timestamp'].iloc[i + 1]}")
                        
                        active_trades.append({
                            'entry_price': entry_price,
                            'stop_loss': stop_loss,
                            'direction': 'SHORT',
                            'entry_time': df['timestamp'].iloc[i + 1],
                            'breakeven_active': False,
                            'trailing_active': False,
                            'lowest_price': entry_price,
                            'initial_stop': stop_loss
                        })

            # Gestionar trades activos
            trades_to_remove = []
            for trade_idx, active_trade in enumerate(active_trades):
                if active_trade['direction'] == 'LONG':
                    active_trade['highest_price'] = max(active_trade['highest_price'], current_high)
                    current_profit_pct = (current_high - active_trade['entry_price']) / active_trade['entry_price'] * 100
                    
                    print(f"\n📊 GESTIÓN LONG TRADE:")
                    print(f"Precio actual alto: {current_high}")
                    print(f"Profit actual: {current_profit_pct:.2f}%")
                    
                else:
                    active_trade['lowest_price'] = min(active_trade['lowest_price'], current_low)
                    current_profit_pct = (active_trade['entry_price'] - current_low) / active_trade['entry_price'] * 100
                    
                    print(f"\n📊 GESTIÓN SHORT TRADE:")
                    print(f"Precio actual bajo: {current_low}")
                    print(f"Profit actual: {current_profit_pct:.2f}%")

                volatility = self.calculate_volatility(df, i)
                trailing_offset = self.trailing_offset_high_vol if volatility else self.trailing_offset_low_vol
                
                print(f"Volatilidad: {'Alta' if volatility else 'Baja'}")
                print(f"Trailing offset: {trailing_offset}")

                if active_trade['direction'] == 'LONG':
                    if current_profit_pct >= self.breakeven_pct and not active_trade['breakeven_active']:
                        print(f"✅ ACTIVANDO BREAKEVEN")
                        active_trade['stop_loss'] = active_trade['entry_price']
                        active_trade['breakeven_active'] = True

                    if current_profit_pct >= self.trailing_activation_pct:
                        new_stop = active_trade['highest_price'] * (1 - trailing_offset)
                        if new_stop > active_trade['stop_loss']:
                            print(f"📈 ACTUALIZANDO TRAILING STOP:")
                            print(f"Anterior: {active_trade['stop_loss']}")
                            print(f"Nuevo: {new_stop}")
                            active_trade['stop_loss'] = new_stop
                            active_trade['trailing_active'] = True

                    if current_low <= active_trade['stop_loss']:
                        exit_price = active_trade['stop_loss']
                        exit_reason = 'Trailing Stop' if active_trade['trailing_active'] else 'Stop Loss'
                        print(f"\n❌ CIERRE LONG:")
                        print(f"Razón: {exit_reason}")
                        print(f"Precio salida: {exit_price}")
                        trades_to_remove.append((trade_idx, exit_price, exit_reason))

                else:  # SHORT
                    if current_profit_pct >= self.breakeven_pct and not active_trade['breakeven_active']:
                        print(f"✅ ACTIVANDO BREAKEVEN")
                        active_trade['stop_loss'] = active_trade['entry_price']
                        active_trade['breakeven_active'] = True

                    if current_profit_pct >= self.trailing_activation_pct:
                        new_stop = active_trade['lowest_price'] * (1 + trailing_offset)
                        if new_stop < active_trade['stop_loss']:
                            print(f"📉 ACTUALIZANDO TRAILING STOP:")
                            print(f"Anterior: {active_trade['stop_loss']}")
                            print(f"Nuevo: {new_stop}")
                            active_trade['stop_loss'] = new_stop
                            active_trade['trailing_active'] = True

                    if current_high >= active_trade['stop_loss']:
                        exit_price = active_trade['stop_loss']
                        exit_reason = 'Trailing Stop' if active_trade['trailing_active'] else 'Stop Loss'
                        print(f"\n❌ CIERRE SHORT:")
                        print(f"Razón: {exit_reason}")
                        print(f"Precio salida: {exit_price}")
                        trades_to_remove.append((trade_idx, exit_price, exit_reason))

            # Procesar trades cerrados
            for trade_idx, exit_price, exit_reason in trades_to_remove:
                closed_trade = active_trades[trade_idx]
                price_diff = abs(exit_price - closed_trade['entry_price'])
                base_pct = (price_diff / closed_trade['entry_price']) * 100
                
                if closed_trade['direction'] == 'LONG':
                    pnl_usd = self.initial_capital * (base_pct/100) * self.leverage if exit_price > closed_trade['entry_price'] else -self.initial_capital * (base_pct/100) * self.leverage
                else:
                    pnl_usd = self.initial_capital * (base_pct/100) * self.leverage if exit_price < closed_trade['entry_price'] else -self.initial_capital * (base_pct/100) * self.leverage

                print(f"\n💰 RESULTADOS TRADE:")
                print(f"PnL: ${pnl_usd:.2f}")
                print(f"Duración: {current_time - closed_trade['entry_time']}")

                trades.append({
                    'entry_price': closed_trade['entry_price'],
                    'exit_price': exit_price,
                    'entry_time': closed_trade['entry_time'],
                    'exit_time': current_time,
                    'direction': closed_trade['direction'],
                    'price_diff': price_diff,
                    'base_pct': base_pct,
                    'leveraged_pct': base_pct * self.leverage,
                    'pnl_usd': pnl_usd,
                    'exit_reason': exit_reason,
                    'trade_duration': current_time - closed_trade['entry_time']
                })

            # Remover trades cerrados
            for trade_idx, _, _ in sorted(trades_to_remove, reverse=True):
                active_trades.pop(trade_idx)

        return pd.DataFrame(trades)

