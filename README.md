# DDS Sales Bot

## Setup
1. Python 3.10+ recommended
2. `pip install -r requirements.txt`
3. Create `.env` with your `OPENAI_API_KEY`
4. Put your data files in `data/`:
   - `1256_sales_data_extended.json`
   - `dds_training.json` (optional)

## Run
```bash
python -m app.run_cli
# or
python app/run_cli.py
