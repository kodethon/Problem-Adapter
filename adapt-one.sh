if [ ! -e "$1" ]; then
    echo "$1 does not exist..."
    exit
fi

file_path=$1
file_name=$(basename -- "$file_path")
prob_name="${file_name%.*}"
output_dir=output/$prob_name

# Create log folder if it doesn't exit
if [ ! -e "log" ]; then
    mkdir log
fi

python3_prints=$(cat "$file_path" | grep -P 'print ?\(.*\)')
if [ -z "$python3_prints" ]; then
    interpreter=python
else
    interpreter=python3
fi

echo "Using $interpreter..."

# parse the python file
$interpreter lib/prepare.py "$file_path" 2>> log/prepare.log

if [ -e "$output_dir" ]; then
    # Generate cases folder
    $interpreter lib/mutate.py "$output_dir" 2>> log/mutate.log

    # Zip up cases folder
    cwd=$(pwd)
    cd "$output_dir"; zip -r cases.zip cases > /dev/null
    cd "$cwd"

    # Copy the description file
    description_path=$(dirname $file_path)/description.txt

    if [ -e "$description_path" ]; then
        cp $description_path $output_dir
    else
        touch $output_dir/description.txt
    fi
fi
