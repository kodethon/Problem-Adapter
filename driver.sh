for category in $1/*; do
    src_folder=$category/python

    # If the folder exists...
    if [ -d "$src_folder" ]; then
        for dir in $src_folder/*; do
            echo "Processing $dir..."

            dirname=$(basename -- "$dir")
            python lib/prepare.py "$dir/$dirname.py"
            python lib/mutate.py "output/$dirname/test-0.json"
        done
    fi
done
