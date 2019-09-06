cd ../..

cwd=$(pwd)
problem_folder=$1
cd "$problem_folder" && zip -r cases.zip cases > /dev/null; cd "$cwd"
python lib/upload.py "$problem_folder"

