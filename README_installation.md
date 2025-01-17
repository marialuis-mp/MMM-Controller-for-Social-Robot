# Project Name

### Overview
This project requires Python 3.9 and includes two main scripts located in the root folder. The necessary packages are listed in the `requirements.txt` file, and users can install them using a Python virtual environment or Anaconda.

### Prerequisites
Ensure that Python 3.9 is installed on your system. You can install Python 3.9 using any of the following methods:

- **Anaconda**: A Python distribution with easy-to-use package and environment management.
- **venv**: A lightweight virtual environment tool included with Python.

#### Installing Python 3.9 (Anaconda)

1. Download and install [Anaconda](https://www.anaconda.com/products/individual).
2. Create a new environment for Python 3.9:
   ```bash
   conda create --name myenv python=3.9
   ```
3. Activate the environment:
   - On Windows:
     ```bash
     conda activate myenv
     ```
   - On macOS/Linux:
     ```bash
     source activate myenv
     ```

#### Installing Python 3.9 (venv)

1. Ensure Python 3.9 is installed on your system. If not, download and install it from [python.org](https://www.python.org/downloads/).
2. Create a virtual environment:
   ```bash
   python3.9 -m venv myenv
   ```
3. Activate the environment:
   - On Windows:
     ```bash
     myenv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source myenv/bin/activate
     ```

### Install Dependencies
Once Python 3.9 is installed and your environment is active, install the required packages by running:

```bash
pip install -r requirements.txt
```

### Running the Main Scripts
There are two main scripts in the root folder. You can run them using the following commands:

1. **Running the first main script:**
   ```bash
   python main1.py
   ```

2. **Running the second main script:**
   ```bash
   python main2.py
   ```

Ensure that your virtual environment is activated when running the scripts.

### Deactivating the Environment
Once you're done working with the project, you can deactivate the virtual environment using:

- **Anaconda:**
  ```bash
  conda deactivate
  ```

- **venv:**
  ```bash
  deactivate
  ```

### License
Include licensing information here if applicable.
