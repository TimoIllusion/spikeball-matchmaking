# Spikeball Matchmaking

This Streamlit app automatically generates optimal matchups for Spikeball or other 2v2 games. It considers several factors like the number of breaks, variety of opponents, and team compositions to ensure balanced and enjoyable games.

You can access the app online [here](https://spikeball.streamlit.app/).

## Local Setup With Streamlit

Follow these steps to set up the app locally:

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/TimoIllusion/spikeball-matchmaking.git
   ```
2. **Navigate to the Project Directory:**
   ```bash
   cd spikeball-matchmaking
   ```
3. **Create a Conda Environment with Python 3.10:**
   ```bash
   conda create -n spikeballmm python=3.10
   ```
4. **Activate the Environment:**
   ```bash
   conda activate spikeballmm
   ```
5. **Install the Required Packages:**
   ```bash
   pip install .
   ```
6. **Run the Streamlit App:**
   ```bash
   streamlit run main.py
   ```
7. **Access the App:**
   - Open [http://localhost:8501/](http://localhost:8501/) in your web browser (it should open automatically).

## Run Scripts For Offline Matchmaking

Generate excel tables for a tournament with these scripts.



Assuming already set up and activated python environment:

1. Configure the config.py in root of this repo depending on your requirements.

2. Install the package:

```bash
cd spikeball-matchmaking
pip install .
```
3. Run the script:

```bash
python generate_matchups_excel_sheet.py 
```

## Build Cpp Extensions

```python setup.py build_ext --inplace```

## TODO

- [ ] Build complete c or c++ engine for matchmaking
