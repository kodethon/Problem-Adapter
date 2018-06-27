file_path=$1
file_name=$(basename -- "$file_path")
prob_name="${file_name%.*}"
python lib/prepare.py "$file_path"

output_dir=output/$prob_name

# Generate cases folder
python lib/mutate.py "$output_dir"

# Zip up cases folder
cwd=$(pwd)
cd "$output_dir"; zip -r cases.zip cases
cd "$cwd"

# Copy the description file
description_path=$(dirname $file_path)/description.txt
if [ -e "$description_path" ]; then
    cp $description_path $output_dir
else
    touch $output_dir/description.txt
fi
