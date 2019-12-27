*how to run the analysis pipelines?*

analyze mutual information of phenotypes regardless of a disease:

1. specify the analysis parameters in "regardless_of_diseases" section in the 
analysisConfig.yaml file. 
2. in the main() function of "analysis_pipeline" module, run the 
pipeline_regardless_of_disease() function (comment out other lines)


analyze mutual information of phenotypes in regarding to a disease:

1. specify which diseases are of interest in the analysisConfig.yaml file, 
also specify other parameters
2. go to the declaration of pipeline_regarding_diseases() in 
"analysis_pipeline" module, manually change and run the code following the 
instructions. 