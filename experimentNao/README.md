# Interactions with model-based-control
This repository allows to generate the three sessions of interactions used in [the scientific article](/README.md#Model-based-controller-article), as well as to identify 
the models using the data collected in training interactions.

** Structure of the repository ** \
```
experimentNao
├── interaction: main files required to manage the interaction between robot and participant
├── behaviour_controllers: ...
```

## Installation
You must first follow the installation guide from [README Overall](README.md#Installation) file. This section represents additional requirements to use the experimentNao package. 

- Install stockfish (follow the instructions given in https://pypi.org/project/stockfish/). 
  - **Important:** Add the path to stockfish on your computer as the variable: "stockfish_path" in 'experimentNao/folder_path.py'. \
- Download the lichess puzzles database from https://database.lichess.org/#puzzles. Move the database .csv file to "experimentNao/chess_game". 
  - **Important:** Run 'experimentNao/chess_game/extract_chess_puzzles.py' to get the shortened and processed database used in the experiments. \
- In 'experimentNao/folder_path.py', set the variable 'data_folder_path' as the path where the data is going to be stored, if you wish to use any of the data analysis tools.

## Usage
This project can be used to run several of the following tasks. 

The general **workflow** adopted was: 
1. Start by setting the identifier of the participant in experiment_nao/participant.py. 
2. Run [Interaction](#interaction) in "TRAINING" mode
3. Run the [Model Identification](#model-identification) script with the desired model configuration. 
If you wish to run several configurations in separate, you can compare them using 
[the post identification analysis](#post-identification-analysis)
4. Run the [Pre Process Data](#pre-process-data) script before running [Interaction](#interaction) in "MBC" mode
5. Run [Interaction](#interaction) in "MBC" mode for model based control.

### Most relevant scripts 
Run each of these mains to achieve the two main specific tasks of experimentNao (**Interaction** and **Model identification**).
To run these scripts you need to:
1. Activate the environment
2. Run the main.py
3. Deactivate the environment
For full information on how to run these scripts, check out the overall README file [README Overall](README.md#Usage).

##### Interaction
- **Main:** 'main_interaction.py':  
- **What it does:** Runs the interaction. 
- **Usage:** You can change the most important settings of the interaction in this main, 
including the type of interaction between "TRAINING", Model-based-control and "MBC" and "ALTERNATIVE_C". 
Then, you can press main to run the interaction. 
  - interaction mode "MBC" and "ALTERNATIVE_C" only work once a model was identified (see next main, which identifies the model). 
- **Output:** Excel file "Reply_<participant_ID>_<timestamp>.xlsx" in output folder 
experimentNao/out/replies_participants (see [the structure of the output folder](#output-folder)).

##### Model Identification
- **Main:** 'main_identification.py':  
- **What it does:** Runs the identification of the model, given the arguments passed to the main. 
- **Usage:** Can only be done after at least one session of [the interaction](#interaction) was done with the 
participant and its output file was generated. 
  - Moreover, **the output file "Reply_<participant_ID>_<timestamp>.xlsx" of ** [the interaction](#interaction) ** 
  (generated in folder "replies_participants") must be moved into the sub-folder "replies_participants\to_id" ** and its 
  name should be edited as "Reply_<participant_ID>_<number_of_interaction>.xlsx". For example, "Reply_SKM9sa_1.xlsx" 
  for interaction 1 of participant "SKM9sa". 
  - See [the structure of the output folder](#data-structure) for more information.
- **Output:** Excel file "model_id_<participant_ID>_<model_configuration_details>.xlsx" in output folder 
experimentNao/out/replies_participants (see [the structure of the output folder](#output-folder)).

### Additional (data processing) scripts 
These are the additional scripts to process the data from/before the interactions and the identification, as described in the workflow above.

##### Post Identification Analysis
- **Main:** experimentNao/data_analysis/post_id_analysis/main_post_id.py

##### Pre Process Data
- **Main:** main_pre_mbc_interaction.py

### Output data - folder structure
The output folder should have the following structure, in experimentNao/out:
```
experimentNao/out 
├── model_id_out
├── participants_rld
├── replies_participants
│   ├── training_sessions
│   ├──"Reply_<participant_ID>_<timestamp>.xlsx"
│   │   ├── to_id
│   │   │   ├──"Reply_<participant_ID>_1.xlsx"
│   │   │   ├──"Reply_<participant_ID>_2.xlsx"
│   ├── mbc_session
│   │   ├── final
│   │   │   ├──"Output_<participant_ID>.xlsx"
│   │   │   ├──"Output_alternative_<participant_ID>.xlsx"
```
