problem_folder=$1
cd "$problem_folder" && zip -r cases.zip cases > /dev/null; cd ../..
python lib/upload.py "$problem_folder"

