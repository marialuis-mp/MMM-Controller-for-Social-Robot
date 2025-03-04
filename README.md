# Model Based Controller
This repository allows to create a theory of mind model of the humans in the context of social interactions between social robots and human users.
Furthermore, it allows integrating the model into a controller of a social robot in order to automatically control the social robot based on the model estimations, by defining objectives regarding the mental states of the human users.

## Structure of the repository
The repository is organized into two big parts:
- **'lib'**: general files that can be used to create your own human-robot-interaction based on our framework. **It includes the ToM Model** code.
- **'experimentNao'**: Human-Robot interaction between Nao robot where the humans participants can play chess with the robot. 
  - The robot uses the ToM model to interact with the participant. This package depends on the 'lib' package.
  - This experiment corresponds to the case-study in [URL TO PAPER, will be updated once paper is published]. 

Depending on which part of the project you are planning to use, find the specific READ ME file for each one the two parts inside the respective folder:
- [README Experiment](experimentNao/README.md) of 'experimentNao'.  
- [README Model](lib/tom_model/README.md) of the 'Theory of Mind' code

## Installation
This project requires Python 3.9 and includes two main scripts located in the root folder. The necessary packages are listed in the `requirements.txt` file, and users can install them using a Python virtual environment or Anaconda.
**Important:** For the  'experimentNao' part of the project, additional installation requirements are needed before running the scripts. See [README Experiment](experimentNao/README.md) for more information.

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
There are two main scripts in the root folder. They correspond to the EXPERIMENT mode. 
Check the [README Experiment](experimentNao/README.md) for more information about the purpose and working flow of these two mains. 
You can run the two main scripts using the following commands:

1. **Running the first main script:**
   ```bash
   python main_identification.py
   ```

2. **Running the second main script:**
   ```bash
   python main_interaction.py
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

## Usage
Depending on which block of the project you are interested, search the 'Usage' section under the corresponding README file:
- if you want to run the example interaction 'experimentNAO': [README Experiment|Usage](experimentNao/README.md#Usage)
- if you want to use the 'Theory of Mind' model: [README Model|Usage](lib/tom_model/README.md#Usage)