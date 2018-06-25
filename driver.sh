for category in $1/*; do
    src_folder=$category/python

    # If the folder exists...
    if [ -d "$src_folder" ]; then
        echo "$src_folder exists!"
        for file in $src_folder/*; do
            echo "Processing $file..."
            python lib/prepare.py $file
            filename=$(basename -- "$file")
            filename="${filename%.*}"
            python lib/mutate.py "output/$filename/test-0.json"
        done
    fi
done
