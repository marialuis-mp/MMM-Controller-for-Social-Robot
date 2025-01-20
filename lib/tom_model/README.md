# Theory of Mind model
This repository that allows to declare a theory of mind (ToM) model with the structure provided in [...]. 

** Structure of the repository ** \
```
lib\tom_model\
├── usage_example: contains an example on how to declare and run a simple version of our ToM model. \
├── model_elements: contains the code that defines the classes of elements of the model (variables, processes, and linkages). The processes are functions that receive one or more variables and result in another variables. The linkages define how certain variables influencer other variables. \
├── model_structure: contains the structure of the model, which is divided in three main modules: the 'perception_module.py', 'cognitive_module.py', and 'decision_making_module.py'. Each file defines which variables, processes, and linkages can be included in the corresponding module. \
├── model_declaration_auxiliary: contains some functions that help declare the model. \
├── fis_support_functions: contains some support functions to represent the linkages as fuzzy inference systems (FIS) \
├── config.py: contains some general configuration variables, such as the linkages framework and the step of FIS \
```

## Installation
See [overall ReadMe](README.md#Installation) file in root folder for information about installation.
No further installation steps are required after following this.

## Usage
Either:
- run the usage_example\main_example.py in order to run the already made example. 
- create your own theory of mind model following the folder structure of the folder "usage_example"
  - the function "main_example.py" runs the model for x time steps
  - to declare the variables, follow the structure of declare_variables
  - to declare each module, follow the structure of declare_cognitive_module, declare_decision_making, \
    declare_perception_module
  - the file "declare_entire_model.py" declares all modules defined in the aforementioned files and attached them to the \
    tom model object. Follow its structure as close as possible. 
  - to change the mathematical functions that model the relationship between variables, use the config.py file.