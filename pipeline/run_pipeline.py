import subprocess, logging, sys  #subprocess module lets python run external commands, like running commands in a terminal or other scripts
logging.basicConfig(level=logging.INFO)

subprocess.run([sys.executable, 'clean.py'], check=True) # run 'python clean.py' command in terminal
# subprocess.run(['python', 'cluster.py'], check=True) # if i add kmeans clustering later


# this file orchestrates the pipeline's workflow

# How to run full pipeline:
# cd pipeline
# pipelinevenv\Scripts\activate
# python run_pipeline.py