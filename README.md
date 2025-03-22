# Binance Live Crypto Day Trading Bot

An automated cryptocurrency trading bot that receives signals from MetaSignals.io via Discord and automatically executes trades on Binance Futures.

## Features

- Automatic connection to MetaSignals.io Discord channel
- Real-time signal processing for trading decisions
- Integration with Binance Futures API
- Automatic positioning based on strategic signals
- Risk management through Stop-Loss and Take-Profit levels
- Multi-threading for parallel signal processing
- Excelsheet-based strategy analysis

## Prerequisites

- Python 3.x
- Binance API Key and Secret
- Discord Bot Token
- MetaSignals.io Discord channel access

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Chruut/Binance_LiveCryptoDayTradingBot.git
cd Binance_LiveCryptoDayTradingBot
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Configure your API keys in the `access.py` file:
```python
api_key = "YOUR_BINANCE_API_KEY"
api_secret = "YOUR_BINANCE_API_SECRET"
discord_token = "YOUR_DISCORD_TOKEN"
discord_channel_id = "YOUR_DISCORD_CHANNEL_ID"
```

## Usage

1. Start the bot:
```bash
python main.py
```

2. The bot will automatically:
   - Connect to the MetaSignals.io Discord channel
   - Receive and analyze trading signals
   - Execute trades based on configured strategies
   - Manage positions with Stop-Loss and Take-Profit

![Metasignal_example](https://github.com/user-attachments/assets/afc86795-2929-493f-88c3-d1a64521c96a)

### Example of Meta Signals Strategy: Official release of their profit table
![grafik](https://github.com/user-attachments/assets/73ceb8a6-4553-400f-8265-ce514771da96)

## Configuration

The main configuration parameters are located in `main.py`:

- `wallet_wealth`: Total capital for trading
- `max_wallet_proportion`: Maximum wallet utilization per trade
- `stake_position`: Capital share per trade
- `leverage`: Leverage for futures trading

## Security Notes

- Keep your API keys secure
- Test the bot initially with small amounts
- Monitor performance regularly
- Be aware of cryptocurrency trading risks

## License

MIT License

## Disclaimer

This bot is intended for educational purposes. Cryptocurrency trading involves high risks. Use this bot at your own risk and only with funds you can afford to lose.
